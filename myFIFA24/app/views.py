from django.shortcuts import render
from myFIFA24.api.leagues import get_leagues, get_leagues_by_name, get_league_by_guid
# Create your views here.


def index(request):
    return render(request, 'index.html')


def leagues_view(request):
    leagues = get_leagues()
    return render(request, 'leagues.html', {'leagues': leagues})

def leagues_by_name_view(request, name):
    leagues = get_leagues_by_name(name)
    return render(request, 'leagues_by_name.html', {'leagues': leagues})

def league_by_guid_view(request, guid):
    league = get_league_by_guid(guid)
    return render(request, 'league_by_guid.html', {'league': league})



















