from django.shortcuts import render
from .api import leagues as leagues_api
from django.contrib.auth.decorators import login_required
# Create your views here.

@login_required(login_url='login')
def index(request):
    return render(request, 'index.html')

def leagues_view(request):
    leagues = leagues_api.get_leagues()
    return render(request, 'leagues.html', {'leagues': leagues})

def login_view(request):
    return render(request, 'login.html')


















