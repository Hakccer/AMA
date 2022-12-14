# Generated by Django 4.0.4 on 2022-09-06 13:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('amazon', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Products',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prod_img', models.ImageField(upload_to='')),
                ('title', models.CharField(max_length=100)),
                ('desc', models.TextField()),
                ('stock', models.IntegerField(default=10)),
                ('price', models.PositiveIntegerField()),
                ('category', models.CharField(max_length=100)),
            ],
        ),
        migrations.AlterField(
            model_name='user',
            name='cart',
            field=models.TextField(default='No Items In Cart'),
        ),
        migrations.AlterField(
            model_name='user',
            name='orders',
            field=models.TextField(default='No Orders Doned Or Delieverd'),
        ),
    ]
