# Classic Accounting Developers Guide

## ID Generation Strategy

### Long ID - All Versions Through 2020 (Year 2021)

CA uses the Hibernate TABLE id generation strategy. IDs are assigned as a "block" per session, for each table to be inserted in.

- The keys are in the table `"public"."hibernate_sequences"`
  - `sequence_name` is the name of the table
  - `sequence_next_hi_value` is the next "block number" of IDs that is available.
- The application is required to cache the id's being used for the duration of a session (application open to close).

For example, if your application needs to insert entries in the `itm_items` (Items) table:

1. The first use of this ID within the application's session get the next block and update table:
   1. Get the next block: `id_block = "SELECT sequence_next_hi_value FROM hibernate_sequences WHERE sequence_name = ?table_name?;"`
   2. Increment the next block value: `UPDATE hibernate_sequences SET sequence_next_hi_value = (sequence_next_hi_value + 1) WHERE table_name = ?table_name?`
   3. Get and store the actual ID to use: `next_id = (id_block * 32768)`
2. Now each time you need an ID for this table within the application's session get it:
   1. `id = next_id`
   2. `next_id = next_id + 1`
3. Use the resulting id: `INSERT INTO itm_items(itemid, itemnumber, …) VALUES (id, 'test item', …);`

Of course this is pretty simplified – you will need to track different ids for each table.

Classic Accounting gets a new "block" of IDs each time CA is launched. The author has created a program that uses a separate table with a date stamp so it only gets a new block once a day. However, your application should get and increment the `sequence_next_hi_value` only if that ID is actually needed.

### Long ID – Version 2022 and Later

Hibernate documentation states that TABLE id generation should not be used for production. As of this writing work is progressing to switch to using Sequences for generating the ID numbers. Will be using Sequences in first 2022 version. (There are no CA releases labeled as 2021.)

Implementing Sequence in your application is quite simple. You do not specify the ID field in your INSERT statement and the database automatically inserts the next sequence number for you.

However, if you wish to insert parent > child entries then you have a problem. You first insert the parent (`acct_trans`, for instance), but then in order to insert the child entries (`acct_entry`, etc) you need to know the ID of the parent that was inserted. There are several ways this can be obtained, here are 3 options listed from best to worst.

Also note that in many situations the application does not need to know what the assigned ID of the child entries are, often you can just call INSERT without supplying an ID, let the database assign the value, and don't really need to know what the assigned value is.

1. Turn your INSERT statement into a query by using a RETURNING clause. If you end a normal SQL INSERT statement with `RETURNING <column>` you can run it as a Query (`executeQuery` rather than `executeUpdate`) and obtain a ResultSet that contains the ID of the record that was inserted. You can specify multiple columns in the RETURNING clause same as in the SELECT clause, which might be desirable if you are inserting multiple entities and you need to know which record was assigned which ID.
   - Example: `INSERT INTO acct_trans (col1, col2...) VALUES (val1, val2...) RETURNING transid;`
   - Note that you may not specify `transid` in the insert column list.
2. Before doing the INSERT fetch the next sequence value from the appropriate sequence, then supply that value in your INSERT.
   - All sequences are (supposed to be) named in the following syntax: `<table_name>_<id_column_name>_seq`. So the sequence for `acct_trans` (`transid`) is: `acct_trans_transid_seq`.
   - To fetch the next value use the query: `SELECT nextval('acct_trans_transid_seq'::regclass);`
   - Note that the syntax and casting is a bit different for this.
   - Now use the fetched id when inserting your record. If you want to insert multiple records you need to fetch X # of times. See Note Below.
3. Do your INSERT without supply the ID column or value, then select the max id from that table.
   - `SELECT max(transid) FROM acct_trans;`
   - This method has potential to return the wrong value in a multi-user environment, where another user could insert a record between your insert and max select.

#### Note on Sequence Increment

When you fetch the `nextval` of a sequence it returns a number that is the sequence's INCREMENT value more than the previous `nextval` fetch. As of the initial 2022 release we expect to have the INCREMENT value on all Sequences set to 1. It is possible that some tables, at least, will have this number increased in the future, maybe somewhere in the 20-100 range.

The reason for doing so would be to reduce that number of queries the application makes to the database. In Classic Accounting most database INSERTS are done via Hibernate, which the author believes uses method #2 above when inserting records. Some tables normally do multiple inserts at once, like in `acct_entry`. So if a Sequence's INCREMENT value is set to 50 then the application can insert 50 records for each `SELECT nextval` query it does, rather than selecting `nextval` 50 times.

#### Multiple nextval Fetching

If you choose to use option #2 above it is possible to fetch X number of `nextval` values in one query by using a RECURSIVE query. You can use the following query and change the highlighted text to specify the # of records to fetch (set to 8 here) and the name of the sequence to fetch from.

Note that the `ct` column can be eliminated and the code can be compacted (remove line breaks, etc), I tried to make it readable.

```sql
WITH RECURSIVE qry AS 
(
	SELECT 1 AS ct
	UNION ALL
	SELECT ct+1 AS ct
	FROM qry
	WHERE ct < 8 
)
SELECT nextval('acct_trans_transid_seq'::regclass), ct
FROM qry
```

### String IDs

Several tables use a UUID String as an ID. For instance, table `"public"."acct_sales_rep"`.

If your programming language does not have a random UUID generation function you can fake a UUID string using the following SQL command:

```sql
SELECT substring(tx, 1, 8) || '-' || substring(tx, 9, 4) || '-' || substring(tx, 13, 4) 
	|| '-' || substring(tx, 17, 4) || '-' || substring(tx, 21) AS uuid
FROM (SELECT md5(CAST(clock_timestamp() AS varchar)) AS tx) AS q;
```

The results should be a 36 digit string, something similar to: `"a01021ff-103e-dd06-039b-dd53aefeb36a"`. The odds of ever getting the same string twice are extremely small.

**Revised Nov 29, 2021:** The above function was revised to use `clock_timestamp()` instead of `current_timestamp`. Note that the parentheses `()` after `clock_timestamp` are required.

The `clock_timestamp()` function is PostgreSQL specific, at least it did not work on a H2 database when the author tested. The difference is that `current_timestamp` queries the actual time only once per transaction, where `clock_timestamp()` queries each time it is invoked.

The following query is a visible example, it uses the above function using in a WITH query that generates numbers from 1 to 100, along with the md5 hash of `clock_timestamp()`. If you replace `clock_timestamp()` with `current_timestamp` it returns the same uuid value 100 times, but `clock_timestamp()` returns 100 different values.

```sql
WITH RECURSIVE numbers AS (
SELECT 1 AS i, md5(CAST(clock_timestamp() AS varchar)) AS tx
UNION ALL
SELECT i +1 AS i, md5(CAST(clock_timestamp() AS varchar)) AS tx
FROM numbers
WHERE i < 100)
SELECT i, substring(tx, 1, 8) || '-' || substring(tx, 9, 4) || '-' || substring(tx, 13, 4) 
	|| '-' || substring(tx, 17, 4) || '-' || substring(tx, 21) AS uuid
FROM numbers
```

## Inserting Items

Quite complicated.

- The main Item info is stored in `itm_items`
- The Item's Units are stored in `itm_item_unit`
  - Each item must have at least one Unit, and must have one Unit which is set TRUE to each of the following:
    - `defaultselling`
    - `defaultpurchasing`
    - `sellable`
    - `active`
- The Item's Base Price is stored in the `price` field. However, if CA has active Price Levels (`itm_price_levels`) then we need to create selling price entries in `itm_item_price_levels`.
  - There is one entry in `itm_item_price_levels` for each Price Level, for each Item.
- The Item's Taxes, Components and Extras data is all stored in `itm_item_link`

## Org: Customers and Vendors

All Customers, Vendors, Employees and the Company Information are stored in the `org` table.

- Valid `"org"."orgdiscriminator"` values are: `'COMP'`, `'CUST'`, `'VEND'` and `'EMP'`
  - There **MUST BE** one, and **ONLY ONE** entry for `COMP`!

There are a good number of foreign keys connected to this table, for Terms, Price Levels, Org Type, etc.

The address information for each org is stored in `org_address`

- There are 2 types of addresses (`addresstype`) – see table `org_address_type`:
- Each Org **MUST** have one, and may have **ONLY ONE** `'BILLTO'` address
- Currently only Customers are made to handle `SHIPTO` addresses. Each Customer may have 0 or more `'SHIPTO'` entries.
  - For each Customer, only one `SHIPTO` address may have the `is_default` flag set to `TRUE`.

- For Customers you must create Sales Tax entries in `org_item_link` table.
  - Contains a `'TAX'` entry for the CUST * each active SALESTAX Item (in `itm_items`).
  - The important thing here is whether `exempt` is true (non-taxable) or false (taxable).
  - Beware that many CA users have multiple Sales Tax items.

## Inserting Documents

There are 2 main tables containing the document information:

- Document Header = `acct_trans`
- Line Items = `acct_entry`

There are a lot of foreign keys in these tables.

1. First you need to insert the document header.
   1. There is information on the different document types in `acct_trans_type` table.
      1. If `acct_trans_type.multiplier` is -1 then the `acct_trans.transtotal` is negative, otherwise it is positive. (There are a few exceptions, `INVENADJ` can be either negative or positive, depending on the document total.)
      2. The `acct_trans.referencenumber` (doc #) needs to be obtained from the `acct_trans_type.lastsequence` **NOTE:** the number in this table needs to be updated each use!
   2. You need to set a valid `orgid`, which represents the Customer (income docs) or Vendor (expense docs).
   3. For Income docs you must set a Tax Region by adding an entry to `acct_trans_tax_regions`.
      1. This should match the non-exempt TAX entries from `org_item_link` for the document's customer.
2. Then insert the Line Items (`ITEMENTRY`)
   1. The `acct_entry.transid` needs to be `acct_trans.transid` of the `acct_trans` entry that was inserted.
   2. You cannot create `ITEMENTRY` without setting a valid `itemid` from `itm_items` table (CA will not recognize the line item if you do).
      1. You must also set a valid `itemunitid` (references `itm_item_unit.id`)
   3. The `entrytotal` must equal `(entryqty * entryamnt * measure_qty)`
      1. None of these qty / price fields may be null
      2. `measure_qty` must be 1.0, not 0.0
   4. The lines are sorted according to the `orderseq` entry. First row is 0, next row is 1, etc.
   5. The line's Description field is named `memotx` – not very obvious.
   6. If this is an Income document then you must generate entries in `acct_entry_applic_taxes` for each `ITEMENTRY` that is taxable.
3. If the `acct_trans_type` of the document you are inserting `is_pl_eligible` then you also need to create `GLENTRY` for this document. *Special Notes on ITEMREC and MNFT docs in Asset Value section*
   1. This becomes more complicated, but remember that the query:
      ```sql
      SELECT sum(entrytotal) FROM acct_entry WHERE entrytypecode = 'GLENTRY' AND transid = ?
      ```
      **MUST RETURN 0.00!**
   2. There is one `GLENTRY` for the document total.
      1. The `glacctid` for an Invoice would be "Accounts Receivable"
         > Stupid, but A/R GL is hard-coded in CA, `gl_acct_id = 1001`
      2. The `glacctid` for a Vendor Bill would be "Accounts Payable"
         > Stupid, but A/P GL is hard-coded in CA, `gl_acct_id = 1000`
   3. If the item is NOT an Inventory Item then here is one `GLENTRY` for each `ITEMENTRY`, using the Item's Sales GL (on Sales Docs) or Purchase GL (on Purchase Docs) for the `glacctid`.
      1. The `GLENTRY` for Sales Tax will go to GL #2200, Sales Tax Payable.
   4. For each Inventory Item `ITEMENTRY` there are 2 or 3 `GLENTRY` entries: (Sales or Purchase GL), Assets and/or Cost of Goods Sold.
      - See Asset Value info below for more information on `GLENTRY` postings
      - You need to set the `orderseq` value of `GLENTRY` records to match the corresponding `ITEMENTRY`. This is to enable better reports to be generated.
      - The `orderseq` of the document's `GLENTRY` (A/R, A/P) should be -1.
      - In version 2025 some changes were made to Vendor Bill postings, and the term Variance was relabeled to COGS within CA, although the database fields are still named variance.

- If your application is automating document conversion in CA (converting SO to Invoice, etc) then it must generate entries in `acct_trans_relations` for the links
- The `acct_trans_relations` table also contains the information (basically "document lines") for document types:
  - Receive Payment
  - Bill Pay Check
  - Deposit

- `acct_entry_link` is a dead table – is not used.

## Asset Value for Inventory Items

This section added for release 2023.1.x, revised functionality. Was further revised for 2025.x.

When you insert `ITEMENTRY` records with Inventory or Asset items in a posting document* then your application will need to honor CA's method of calculating the Asset / COGS Value to use.

\* posting documents are those where `acct_trans_type.is_pl_eligible = true`. This update also affects document types Item Receipt (`ITEMREC`) and Manufacture (`MNFT`), see notes below.

Some key elements of using Inventory Items:

- Your application will need to set values for `main_unit_qty` and `total_asset_value`, plus set the `asset_value_verified` field to `TRUE`, on the `ITEMENTRY` record. There are database functions for calculating the value of these fields, as explained below.
- Use the amount of `total_asset_value` for `entrytotal` on Asset and COGS `GLENTRY` records.
- Insert the correct `GLENTRY` records – more details below
- Set correct value to `acct_trans.transtotal` for the document's total value.

Storing these values is to allow CA to accurately track current Asset Value and Average Cost of each item.

There is a `calculate_asset_value` database function to calculate the values for `main_unit_qty` and `total_asset_value`. Since there are now (as of v2025) several different versions of the `calculate_asset_value` function in existence a special developer version was created that checks version and calls the correct function. It will even work on older versions databases. This function, `thirdparty_calculate_asset_value` is supplied below, but your application must add it to the database.

When calling this function you need to supply the following IN parameters:

- `transcode` (INVOICE, VENDINV, etc – must be a valid value from `acct_trans.accttranstypecode`)
- `entry_id` (the value `acct_entry.entryid` of the record you are modifying - null if new entry)
- `unit_id` (the value of `acct_entry.itemunitid` of the record you're inserting or modifying – not null)
- `qty` (the total qty, must be total of `acct_entry.entryqty * acct_entry.measure_qty`)
- `rate` (the value of `acct_entry.entryamnt`)
- `has_parent_entry` (`acct_entry.parententryid IS NOT NULL` - utilized only on MNFT docs)

The function utilizes OUT parameters to return multiple values from a single function call. Calling the `thirdparty_calculate_asset_value` function with the correct parameters will return a record with 3 values, here is a sample with values for the parameters (adjust ids for your database):

```sql
SELECT * FROM thirdparty_calculate_asset_value('INVOICE', null, 2818049, 1.0, 7.425, false);
```

Result:
```
  mainunitqty   |    totalassetvalue     | assetfactor 
----------------+------------------------+--------
 1.000000000000 | 4.85000000000000000000 |     -1
```

The value of `assetfactor` indicates whether this entry is adding or removing inventory. Use the values returned by this function for your `acct_entry` INSERT and UPDATE statements as follows:

- `ITEMENTRY`: `main_unit_qty = mainunitqty`, `total_asset_value = totalassetvalue`
- `GLENTRY` (Asset): `entryamnt = totalassetvalue`, `entryqty = factor`
- `GLENTRY` (COGS): `entryamnt = totalassetvalue`, `entryqty = -factor` (negated)

> **WARNING:** The information in above chart changed for `thirdparty_` function!

### Special Notes

- **Asset Items**
  - Asset Items have only an Asset `GLENTRY`, no Variance, Cost Of Goods or Income entries.
- **Manufacture**
  - The `has_parent_entry` parameter; for the item being manufactured this value is false, and for the components being used it is true.
  - There is no COGS entry for MNFT docs, the sum of all the Asset `GLENTRY` should be 0.00 as it is just moving assets between accounts, not creating an expense (not necessarily true if you have service or non-inventory components).
    - Expect changes in how Manufacture doc entries are made in future version.
- **Item Receipt**
  - Prior to version 2025.x Item Receipts did not have any `GLENTRY`, but that has changed. A new system Asset GL named Unverified Assets was added.
  - If the query `SELECT max(db_version) >= 20250017 FROM db_version;` returns true then you need to insert a `GLENTRY` for the items Asset GL (qty = 1), plus an offset entry (or a doc total entry) to the Unverified Assets GL. This GL Account is hard-coded in CA with ID 1047.
- **Inventory Adjustment**
  - There is no Variance entry for `INVENADJ` docs, the sum of all Asset transactions is balanced against the document's Adjustment Account (GL 4050 in this screenshot).
  - The total of Inventory Adjustment document can be either positive or negative.
- **Vendor Bill / Vendor Credit**
  - Historically CA has created the following `GLENTRY` for each `ITEMENTRY`:
    - Asset GL (+1 entryqty for Bill, -1 for Credit)
    - Purchase GL (+1 entryqty for Bill, -1 for Credit)
    - COGS (Variance) GL (-1 entryqty for Bill, +1 for Credit)
  - If the query `SELECT max(db_version) >= 20250017 FROM db_version;` returns true then you should eliminate the Purchase and COGS entries. In fact, it would be fine to just eliminate these entries regardless.

### Database Function for Calculating Asset Value

Check if database supports `total_asset_value` and `main_unit_qty` fields:

```sql
SELECT count(*) = 2
FROM information_schema.columns
WHERE table_name = 'acct_entry' AND column_name IN ('total_asset_value', 'main_unit_qty');
```

If this returns false then database predates addition of `total_asset_value` and `main_unit_qty` fields.

Database function for calculating asset value and qty:

```sql
CREATE OR REPLACE FUNCTION thirdparty_calculate_asset_value(
    IN transCode VARCHAR, IN entry_id BIGINT, IN unit_id BIGINT, IN qty NUMERIC, IN rate NUMERIC,
    IN has_parent_entry BOOLEAN,
    OUT muQty NUMERIC, OUT totalVal NUMERIC, OUT assetFactor INTEGER
) RETURNS record AS
$$
DECLARE
    iid BIGINT;
    iType VARCHAR;
    currAvgCost NUMERIC;
    fac INTEGER;
    is_absolute BOOLEAN;
    muq NUMERIC := 0.0;
    tav NUMERIC := 0.0;
BEGIN

    SELECT itemid, itemtypecode, COALESCE(averagecost, 0.00)
    INTO iid, iType, currAvgCost
    FROM itm_items
    WHERE itemid = (
        SELECT itemid
        FROM itm_item_unit
        WHERE id = unit_id);

    assetFactor := (
            SELECT CASE
                       WHEN (iType IN ('ASSETITM', 'INVEN')) THEN
                           (
                               SELECT CASE
                                          WHEN accttranstypecode = 'MNFT' THEN
                                              CASE WHEN has_parent_entry THEN -1 ELSE 1 END
                                          WHEN accttranstypecode = 'ITEMREC' THEN 1
                                          WHEN NOT is_pl_eligible OR accttranstypecode LIKE '%CHECK' THEN 0
                                          WHEN is_income THEN -1 * multiplier
                                          WHEN is_expense THEN 1 * multiplier
                                          ELSE multiplier END AS factor
                               FROM acct_trans_type
                               WHERE accttranstypecode = transCode
                               ORDER BY factor, accttranstypecode)
                       ELSE
                           0
                END);

    CASE (
        SELECT count(*)
        FROM information_schema.parameters
        WHERE specific_name LIKE 'calculate_asset_value%' AND parameter_mode = 'OUT')

        WHEN 0 THEN -- version n/a, before calculate_asset_value function

        is_absolute := NOT
            (
                SELECT iType = 'INVEN'
                    AND (transCode IN ('INVOICE', 'CUSTCRED', 'SALESREC')
                        OR transCode = 'MNFT' AND has_parent_entry));

        fac := assetFactor;

        muq := (
            SELECT gettotalqty(unit_id, qty) * fac);
        IF is_absolute THEN
            tav := (qty * rate);
        ELSE
            tav := (muq * currAvgCost);
        END IF;

        WHEN 3 THEN -- first version, 3 out parameters, v2023.2 > 2025.0.09
        SELECT mainUnitQty, totalAssetValue, factor
        INTO muq, tav, fac
        FROM calculate_asset_value(transCode, entry_id, unit_id, qty, rate, has_parent_entry);

        muq := muq * fac;
        tav := tav * fac;

        WHEN 4 THEN -- temp version used in test releases, v2025.0.10 -> 2025.0.16
        SELECT mainUnitQty, totalAssetValue
        INTO muq, tav
        FROM calculate_asset_value(transCode, entry_id, unit_id, qty, rate, has_parent_entry);

        WHEN 5 THEN -- temp version 2, maybe used in test release?
        SELECT mainUnitQty, totalAssetValue, factor
        INTO muq, tav, fac
        FROM calculate_asset_value(transCode, entry_id, unit_id, qty, rate, has_parent_entry);

        muq := muq * fac;
        tav := tav * fac;

        WHEN 2 THEN -- 'current' version, v 2025.0.17+
        SELECT mainUnitQty, totalAssetValue
        INTO muq, tav
        FROM calculate_asset_value(transCode, entry_id, unit_id, qty, rate, has_parent_entry);

        ELSE -- 'invalid'
        RAISE EXCEPTION 'Invalid return value for OUT parameter count of calculate_asset_value function';
        END CASE;

    muQty := muq;
    totalVal := tav;

END;
$$ LANGUAGE plpgsql;
```

## Entries for Sales Tax

The way CA auto-calculates Sales Tax is each `ITEMENTRY` in the `acct_entry` table (Income docs only) is "taxable" for each SALESTAX item that is taxable (not exempt) for BOTH the Item AND the Customer. These ID's need to be stored in `acct_entry_applic_taxes` table, one entry for each Sales Tax * Item Entry.

The `acct_entry_applic_taxes.order_seq` is a value 0-x, is not critical except each entry per `ITEMENTRY` needs to be incremental (not same), probably just sort by `tax_item_id`.

We also need to insert an entry in `acct_trans_tax_regions` for the document's "Tax Regions".

### Taxable Status of Items

The taxable status of Items is stored in `itm_item_link` table.

This query will get you a list of all the Tax Items (ids) that should be applied to a given Item. Note that we need to eliminate in-active tax items from this list:

```sql
SELECT l.childitemid
FROM itm_item_link AS l
LEFT JOIN itm_items AS i ON i.itemid = l.childitemid
WHERE l.parentitemid = ?
AND l.linktype = 'TAX'
AND i.active = TRUE
AND l.exempt = FALSE;
```

Note that the `itm_item_link.ordinal` field is for sorting purposes and is not important to you - it is used for sorting when getting the Component and Extras lists, which are stored in the same table (note the `linktype = 'TAX'` filter in query below).

### Taxable Status of Customers

The taxable status of Customers is stored in `org_item_link` table.

This query will get you all of the tax items that should be applied to a given customer. Again, we need to eliminate inactive Sales Tax items:

```sql
SELECT l.itemid
FROM org_item_link AS l
LEFT JOIN itm_items AS i ON i.itemid = l.itemid
WHERE l.orgid = ?
AND l.linktype = 'TAX'
AND i.active = TRUE
AND l.exempt = FALSE;
```

If the above query returns results then that item id(s) should be used to insert the `acct_trans_tax_regions` record(s), otherwise use this:

```sql
SELECT tax_item_id FROM inc_income_settings_def_tax_regions;
```

Your application will need to insert the `ITEMENTRY` for the Sales Tax items as well, and these do not have any entries in `acct_entry_applic_taxes`.

If you are inserting Discount line items then there's quite a bit of additional complication. The discount lines do not have any `acct_entry_applic_taxes` entries. Instead, the lines that are being discounted have the total amount of discount saved in `acct_entry.discount_applied`, and that line's sales tax is calculated on the line total less the discount applied. Don't tell me it's ugly, I know that. But to get accurate sales tax calculations it was necessary.

### Insert Query for Sales Tax Entries

Here is a combination insert query, something in the line of what I'd likely do, that gets the necessary records for `acct_entry_applic_taxes`. Need to supply the correct entry, item and org ids:

```sql
INSERT INTO acct_entry_applic_taxes (entry_id, tax_item_id, order_seq)
(SELECT ?entryid? AS entry_id, l.itemid AS tax_item_id, (ROW_NUMBER() OVER (ORDER BY l.itemid ASC))-1 AS order_seq
FROM org_item_link AS l
LEFT JOIN itm_items AS i ON i.itemid = l.itemid
WHERE l.orgid = ?orgid?
AND l.linktype = 'TAX'
AND i.active = TRUE
AND l.exempt = FALSE
AND l.itemid IN (
    SELECT l.childitemid
    FROM itm_item_link AS l
    LEFT JOIN itm_items AS i ON i.itemid = l.childitemid
    WHERE l.parentitemid = ?itemid?
    AND l.linktype = 'TAX'
    AND i.active = TRUE
    AND l.exempt = FALSE
));
```

You will additionally need to insert the `acct_trans_tax_regions` record(s). Here is a query that does this, after the `acct_entry_applic_taxes` are inserted:

```sql
WITH entries AS (
	SELECT tax_item_id, order_seq
	FROM acct_entry_applic_taxes AS t 
	WHERE t.entry_id = ?entryid? ORDER BY order_seq
), deftax AS (
	SELECT tax_item_id, order_seq FROM inc_income_settings_def_tax_regions
)
INSERT INTO acct_trans_tax_regions (tax_item_id, order_seq, trans_id)
SELECT *, (SELECT transid FROM acct_entry WHERE entryid = ?entryid?)
FROM 
	(SELECT *
	FROM entries 
	UNION ALL
	SELECT * FROM deftax WHERE NOT EXISTS (SELECT * FROM entries)) AS qry;
```