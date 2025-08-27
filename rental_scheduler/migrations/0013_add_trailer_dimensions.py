from django.db import migrations, models
from decimal import Decimal


def forwards(apps, schema_editor):
    Trailer = apps.get_model('rental_scheduler', 'Trailer')
    for trailer in Trailer.objects.all():
        size = trailer.size
        width_val = None
        length_val = None
        if size:
            size_clean = size.replace("'", '').replace('"', '').lower().strip()
            if 'x' in size_clean:
                parts = size_clean.split('x')
                if len(parts) == 2:
                    try:
                        width_val = Decimal(parts[0].strip())
                        length_val = Decimal(parts[1].strip())
                    except Exception:
                        pass
        trailer.width = width_val
        trailer.length = length_val
        trailer.save(update_fields=['width', 'length'])


def backwards(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('rental_scheduler', '0012_remove_contract_furniture_blanket_quantity_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='trailer',
            name='width',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, help_text='Width in feet'),
        ),
        migrations.AddField(
            model_name='trailer',
            name='length',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, help_text='Length in feet'),
        ),
        migrations.RunPython(forwards, backwards),
    ] 