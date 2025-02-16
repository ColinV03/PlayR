# Generated by Django 5.1.6 on 2025-02-12 16:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_alter_game_group_alter_group_organizer_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='event',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.groupscheduleevent'),
        ),
        migrations.AlterField(
            model_name='teamassignment',
            name='team_name',
            field=models.CharField(choices=[('Team A', 'Team A'), ('Team B', 'Team B')], max_length=10),
        ),
        migrations.DeleteModel(
            name='ScheduledGame',
        ),
    ]
