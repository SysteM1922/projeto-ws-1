from django.shortcuts import render, redirect
from .api import leagues as leagues_api
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Profile
# Create your views here.

@login_required(login_url='login')
def index(request):

    return render(request, 'index.html')

def login_view(request):

    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            
            if request.POST.get("remember"):
                request.session.set_expiry(1209600)
            
            return redirect('index')
        else:
            messages.error(request, 'Invalid credentials')
            return redirect('login')

    return render(request, 'login.html')

@login_required(login_url='login')
def logout_view(request):
    auth.logout(request)
    return redirect('login')

def signup_view(request):

    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm-password']
        email = request.POST['email']

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username is already taken')
            return redirect('signup')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email is already taken')
            return redirect('signup')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return redirect('signup')

        user = User.objects.create_user(username=username, password=password, email=email)
        Profile.objects.create(user=user)
        user.save()

        return redirect('login')

    return render(request, 'signup.html')

def leagues_view(request):
    leagues = leagues_api.get_leagues()
    return render(request, 'leagues.html', {'leagues': leagues})


















