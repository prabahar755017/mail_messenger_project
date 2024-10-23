
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
import datetime
import os
from django.utils import timezone
from django.conf import settings


def getFileName(requset,filename):
    now_time=datetime.datetime.now().strftime("%Y%m%d%H:%M:%S")
    new_filename="%s%s"%(now_time,filename)
    return os.path.join('uploads/',new_filename)

class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None):
        if not email:
            raise ValueError('Users must have an email address')
        if not username:
            raise ValueError('Users must have a username')

        email = self.normalize_email(email)
        user = self.model(username=username, email=email)
        user.set_password(password)  # Hash the password
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None):
        user = self.create_user(username, email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()  # Assign the custom manager

    USERNAME_FIELD = 'email'  # Use email as the login field
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username


from django.db import models
from django.conf import settings
from django.utils import timezone

class Attachment(models.Model):
    message = models.ForeignKey('Message', related_name='attachments', on_delete=models.CASCADE)
    file = models.FileField(upload_to='attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Attachment for message {self.message.id}: {self.file.name}'

class Message(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_messages', on_delete=models.CASCADE)
    recipient_email = models.EmailField(default='default@example.com')  # Ensure this field exists
    content = models.TextField(blank=True)  # Making content optional for non-text messages
    timestamp = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.SET_NULL)

    def __str__(self):
        return f'Message from {self.sender.username} to {self.recipient.username} at {self.timestamp}'
