# Generated by Django 2.0.4 on 2018-04-04 06:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('processor', '0002_remove_register_addr'),
    ]

    operations = [
        migrations.AddField(
            model_name='mipsprogram',
            name='label',
            field=models.CharField(blank=True, max_length=20),
        ),
    ]
