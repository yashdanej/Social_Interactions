# Generated by Django 4.0.5 on 2022-06-28 05:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_alter_profile_profileimg'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='profileimg',
            field=models.ImageField(default='profile_blank.png', upload_to='profile_images'),
        ),
    ]
