# Generated by Django 4.2.16 on 2024-10-23 07:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social_media_app', '0006_message_attachment'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='recipient',
        ),
        migrations.AddField(
            model_name='message',
            name='recipient_email',
            field=models.EmailField(default='default@example.com', max_length=254),
        ),
    ]