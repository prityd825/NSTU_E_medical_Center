# Generated by Django 4.2.4 on 2023-09-06 15:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('hospital', '0028_appointment_doctorid_appointment_doctorname_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='patient',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
