# Generated migration for call reminder completed field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rental_scheduler', '0027_add_call_reminder_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='call_reminder_completed',
            field=models.BooleanField(
                default=False,
                help_text='Whether the call reminder has been completed'
            ),
        ),
    ]







