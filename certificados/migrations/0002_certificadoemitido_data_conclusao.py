# Generated by Django 5.1.2 on 2025-07-09 16:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('certificados', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='certificadoemitido',
            name='data_conclusao',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
