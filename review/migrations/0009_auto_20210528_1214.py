# Generated by Django 2.1.5 on 2021-05-28 12:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('review', '0008_auto_20200930_1731'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='companyreview',
            options={'ordering': ('-created',)},
        ),
        migrations.AlterModelOptions(
            name='interview',
            options={'ordering': ('-created',)},
        ),
        migrations.AlterField(
            model_name='companyreview',
            name='ip',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='interview',
            name='ip',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='interviewcomment',
            name='ip',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='reviewcomment',
            name='ip',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
