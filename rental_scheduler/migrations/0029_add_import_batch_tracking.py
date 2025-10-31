# Generated migration to add import batch tracking

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rental_scheduler', '0028_add_call_reminder_completed'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='import_batch_id',
            field=models.CharField(
                blank=True, 
                null=True, 
                max_length=36, 
                db_index=True,
                help_text='UUID for batch import tracking - allows reverting imports'
            ),
        ),
    ]



