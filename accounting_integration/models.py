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


class ItmItems(models.Model):
    """
    Classic Accounting items (parts/services).

    Primary key in Classic is `itemid`.
    """

    itemid = models.BigAutoField(primary_key=True)

    itemnumber = models.CharField(max_length=60)
    salesdesc = models.CharField(max_length=3000)
    price = models.DecimalField(max_digits=20, decimal_places=8)

    class Meta:
        managed = False
        db_table = "itm_items"

    def __str__(self):
        return f"{self.itemnumber}"

