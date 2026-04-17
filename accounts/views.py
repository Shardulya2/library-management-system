from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.core.mail import send_mail

from .models import OTP

User = get_user_model()


def register(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('/transactions/admin-dashboard/')
        return redirect('/books/dashboard/')

    if request.method == 'POST':
        username = request.POST.get('username').strip()
        email = request.POST.get('email').strip()
        password = request.POST.get('password')

        # ❌ Username exists
        if User.objects.filter(username=username).exists():
            return render(request, 'accounts/register.html', {
                'error': "Username already exists"
            })

        # ❌ Email exists
        if User.objects.filter(email=email).exists():
            return render(request, 'accounts/register.html', {
                'error': "Email already registered"
            })

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_active=False,
            role='user'
        )

        code = OTP.generate_otp()
        OTP.objects.create(user=user, code=code)

        send_mail(
            subject='Your OTP Code',
            message=f'Your OTP is {code}',
            from_email='noreply@example.com',
            recipient_list=[email],
        )

        return redirect(f'/accounts/verify/{user.id}/')

    return render(request, 'accounts/register.html')


def verify_otp(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        entered = request.POST.get('otp').strip()
        otp = OTP.objects.filter(user=user).last()

        if otp and otp.code == entered:
            user.is_active = True
            user.is_verified = True
            user.save()

            return redirect('/accounts/user-login/')
        else:
            return render(request, 'accounts/verify.html', {
                'error': "Invalid OTP"
            })

    return render(request, 'accounts/verify.html')


# 👤 USER LOGIN
def user_login(request):

    # 🔥 logout if switching from admin
    if request.user.is_authenticated and request.user.is_superuser:
        logout(request)

    if request.method == 'POST':
        username = request.POST.get('username').strip()
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            if user.role != 'user':
                return render(request, 'accounts/user_login.html', {
                    'error': "Not a user account"
                })

            if not user.is_verified:
                return render(request, 'accounts/user_login.html', {
                    'error': "Verify email first"
                })

            login(request, user)
            return redirect('/books/dashboard/')

        else:
            return render(request, 'accounts/user_login.html', {
                'error': "Invalid username or password"
            })

    return render(request, 'accounts/user_login.html')


# 👑 ADMIN LOGIN
def admin_login(request):

    # 🔥 logout if switching from user
    if request.user.is_authenticated and not request.user.is_superuser:
        logout(request)

    if request.method == 'POST':
        username = request.POST.get('username').strip()
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            if not (user.is_superuser or user.role == 'admin'):
                return render(request, 'accounts/admin_login.html', {
                    'error': "Not an admin account"
                })

            login(request, user)
            return redirect('/transactions/admin-dashboard/')

        else:
            return render(request, 'accounts/admin_login.html', {
                'error': "Invalid username or password"
            })

    return render(request, 'accounts/admin_login.html')


def logout_view(request):
    logout(request)
    return redirect('/')