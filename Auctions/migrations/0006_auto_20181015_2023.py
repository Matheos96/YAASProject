# Generated by Django 2.1.1 on 2018-10-15 17:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Auctions', '0005_bid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='auction',
            name='current_bid',
        ),
        migrations.RemoveField(
            model_name='auction',
            name='current_winner',
        ),
    ]