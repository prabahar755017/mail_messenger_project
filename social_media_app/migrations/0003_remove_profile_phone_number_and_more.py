# Generated by Django 4.2.16 on 2024-10-22 06:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('social_media_app', '0002_post_image_post_video_profile_friendrequest'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='phone_number',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='verification_code',
        ),
    ]
