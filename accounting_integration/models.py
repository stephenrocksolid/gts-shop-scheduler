"""
Unmanaged models for the Classic Accounting database.

We intentionally keep these models minimal and focused on the tables/columns
needed by the scheduler's Work Order revamp. The backing tables live in an
external database and are accessed via the Django DB alias "accounting".
"""

from django.db import models


class Org(models.Model):
    """
    Classic Accounting customer/org record.

    Primary key in Classic is `org_id` (see upstream accounting_integration).
    """

    org_id = models.BigAutoField(primary_key=True)

    # Required discriminator / uniqueness fields
    orgdiscriminator = models.CharField(max_length=31)
    org_name_extension = models.CharField(max_length=60, default="")

    # Required status fields (Classic has NOT NULL constraints)
    active = models.BooleanField()
    autoactive = models.BooleanField()
    balance = models.DecimalField(max_digits=16, decimal_places=2)
    createdate = models.DateTimeField()
    moddate = models.DateTimeField(blank=True, null=True)

    # Common customer-facing fields (used by WO customer selector/editor)
    orgname = models.CharField(max_length=60, blank=True, null=True)
    phone1 = models.CharField(max_length=45, blank=True, null=True)
    contact1 = models.CharField(max_length=45, blank=True, null=True)
    email = models.CharField(max_length=300, blank=True, null=True)

    # Additional fields used by create/update flows
    fax1 = models.CharField(max_length=45, blank=True, null=True)
    notes = models.CharField(max_length=2000, blank=True, null=True)
    alertnotes = models.CharField(max_length=1000, blank=True, null=True)
    exported = models.BooleanField(blank=True, null=True)
    fiscalmonth = models.IntegerField(blank=True, null=True)
    taxmonth = models.IntegerField(blank=True, null=True)
    logo = models.BinaryField(blank=True, null=True)
    companyname = models.CharField(max_length=60, blank=True, null=True)
    creditlimit = models.DecimalField(max_digits=16, decimal_places=4, blank=True, null=True)
    tax_exempt_expiration_date = models.DateField(blank=True, null=True)
    tax_exempt_number = models.CharField(max_length=60, default="")
    taxable = models.BooleanField(blank=True, null=True)
    eligible1099 = models.BooleanField(blank=True, null=True)
    taxidno = models.CharField(max_length=40, blank=True, null=True)
    lastfcdate = models.DateField(blank=True, null=True)
    is_cash_customer = models.BooleanField()
    is_no_charge_sales = models.BooleanField()

    class Meta:
        managed = False
        db_table = "org"

    def __str__(self):
        return self.orgname or f"Org #{self.org_id}"


class OrgAddress(models.Model):
    """Classic Accounting address record (used for BILLTO)."""

    addresstype = models.CharField(max_length=45)
    gen_addr_id = models.BigAutoField(primary_key=True)
    active = models.BooleanField()
    addrname = models.CharField(max_length=45, blank=True, null=True)
    txtcity = models.CharField(max_length=60, blank=True, null=True)
    txtcountry = models.CharField(max_length=25, blank=True, null=True)
    createdate = models.DateTimeField()
    moddate = models.DateTimeField(blank=True, null=True)
    txtstate = models.CharField(max_length=25, blank=True, null=True)
    streetone = models.CharField(max_length=60, blank=True, null=True)
    streettwo = models.CharField(max_length=60, blank=True, null=True)
    txtzip = models.CharField(max_length=45, blank=True, null=True)
    is_default = models.BooleanField()
    orgid = models.ForeignKey(Org, models.DO_NOTHING, db_column="orgid", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "org_address"


class ItmItemType(models.Model):
    itemtypecode = models.CharField(primary_key=True, max_length=10)
    itemtypename = models.CharField(max_length=60)
    weighable = models.BooleanField()

    class Meta:
        managed = False
        db_table = "itm_item_type"

    def __str__(self):
        return self.itemtypecode


class ItmItems(models.Model):
    """
    Classic Accounting items (parts/services).

    Primary key in Classic is `itemid`.
    """

    itemtypecode = models.ForeignKey(
        ItmItemType, models.DO_NOTHING, db_column="itemtypecode"
    )
    itemid = models.BigAutoField(primary_key=True)
    active = models.BooleanField()

    itemnumber = models.CharField(max_length=60)
    itemname = models.CharField(max_length=100)
    salesdesc = models.CharField(max_length=3000)
    price = models.DecimalField(max_digits=20, decimal_places=8)
    taxable = models.BooleanField()
    salesaccountid = models.ForeignKey(
        "GlAcct", models.DO_NOTHING, db_column="salesaccountid",
        related_name="itmitems_salesaccountid_set", blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "itm_items"

    def __str__(self):
        return f"{self.itemnumber}"


class OrgItemLink(models.Model):
    id = models.BigAutoField(primary_key=True)
    createdate = models.DateTimeField()
    exempt = models.BooleanField()
    linktype = models.CharField(max_length=255)
    moddate = models.DateTimeField(blank=True, null=True)
    itemid = models.ForeignKey(ItmItems, models.DO_NOTHING, db_column="itemid")
    orgid = models.ForeignKey(Org, models.DO_NOTHING, db_column="orgid")

    class Meta:
        managed = False
        db_table = "org_item_link"


class ItmItemLink(models.Model):
    id = models.BigAutoField(primary_key=True)
    createdate = models.DateTimeField()
    description = models.CharField(max_length=500, blank=True, null=True)
    exempt = models.BooleanField()
    linktype = models.CharField(max_length=20)
    moddate = models.DateTimeField(blank=True, null=True)
    ordinal = models.IntegerField(blank=True, null=True)
    qty = models.DecimalField(max_digits=16, decimal_places=4)
    childitemid = models.ForeignKey(
        ItmItems, models.DO_NOTHING, db_column="childitemid"
    )
    itemunitid = models.BigIntegerField(blank=True, null=True)
    parentitemid = models.ForeignKey(
        ItmItems,
        models.DO_NOTHING,
        db_column="parentitemid",
        related_name="itmitemlink_parentitemid_set",
    )

    class Meta:
        managed = False
        db_table = "itm_item_link"


class IncIncomeSettings(models.Model):
    id = models.BigAutoField(primary_key=True)

    class Meta:
        managed = False
        db_table = "inc_income_settings"


class IncIncomeSettingsDefTaxRegions(models.Model):
    inc_settings = models.ForeignKey(
        IncIncomeSettings, models.DO_NOTHING, primary_key=True
    )
    tax_item = models.ForeignKey(ItmItems, models.DO_NOTHING)
    order_seq = models.IntegerField()

    class Meta:
        managed = False
        db_table = "inc_income_settings_def_tax_regions"
        unique_together = (("inc_settings", "order_seq"),)


class ItmItemUnit(models.Model):
    id = models.BigAutoField(primary_key=True)
    upccode = models.CharField(max_length=60, blank=True, null=True)
    active = models.BooleanField()
    createdate = models.DateTimeField()
    defaultpurchasing = models.BooleanField()
    defaultselling = models.BooleanField()
    mainunit = models.BooleanField()
    mathoper = models.CharField(max_length=45)
    moddate = models.DateTimeField(blank=True, null=True)
    quantity = models.DecimalField(max_digits=16, decimal_places=4)
    sellable = models.BooleanField()
    unitname = models.CharField(max_length=45)
    itemid = models.ForeignKey(ItmItems, models.DO_NOTHING, db_column="itemid")

    class Meta:
        managed = False
        db_table = "itm_item_unit"


class GlAcctType(models.Model):
    glaccttypecode = models.CharField(primary_key=True, max_length=10)
    balancefactor = models.IntegerField()
    glaccttypename = models.CharField(max_length=60, blank=True, null=True)
    gl_number_end = models.IntegerField()
    gl_number_start = models.IntegerField()
    orderseq = models.IntegerField()

    class Meta:
        managed = False
        db_table = "gl_acct_type"


class GlAcct(models.Model):
    gl_acct_id = models.BigAutoField(primary_key=True)
    accountname = models.CharField(max_length=45)
    accountnumber = models.CharField(max_length=45, blank=True, null=True)
    active = models.BooleanField()
    balance = models.DecimalField(max_digits=16, decimal_places=2)
    checks_on_hand = models.SmallIntegerField(blank=True, null=True)
    checks_ordered = models.BooleanField()
    createdate = models.DateTimeField()
    description = models.CharField(max_length=100, blank=True, null=True)
    endingbalance = models.DecimalField(max_digits=16, decimal_places=2, blank=True, null=True)
    glnumber = models.IntegerField(unique=True)
    lastchknumber = models.CharField(max_length=45, blank=True, null=True)
    lastreconciledate = models.DateField(blank=True, null=True)
    moddate = models.DateTimeField(blank=True, null=True)
    permanent = models.BooleanField()
    retained_earnings_acct = models.BooleanField(blank=True, null=True)
    is_short_term = models.BooleanField()
    glaccttype = models.ForeignKey(GlAcctType, models.DO_NOTHING, db_column="glaccttype")
    parentglaccountid = models.ForeignKey("self", models.DO_NOTHING, db_column="parentglaccountid", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "gl_acct"

    def __str__(self):
        return f"{self.glnumber} - {self.accountname}"


class AcctTerms(models.Model):
    terms_id = models.BigAutoField(primary_key=True)
    active = models.BooleanField()
    createdate = models.DateTimeField()
    discount_day_of_month = models.IntegerField(blank=True, null=True)
    discountdays = models.IntegerField()
    discountpercentage = models.DecimalField(max_digits=16, decimal_places=4)
    due_day_of_month = models.IntegerField(blank=True, null=True)
    fixed_discount_date = models.DateField(blank=True, null=True)
    fixed_due_date = models.DateField(blank=True, null=True)
    moddate = models.DateTimeField(blank=True, null=True)
    netduedays = models.IntegerField()
    termsname = models.CharField(unique=True, max_length=45)
    terms_mode = models.CharField(max_length=16)

    class Meta:
        managed = False
        db_table = "acct_terms"


class AcctTransType(models.Model):
    accttranstypecode = models.CharField(primary_key=True, max_length=10)
    is_expense = models.BooleanField()
    is_income = models.BooleanField()
    java_class = models.CharField(max_length=255)
    lastsequence = models.CharField(max_length=45, blank=True, null=True)
    multiplier = models.IntegerField()
    is_pl_eligible = models.BooleanField()
    accttranstypename = models.CharField(max_length=60)
    transferable = models.BooleanField()

    class Meta:
        managed = False
        db_table = "acct_trans_type"


class AcctTransStatus(models.Model):
    statuscode = models.CharField(primary_key=True, max_length=20)
    statusname = models.CharField(max_length=45, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "acct_trans_status"


class AcctTrans(models.Model):
    transtypecode = models.ForeignKey(AcctTransType, models.DO_NOTHING, db_column="transtypecode")
    transid = models.BigAutoField(primary_key=True)
    createdate = models.DateTimeField()
    exported = models.BooleanField(blank=True, null=True)
    fromdate = models.DateField(blank=True, null=True)
    memo = models.CharField(max_length=1000, blank=True, null=True)
    moddate = models.DateTimeField(blank=True, null=True)
    notes = models.CharField(max_length=5000, blank=True, null=True)
    printed = models.BooleanField()
    referencenumber = models.CharField(max_length=45, blank=True, null=True)
    todate = models.DateField(blank=True, null=True)
    transtotal = models.DecimalField(max_digits=16, decimal_places=2)
    transdate = models.DateField()
    rec_version = models.BigIntegerField(blank=True, null=True)
    billtotx = models.CharField(max_length=400, blank=True, null=True)
    paytotx = models.CharField(max_length=60, blank=True, null=True)
    transtotalwordtx = models.CharField(max_length=200, blank=True, null=True)
    expecteddate = models.DateField(blank=True, null=True)
    fixed_discount_date = models.DateField(blank=True, null=True)
    fixed_due_date = models.DateField(blank=True, null=True)
    fobtx = models.CharField(max_length=45, blank=True, null=True)
    paydate = models.DateField(blank=True, null=True)
    pmtreference = models.CharField(max_length=30, blank=True, null=True)
    shiptotx = models.CharField(max_length=400, blank=True, null=True)
    sourcerefnumber = models.CharField(max_length=120, blank=True, null=True)
    taxes_migrated = models.BooleanField(blank=True, null=True)
    tendered_amount = models.DecimalField(max_digits=16, decimal_places=2, blank=True, null=True)
    undep_funds_total = models.DecimalField(max_digits=16, decimal_places=2, blank=True, null=True)
    repeat_frequency = models.CharField(max_length=50, blank=True, null=True)
    is_jrn_deposit_eligible = models.BooleanField()
    orgid = models.ForeignKey(Org, models.DO_NOTHING, db_column="orgid", blank=True, null=True)
    parent_trans = models.ForeignKey("self", models.DO_NOTHING, blank=True, null=True)
    transstatus = models.ForeignKey(AcctTransStatus, models.DO_NOTHING, db_column="transstatus")
    glaccountidfrom = models.ForeignKey(GlAcct, models.DO_NOTHING, db_column="glaccountidfrom", blank=True, null=True)
    glaccountidto = models.ForeignKey(GlAcct, models.DO_NOTHING, db_column="glaccountidto", related_name="accttrans_glaccountidto_set", blank=True, null=True)
    termsid = models.ForeignKey(AcctTerms, models.DO_NOTHING, db_column="termsid", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "acct_trans"

    def __str__(self):
        org_name = self.orgid.orgname if self.orgid else "N/A"
        return f"Trans #{self.transid} - {self.transtypecode.accttranstypecode} - {org_name} - ${self.transtotal}"


class AcctEntry(models.Model):
    entrytypecode = models.CharField(max_length=31)
    entryid = models.BigAutoField(primary_key=True)
    active = models.BooleanField()
    billable = models.BooleanField()
    billed = models.BooleanField()
    cleared = models.BooleanField()
    createdate = models.DateTimeField()
    discount_applied = models.DecimalField(max_digits=12, decimal_places=2)
    entrytotal = models.DecimalField(max_digits=16, decimal_places=2)
    moddate = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    orderseq = models.IntegerField(blank=True, null=True)
    entryqty = models.DecimalField(max_digits=16, decimal_places=4)
    rec_version = models.BigIntegerField(blank=True, null=True)
    entrydate = models.DateField(blank=True, null=True)
    memotx = models.TextField(blank=True, null=True)
    entryamnt = models.DecimalField(max_digits=20, decimal_places=8)
    applic_taxes_migrated = models.BooleanField(blank=True, null=True)
    asset_value_verified = models.BooleanField()
    item_number = models.CharField(max_length=500, blank=True, null=True)
    main_unit_qty = models.DecimalField(max_digits=24, decimal_places=12)
    measure_qty = models.DecimalField(max_digits=16, decimal_places=6)
    total_asset_value = models.DecimalField(max_digits=32, decimal_places=20)
    weight = models.DecimalField(max_digits=16, decimal_places=4, blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    start_time = models.DateTimeField(blank=True, null=True)
    glacctid = models.ForeignKey(GlAcct, models.DO_NOTHING, db_column="glacctid", blank=True, null=True)
    transid = models.ForeignKey(AcctTrans, models.DO_NOTHING, db_column="transid")
    itemid = models.ForeignKey(ItmItems, models.DO_NOTHING, db_column="itemid", blank=True, null=True)
    itemunitid = models.ForeignKey(ItmItemUnit, models.DO_NOTHING, db_column="itemunitid", blank=True, null=True)
    order_link_entryid = models.ForeignKey("self", models.DO_NOTHING, db_column="order_link_entryid", blank=True, null=True)
    parententryid = models.ForeignKey("self", models.DO_NOTHING, db_column="parententryid", related_name="acctentry_parententryid_set", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "acct_entry"


class AcctTransTaxRegions(models.Model):
    trans = models.ForeignKey(AcctTrans, models.DO_NOTHING, primary_key=True)
    tax_item = models.ForeignKey(ItmItems, models.DO_NOTHING)
    order_seq = models.IntegerField()

    class Meta:
        managed = False
        db_table = "acct_trans_tax_regions"
        unique_together = (("trans", "order_seq"),)


class AcctEntryApplicTaxes(models.Model):
    entry = models.ForeignKey(AcctEntry, models.DO_NOTHING, primary_key=True)
    tax_item = models.ForeignKey(ItmItems, models.DO_NOTHING)
    order_seq = models.IntegerField()

    class Meta:
        managed = False
        db_table = "acct_entry_applic_taxes"
        unique_together = (("entry", "order_seq"),)

