from django.shortcuts import render, redirect
from .api import leagues as leagues_api
from .api import teams as teams_api
from .api import players as players_api 
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Profile
# Create your views here.

from .api import players as players_api
from django.core.paginator import Paginator


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
            
            return redirect('players')
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

@login_required(login_url='login')
def leagues_view(request):

    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            leagues = leagues_api.get_leagues_by_name(name)
            return render(request, 'leagues.html', {'leagues': leagues, 'name': name})

    leagues = leagues_api.get_leagues()
    return render(request, 'leagues.html', {'leagues': leagues})

@login_required(login_url='login')
def league_view(request, guid):
    teams = teams_api.get_teams_by_league_guid(guid)
    return render(request, 'league.html', {'teams': teams})

@login_required(login_url='login')
def team_view(request, guid):
    players = players_api.get_players_by_team_guid(guid)
    return render(request, 'team.html', {"players": players})

@login_required(login_url='login')
def players_view(request):
    players_per_page = 20

    page_number = request.GET.get('page', 1)

    # Fetch the players using your SPARQL query function
    # Adjust the start and limit parameters based on the current page
    start = (int(page_number) - 1) * players_per_page

    ascending = request.GET.get('ascending', 'false') == 'true'
    players = players_api.get_players_by_prop(start=start, limit=players_per_page, ascending=ascending)

    # paginator
    paginator = Paginator(players, players_per_page)
    page_obj = paginator.get_page(page_number)

    return render(request, 'players.html', {'players': players, 'page_obj': page_obj})

    ''' # Temporary static list for testing
    players = [{'name': 'Player 1'}, {'name': 'Player 2'}, ...] * 100

    # Create a Paginator instance with the static list
    paginator = Paginator(players, players_per_page)

    # Get the Page object for the current page
    page_obj = paginator.get_page(page_number)

    return render(request, 'players.html', {'players': page_obj.object_list, 'page_obj': page_obj}) '''














