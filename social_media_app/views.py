import random
from django.shortcuts import render, redirect,get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth import logout
from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import *
from django.core.files.storage import FileSystemStorage
from django.core.mail import EmailMessage
from django.utils.functional import SimpleLazyObject
from django.contrib.auth import authenticate, login


# Generate a random verification code
def generate_verification_code():
    return str(random.randint(100000, 999999))

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        # Check if the email already exists
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Email already in use. Please try another one.')
            return redirect('register')  # Redirect to registration page

        try:
            # Create user if email is unique
            user = CustomUser.objects.create_user(username=username, email=email, password=password)
            verification_code = generate_verification_code()

            # Store verification code and user ID in session
            request.session['verification_code'] = verification_code
            request.session['user_id'] = user.id

            # Send verification email
            send_mail(
                'Verify Your Email',
                f'Your verification code is {verification_code}.',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            messages.success(request, 'A verification code has been sent to your email.')
            return redirect('verify_email')  # Redirect to verification page

        except IntegrityError:
            # Handle any unexpected integrity errors
            messages.error(request, 'Email already in use. Please try another one.')
            return redirect('register')

    return render(request, 'social_app/register.html')

def verify_email(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        saved_code = request.session.get('verification_code')
        user_id = request.session.get('user_id')

        if code == saved_code:
            user = CustomUser.objects.get(id=user_id)
            user.is_verified = True
            user.save()
            messages.success(request, 'Your account has been verified.')
            return redirect('login')  # Redirect to login page

        messages.error(request, 'Invalid verification code.')
    return render(request, 'social_app/verify_email.html')


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        user = CustomUser.objects.filter(email=email).first()

        if user:
            verification_code = generate_verification_code()
            request.session['verification_code'] = verification_code
            request.session['user_id'] = user.id

            # Send verification email
            send_mail(
                'Password Reset Request',
                f'Your verification code is {verification_code}.',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            messages.success(request, 'A verification code has been sent to your email.')
            return redirect('verify_password_reset')

        messages.error(request, 'No account found with that email.')
    return render(request, 'social_app/forgot_password.html')

def verify_password_reset(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        saved_code = request.session.get('verification_code')
        user_id = request.session.get('user_id')

        if code == saved_code:
            return redirect('reset_password', user_id=user_id)

        messages.error(request, 'Invalid verification code.')
    return render(request, 'social_app/verify_password_reset.html')

def reset_password(request, user_id):
    if request.method == 'POST':
        new_password = request.POST['new_password']
        user = CustomUser.objects.get(id=user_id)
        user.password = make_password(new_password)  # Hash the new password
        user.save()
        messages.success(request, 'Your password has been reset successfully.')
        return redirect('login')  # Redirect to login page

    return render(request, 'social_app/reset_password.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = CustomUser.objects.filter(email=email).first()

        if user and user.is_verified:
            if authenticate(request, username=user.username, password=password):
                login(request, user)
                messages.success(request, 'You are now logged in.')
                return redirect("/")
            else:
                messages.error(request, 'Invalid credentials.')
        else:
            messages.error(request, 'Please verify your email before logging in.')

    return render(request, 'social_app/login.html')


def logout_view(request):
    logout(request)  # Logs out the user
    return redirect('login') 

def send_email_with_attachments(subject, body, to_email, attachments=[]):
    email = EmailMessage(subject, body, settings.DEFAULT_FROM_EMAIL, [to_email])
    
    for attachment in attachments:
        email.attach_file(attachment.file.path)  # Change to `attachment.file.path`
    
    email.send()

@login_required
def send_message(request):
    if request.method == 'POST':
        recipient_email = request.POST.get('recipient_email', '')
        content = request.POST['content']
        
        # Create the message
        message = Message.objects.create(
            sender=request.user,
            recipient_email=recipient_email,
            content=content
        )

        # Handle file uploads
        attachments = []
        for file in request.FILES.getlist('attachments'):
            attachment = Attachment.objects.create(
                message=message,
                file=file
            )
            attachments.append(attachment)

        # Send email with attachments if recipient email is provided
        if recipient_email:
            send_email_with_attachments(
                subject=f'New Message from {request.user.username}',
                body=content,
                to_email=recipient_email,
                attachments=attachments,
            )

        messages.success(request, 'Message sent successfully!')
        return redirect('inbox')

    return render(request, 'social_app/send_message.html')



@login_required
def inbox(request):
    messages = Message.objects.filter(recipient_email=request.user.email, is_deleted=False).order_by('-timestamp')
    return render(request, 'social_app/inbox.html', {'messages': messages})

@login_required
def delete_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)

    if message.sender == request.user or message.recipient_email == request.user.email:
        message.is_deleted = True
        message.save()
        messages.success(request, 'Message deleted successfully.')
    else:
        messages.error(request, 'You do not have permission to delete this message.')

    return redirect('inbox')

@login_required
def sent_messages(request):
    messages = Message.objects.filter(sender=request.user, is_deleted=False).order_by('-timestamp')
    return render(request, 'social_app/sent_messages.html', {'messages': messages})

def index(request):
    if request.user.is_authenticated:
        messages = Message.objects.filter(recipient_email=request.user.email, is_deleted=False).order_by('-timestamp')
    else:
        return redirect('login') 

    return render(request, 'social_app/index.html', {'messages': messages})