# Generated migration for call reminder feature

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rental_scheduler', '0026_add_recurring_events_support'),
    ]

    operations = [
        # Add call_reminder_color to Calendar model
        migrations.AddField(
            model_name='calendar',
            name='call_reminder_color',
            field=models.CharField(
                default='#F59E0B',
                help_text='CSS hex color code for call reminder events (e.g., #F59E0B)',
                max_length=7
            ),
        ),
        # Add has_call_reminder to Job model
        migrations.AddField(
            model_name='job',
            name='has_call_reminder',
            field=models.BooleanField(
                default=False,
                help_text='Whether this job has a call reminder'
            ),
        ),
        # Add call_reminder_weeks_prior to Job model
        migrations.AddField(
            model_name='job',
            name='call_reminder_weeks_prior',
            field=models.PositiveIntegerField(
                blank=True,
                choices=[(2, '1 week prior'), (3, '2 weeks prior')],
                help_text='How many weeks before the job to show the call reminder',
                null=True
            ),
        ),
    ]







