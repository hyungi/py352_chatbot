# Generated by Django 2.0.1 on 2018-02-11 01:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('article', '0007_auto_20180211_0119'),
    ]

    operations = [
        migrations.AlterField(
            model_name='crawlerdata',
            name='crawled_date',
            field=models.DateTimeField(default='2018-02-11 01:30'),
        ),
        migrations.AlterField(
            model_name='newsrequirement',
            name='request_time',
            field=models.DateTimeField(default='2018-02-11 01:30'),
        ),
        migrations.AlterField(
            model_name='requirement',
            name='request_date',
            field=models.DateTimeField(default='2018-02-11 01:30'),
        ),
        migrations.AlterField(
            model_name='userstatus',
            name='gender',
            field=models.CharField(default='', max_length=4),
        ),
    ]
