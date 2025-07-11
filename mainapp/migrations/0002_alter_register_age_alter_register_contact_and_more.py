# Generated by Django 4.2.23 on 2025-06-21 05:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='register',
            name='age',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='register',
            name='contact',
            field=models.CharField(blank=True, default='Unknown', max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='register',
            name='email',
            field=models.EmailField(max_length=50),
        ),
    ]
