# Generated by Django 4.2.4 on 2023-08-12 17:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_alter_apikey_id_alter_continuousmetricdata_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='discretemetricdata',
            name='metric',
            field=models.IntegerField(),
        ),
    ]
