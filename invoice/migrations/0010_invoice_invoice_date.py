# Generated by Django 4.1.2 on 2022-12-11 18:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoice', '0009_invoice_discount_invoice_po_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='invoice_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
