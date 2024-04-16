from django.shortcuts import render, redirect
from .api import leagues as leagues_api
from .api import teams as teams_api
from .api import players as players_api 
from .api import squads as squads_api
from .api import game as game_api
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Profile
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
import random

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

    players_per_page = 30

    page_number = int(request.POST.get('page', 1))

    # Fetch the players using your SPARQL query function
    # Adjust the start and limit parameters based on the current page
    start = (page_number - 1) * players_per_page

    nationalities = players_api.get_nationalities()
    teams = teams_api.get_teams()
    genders = players_api.get_genders()
    positions = players_api.get_positions()

    props = None

    if request.method == 'POST':
        name = request.POST.get('name')
        nationality = request.POST.get('nationality')
        team = request.POST.get('team')
        gender = request.POST.get('gender')
        position = request.POST.get('position')
        order = request.POST.get('order')

        props = []

        if name:
            props.append({"prop": "name", "value": name})
        if nationality:
            props.append({"prop": "nationality", "value": nationality})
        if team:
            print(team)
            props.append({"prop": "team", "value": team})
        if gender:
            props.append({"prop": "gender", "value": gender})
        if position:
            props.append({"prop": "position", "value": position})
        if order:
            props.append({"prop": "order", "value": order})

        if not props:
            props = None

    # Fetch the players using your SPARQL query function with filters
    players = players_api.get_players_by_prop(start=start, limit=players_per_page, props=props)

    total_players = players_api.get_total_players(props=props)

    page_obj = {
        "has_previous": page_number > 1,
        "previous_page_number": page_number - 1,
        "number": page_number,
        "num_pages": total_players // players_per_page + 1 if total_players % players_per_page else total_players // players_per_page,
        "has_next": total_players > start + players_per_page,
        "next_page_number": page_number + 1,
    }

    return render(request, 'players.html', {'players': players, 'page_obj': page_obj, "filters": {"nationalities": nationalities, "teams": teams, "genders": genders, "positions": positions}, "form": {"name": request.POST.get('name', ""), "nationality": request.POST.get('nationality'), "team": request.POST.get('team'), "gender": request.POST.get('gender'), "position": request.POST.get('position'), "order": request.POST.get('order')}})

@login_required(login_url='login')
def player_view(request, guid):
    player = players_api.get_player_by_guid(guid)
    return render(request, 'player.html', {'player': player})

@require_POST
def search_players(request):
    name = request.POST.get('name', '')

    props = []

    if name:
        props.append({"prop": "name", "value": name})

    players = players_api.get_players_base_info_by_name(name=name)
    
    # print("players:", players)
    
    results = []

    for player in players:
        results.append({
            "id": player["playerid"],
            "name": player["name"],
            "shield": player["shield"],
            })

    # print("results:", results)

    return JsonResponse(results, safe=False)



@login_required(login_url='login')
def squad_view(request):
    return render(request, 'squad.html')

@login_required(login_url='login')
def save_squad(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            squad_name = data['name']
            user_id = request.user.id
            formation = data['formation']
            players = data['players']

            # Fetch the user profile by user ID
            user = User.objects.get(id=user_id)
            # Assuming you have a one-to-one relationship with a UserProfile model
            # and it has a squad_id attribute
            squad_id = user.profile.last_squad_id

            print(f"Squad Name: {squad_name}, ID: {squad_id}, Formation: {formation}, Players: {players}")

            result = squads_api.create_squad(user_id, squad={"id":squad_id, "name": squad_name, "formation": formation, "players": players})

            if result:
                user.profile.last_squad_id += 1
                user.profile.save()
                JsonResponse({'status': 'success', 'message': 'Squad saved successfully'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Squad already exists'})
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User not found'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
    
@login_required(login_url='login')  
def squads_by_user(request):
    # squads = squads_api.get_squads_by_user_id(request.user.id)
    # mock squads
    squads = [{
        "squadId": 1,
        "name": f"Squad {1}",
        "formation": "4-3-3",
        "players": [{'id': 'http://fifa24/player/guid/20801', 'pos': '1', 'shield':'https://media.contentapi.ea.com/content/dam/ea/easfc/fc-24/ratings/common/full/player-shields/en/20801.png'}, {'id': 'http://fifa24/player/guid/20801', 'pos': '2'}, {'id': 'http://fifa24/player/guid/20801', 'pos': '3'}, {'id': 'http://fifa24/player/guid/20801', 'pos': '4'}, {'id': 'http://fifa24/player/guid/20801', 'pos': '5'}, {'id': 'http://fifa24/player/guid/20801', 'pos': '6'}, {'id': 'http://fifa24/player/guid/20801', 'pos': '7'}, {'id': 'http://fifa24/player/guid/20801', 'pos': '8'}, {'id': 'http://fifa24/player/guid/20801', 'pos': '9'}, {'id': 'http://fifa24/player/guid/20801', 'pos': '10'}, {'id': 'http://fifa24/player/guid/20801', 'pos': '11'}]
    }]

    players = [
        {'id': 'http://fifa24/player/guid/20801', 'pos': '1', 'shield':'https://media.contentapi.ea.com/content/dam/ea/easfc/fc-24/ratings/common/full/player-shields/en/20801.png'}, 
        {'id': 'http://fifa24/player/guid/20801', 'pos': '2'}, 
        {'id': 'http://fifa24/player/guid/20801', 'pos': '3'}, 
        {'id': 'http://fifa24/player/guid/20801', 'pos': '4'}, 
        {'id': 'http://fifa24/player/guid/20801', 'pos': '5'}, 
        {'id': 'http://fifa24/player/guid/20801', 'pos': '6'}, 
        {'id': 'http://fifa24/player/guid/20801', 'pos': '7'}, 
        {'id': 'http://fifa24/player/guid/20801', 'pos': '8'}, 
        {'id': 'http://fifa24/player/guid/20801', 'pos': '9'}, 
        {'id': 'http://fifa24/player/guid/20801', 'pos': '10'}, 
        {'id': 'http://fifa24/player/guid/20801', 'pos': '11'}
    ]

    # Extract the 'shield' attribute from the first player
    first_shield = players[0]['shield']

    # Iterate over the list starting from the second element
    for i in range(1, len(players)):
        # Update each player dictionary with the 'shield' attribute from the first player
        players[i]['shield'] = first_shield

    squads[0]["players"] = players
    # print("players:", players)
    return render(request, 'squads.html', {'squads': squads, 'user_id': request.user.id})


@login_required(login_url='login')
def update_squad(request, squad_id):
    # squad = squads_api.get_squad_by_guid(squad_id)
    # this will return the players list with the shield attribute

    squad = {
        "squadId": 1,
        "name": f"Squad {1}",
        "formation": "4-3-3",
        "players": [{'id': 'http://fifa24/player/guid/20801', 'pos': '1', 'shield': 'https://media.contentapi.ea.com/content/dam/ea/easfc/fc-24/ratings/common/full/player-shields/en/20801.png'}, {'id': 'http://fifa24/player/guid/20801', 'pos': '2', 'shield': 'https://media.contentapi.ea.com/content/dam/ea/easfc/fc-24/ratings/common/full/player-shields/en/20801.png'}, {'id': 'http://fifa24/player/guid/20801', 'pos': '3', 'shield': 'https://media.contentapi.ea.com/content/dam/ea/easfc/fc-24/ratings/common/full/player-shields/en/20801.png'}, {'id': 'http://fifa24/player/guid/20801', 'pos': '4', 'shield': 'https://media.contentapi.ea.com/content/dam/ea/easfc/fc-24/ratings/common/full/player-shields/en/20801.png'}, {'id': 'http://fifa24/player/guid/20801', 'pos': '5', 'shield': 'https://media.contentapi.ea.com/content/dam/ea/easfc/fc-24/ratings/common/full/player-shields/en/20801.png'}, {'id': 'http://fifa24/player/guid/20801', 'pos': '6', 'shield': 'https://media.contentapi.ea.com/content/dam/ea/easfc/fc-24/ratings/common/full/player-shields/en/20801.png'}, {'id': 'http://fifa24/player/guid/20801', 'pos': '7', 'shield': 'https://media.contentapi.ea.com/content/dam/ea/easfc/fc-24/ratings/common/full/player-shields/en/20801.png'}, {'id': 'http://fifa24/player/guid/20801', 'pos': '8', 'shield': 'https://media.contentapi.ea.com/content/dam/ea/easfc/fc-24/ratings/common/full/player-shields/en/20801.png'}, {'id': 'http://fifa24/player/guid/20801', 'pos': '9', 'shield': 'https://media.contentapi.ea.com/content/dam/ea/easfc/fc-24/ratings/common/full/player-shields/en/20801.png'}, {'id': 'http://fifa24/player/guid/20801', 'pos': '10', 'shield': 'https://media.contentapi.ea.com/content/dam/ea/easfc/fc-24/ratings/common/full/player-shields/en/20801.png'}, {'id': 'http://fifa24/player/guid/20801', 'pos': '11', 'shield': 'https://media.contentapi.ea.com/content/dam/ea/easfc/fc-24/ratings/common/full/player-shields/en/20801.png'}]
    }

    # print("squad:", squad)
    return render(request, 'update_squad.html', {'squad': squad})

last_player = None
last_stat = None
guessed = False

@login_required(login_url='login')
def game_view(request):

    global last_player
    global last_stat
    global guessed

    
    value = request.POST.get('value', None)

    print(value)

    if request.method == 'POST':

        if value and not guessed:
    
            flag = game_api.guess_stat(last_player["playerid"], last_stat, value)
            
            guessed = True
    
            return render(request, 'game.html', {'player': last_player, 'stat': last_stat, 'correct': flag, "value": ""})
        
    guessed = False

    stats = ["name", "ovr", "pac", "sho", "pas", "dri", "def", "phy"]

    player = game_api.get_random_player()

    stat = random.choice(stats)

    last_player = player
    last_stat = stat

    return render(request, 'game.html', {'player': player, 'stat': stat, "value": ""})


@login_required(login_url='login')  
def update_squad(request, squad_id):
    if request.method == 'POST':
        try:
            # Parse the JSON data from the request body
            data = json.loads(request.body)
            squad_id = data.get('squadId')
            squad_name = data.get('squadName')
            squad_formation = data.get('squadFormation')
            player_ids = data.get('playerIds')

            # Construct the squad object
            squad = {
                'id': squad_id,
                'name': squad_name,
                'formation': squad_formation,
                'players': [{'id': player_id} for player_id in player_ids],
            }

            # Call the update_squad function
            result = update_squad(squad_id, squad)

            # Return a JSON response based on the result
            if result:
                return JsonResponse({'status': 'success', 'message': 'Squad saved successfully.'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Failed to save squad.'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)