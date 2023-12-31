# Generated by Django 4.2.4 on 2023-09-05 16:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hospital', '0022_prescription'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accountant',
            name='email',
            field=models.EmailField(default='', max_length=254),
        ),
        migrations.AlterField(
            model_name='doctor',
            name='email',
            field=models.EmailField(default='', max_length=254),
        ),
        migrations.AlterField(
            model_name='patient',
            name='email',
            field=models.EmailField(default='', max_length=254),
        ),
        migrations.AlterField(
            model_name='patientdischargedetails',
            name='email',
            field=models.EmailField(default='', max_length=254),
        ),
    ]
