# Manual migration to add CallReminder model

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rental_scheduler', '0029_add_import_batch_tracking'),
    ]

    operations = [
        migrations.CreateModel(
            name='CallReminder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reminder_date', models.DateField(help_text='The Sunday this reminder appears on')),
                ('notes', models.TextField(blank=True, help_text='Notes about this call reminder')),
                ('completed', models.BooleanField(default=False, help_text='Whether this reminder has been completed')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('calendar', models.ForeignKey(help_text='Calendar this reminder belongs to', on_delete=django.db.models.deletion.CASCADE, to='rental_scheduler.calendar')),
                ('job', models.ForeignKey(blank=True, help_text='Optional link to a job (null for standalone reminders)', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='call_reminders', to='rental_scheduler.job')),
            ],
            options={
                'verbose_name': 'Call Reminder',
                'verbose_name_plural': 'Call Reminders',
                'ordering': ['reminder_date', '-created_at'],
            },
        ),
    ]














