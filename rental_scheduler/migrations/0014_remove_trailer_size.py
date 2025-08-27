from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rental_scheduler', '0013_add_trailer_dimensions'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='trailer',
            name='size',
        ),
    ] 