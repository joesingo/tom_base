# Generated by Django 2.2.1 on 2019-05-15 00:47

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tom_dataproducts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reduceddatum',
            name='timestamp',
            field=models.DateTimeField(db_index=True, default=datetime.datetime.now),
        ),
    ]
