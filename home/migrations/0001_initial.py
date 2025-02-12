# Generated by Django 5.1.5 on 2025-02-07 18:47

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='qr_code',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(blank=True, null=True, upload_to='images/')),
                ('name', models.CharField(max_length=50)),
                ('size', models.IntegerField()),
                ('shape', models.IntegerField()),
                ('custom_style', models.CharField(max_length=255)),
                ('link', models.TextField()),
                ('data_create', models.DateTimeField(default=django.utils.timezone.now)),
                ('expiry_date', models.IntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Subscribers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subscriber', models.CharField(max_length=255)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
