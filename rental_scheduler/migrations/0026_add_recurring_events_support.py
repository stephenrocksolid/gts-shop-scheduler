# Generated migration for recurring events support

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rental_scheduler', '0025_remove_deleted_models'),
    ]

    operations = [
        # Update STATUS_CHOICES to include 'pending' and 'canceled'
        migrations.AlterField(
            model_name='job',
            name='status',
            field=models.CharField(
                choices=[
                    ('pending', 'Pending'),
                    ('uncompleted', 'Uncompleted'),
                    ('completed', 'Completed'),
                    ('canceled', 'Canceled'),
                ],
                default='uncompleted',
                help_text='Current status of the job',
                max_length=20
            ),
        ),
        
        # Add recurrence_rule JSON field
        migrations.AddField(
            model_name='job',
            name='recurrence_rule',
            field=models.JSONField(
                blank=True,
                null=True,
                help_text='JSON storing recurrence rule: {type: monthly/yearly, interval: N, count: X, until_date: YYYY-MM-DD}'
            ),
        ),
        
        # Add recurrence_parent FK (self-referential)
        migrations.AddField(
            model_name='job',
            name='recurrence_parent',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.CASCADE,
                related_name='recurrence_instances',
                to='rental_scheduler.job',
                help_text='Parent job if this is a recurring instance'
            ),
        ),
        
        # Add original_start_dt to track which occurrence this is
        migrations.AddField(
            model_name='job',
            name='recurrence_original_start',
            field=models.DateTimeField(
                blank=True,
                null=True,
                help_text='Original start date for this recurrence instance'
            ),
        ),
        
        # Add end_recurrence_date to parent job
        migrations.AddField(
            model_name='job',
            name='end_recurrence_date',
            field=models.DateField(
                blank=True,
                null=True,
                help_text='Date after which no more recurrences should be generated'
            ),
        ),
        
        # Add index for faster queries
        migrations.AddIndex(
            model_name='job',
            index=models.Index(fields=['recurrence_parent', 'recurrence_original_start'], name='job_recur_idx'),
        ),
    ]







