# Generated by Django 2.2 on 2021-04-09 18:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authapp', '0004_shopuserprofile'),
    ]

    operations = [
        migrations.AddField(
            model_name='shopuser',
            name='registration_type',
            field=models.CharField(blank=True, choices=[('D', 'direct'), ('G', 'Google')], max_length=1, verbose_name='registration type'),
        ),
    ]
