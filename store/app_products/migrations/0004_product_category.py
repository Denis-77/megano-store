# Generated by Django 4.2.6 on 2024-02-14 18:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app_catalog', '0004_alter_image_catalog_item'),
        ('app_products', '0003_alter_image_product'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='category',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='app_catalog.catalogitem'),
        ),
    ]
