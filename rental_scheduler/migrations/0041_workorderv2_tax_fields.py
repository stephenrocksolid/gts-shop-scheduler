from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rental_scheduler", "0040_add_work_order_v2_models"),
    ]

    operations = [
        migrations.AddField(
            model_name="workorderv2",
            name="tax_rate_snapshot",
            field=models.DecimalField(
                max_digits=7,
                decimal_places=4,
                default=Decimal("0.0000"),
            ),
        ),
        migrations.AddField(
            model_name="workorderv2",
            name="tax_amount",
            field=models.DecimalField(
                max_digits=12,
                decimal_places=2,
                default=Decimal("0.00"),
            ),
        ),
    ]
