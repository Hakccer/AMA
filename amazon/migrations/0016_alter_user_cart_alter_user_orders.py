# Generated by Django 4.0.4 on 2022-09-08 11:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('amazon', '0015_rename_prod_pehchan_product_prod_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='cart',
            field=models.TextField(default='[]'),
        ),
        migrations.AlterField(
            model_name='user',
            name='orders',
            field=models.TextField(default='[]'),
        ),
    ]
