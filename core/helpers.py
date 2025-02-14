from functools import wraps
from django.http import HttpResponse
from django.shortcuts import redirect
from .models import UserProfile
from faker import Faker

fake = Faker()

def initialize_context(request):
    context = {
        'user': request.user,
        'authenticated': request.user.is_authenticated,
    }
    return context


def authentication_wrapper(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        else:
            return redirect('unauthorized')


            # return HttpResponse("Unauthorized", status=401)
    return wrapper

# utils.py (or your file)

def generate_game_day_teams(players, event):  # Removed team_size parameter, now takes 'event'
    """
    Generates balanced teams and game schedules for a pickup game day,
    using team_size from the GroupScheduleEvent.

    Args:
        players: A list of UserProfile objects participating.
        event: The GroupScheduleEvent object containing event details, including team_size.

    Returns:
        A list of dictionaries, where each dictionary represents a game setup
        and contains 'team_a', 'team_b', and 'sitting_out' player lists.
    """
    team_size = event.team_size # Get team_size from the event object

    team_a_players = []
    team_b_players = []
    team_a_score = 0
    team_b_score = 0

    sorted_players = sorted(players, key=lambda player: player.score, reverse=True)

    game_setups = []
    all_players_available = list(sorted_players)
    players_played_in_game = set()

    game_number = 1
    while all_players_available:
        current_game_setup = {
            'game_number': game_number,
            'team_a': [],
            'team_b': [],
            'sitting_out': [],
        }

        while len(current_game_setup['team_a']) < team_size and all_players_available:
            player = all_players_available.pop(0)
            current_game_setup['team_a'].append(player)
            players_played_in_game.add(player)

        while len(current_game_setup['team_b']) < team_size and all_players_available:
            player = all_players_available.pop(0)
            current_game_setup['team_b'].append(player)
            players_played_in_game.add(player)

        current_game_setup['sitting_out'] = list(all_players_available)
        all_players_available = []

        game_setups.append(current_game_setup)
        game_number += 1

        players_sitting_out_current_game = current_game_setup['sitting_out']
        players_played_current_game = set(current_game_setup['team_a'] + current_game_setup['team_b'])

        all_players_available = players_sitting_out_current_game + [player for player in sorted_players if player not in players_sitting_out_current_game and player not in players_played_in_game]
        all_players_available = sorted(all_players_available, key=lambda player: player.score, reverse=True)

        if not all_players_available and (len(current_game_setup['team_a']) < 2 or len(current_game_setup['team_b']) < 2):
            break

        if not all_players_available:
            break

    return game_setups


import random
import math # for ceil

# def generate_game_teams(players, team_size):
#     """
#     Generates balanced teams for a game, using a specified team size.

#     Args:
#         players: A list of UserProfile objects.
#         team_size: The number of players per team.

#     Returns:
#         A tuple of two lists, each containing UserProfile objects.
#     """
#     team_a = []
#     team_b = []
#     team_a_score = 0
#     team_b_score = 0

#     sorted_players = sorted(players, key=lambda player: player.score, reverse=True)

#     for player in sorted_players:
#         if len(team_a) < team_size:
#             team_a.append(player)
#             team_a_score += player.score
#         elif len(team_b) < team_size:
#             team_b.append(player)
#             team_b_score += player.score
#         else:
#             if team_a_score < team_b_score:
#                 team_a.append(player)
#                 team_a_score += player.score
#             else:
#                 team_b.append(player)
#                 team_b_score += player.score

#     return team_a, team_b


def generate_even_teams(players, event):
    """
    Generates teams with even distribution of players, even if it means
    teams are slightly larger than the ideal team_size. Score balancing is disregarded.

    Args:
        players: A list of UserProfile objects.
        event: The GroupScheduleEvent object (with team_size).

    Returns:
        A list of dictionaries, each representing a game setup.
    """
    team_size = event.team_size
    # calculate duration based on event start_time and end_time, both are datetime objects
    event_duration = abs(event.end_time - event.start_time)
    event_duration_minutes = event_duration.total_seconds() / 60
    
    game_length_duration_minutes = event.game_duration if event.game_duration > 0 else event_duration_minutes


    # show leftover time, if any, after all games are played
    max_number_of_games = event_duration_minutes // game_length_duration_minutes
    print("Max Number of Games: ", max_number_of_games)

    remaining_time = event_duration_minutes % game_length_duration_minutes
    print("Remaining Time: ", remaining_time)

    # suggest a different game length if the event duration is not a multiple of the game length
    if remaining_time > 0:
        print("Suggest a different game length or event duration to evenly distribute games.")
        print("Suggested Game Length: ", game_length_duration_minutes + remaining_time / max_number_of_games)
         
        game_length_duration_minutes = game_length_duration_minutes + (remaining_time / max_number_of_games)

        #  Shorten the games to add additional games if there is remaining time
        max_number_of_games += 1
        game_length_duration_minutes = event_duration_minutes / max_number_of_games












    num_players = len(players)

    if team_size <= 0:
        return {"error": "Team size must be greater than 0."}
    if num_players == 0:
        return {"error": "No players attending the event."}

    game_setups = []
    available_players = list(players)
    random.shuffle(available_players) # Shuffle players once at the start

    # Hash map to track each player's game count / playtime
    player_game_counts = {player: 0 for player in available_players}

    for game_number in range(1, int(max_number_of_games) + 1):
        if not available_players:
            break

        # if there's only one gam, add all players to the game for both teams
        if max_number_of_games == 1:
            current_game_setup = {
                'game_number': game_number,
                'team_a': available_players[:team_size],
                'team_b': available_players[team_size:team_size * 2],
                'sitting_out': available_players[team_size * 2:],
                'estimated_playtime_minutes': game_length_duration_minutes
            }
            game_setups.append(current_game_setup)
            break

        
        current_game_setup = {
            'game_number': game_number,
            'team_a': [],
            'team_b': [],
            'sitting_out': [],
            'estimated_playtime_minutes': game_length_duration_minutes
        }

        while len(current_game_setup['team_a']) < team_size and available_players:
            player = available_players.pop(0)
            current_game_setup['team_a'].append(player)
            player_game_counts[player] += 1

        while len(current_game_setup['team_b']) < team_size and available_players:
            player = available_players.pop(0)
            current_game_setup['team_b'].append(player)
            player_game_counts[player] += 1

        current_game_setup['sitting_out'] = list(available_players)

        game_setups.append(current_game_setup)

        # Re-add players to available list for next game
        available_players = list(players)
        random.shuffle(available_players)

        # Sort players by game count to balance playtime
        available_players.sort(key=lambda player: player_game_counts[player])

    return game_setups




def generate_random_game_day_teams(players, event, total_event_duration_minutes):
    """
    Generates randomized teams and game schedules for a pickup game day,
    aiming for fair playtime and using event's team_size and max_participants.

    Args:
        players: A list of UserProfile objects.
        event: The GroupScheduleEvent object.
        total_event_duration_minutes: Total duration of the event in minutes.

    Returns:
        A list of dictionaries, each representing a game setup.
    """
    try: 

        print("players", players)
        print("event", event)
        print("total_event_duration_minutes", total_event_duration_minutes)

        team_size = event.team_size
        print("team_size", team_size)

        max_participants = event.max_participants
        num_players = len(players)
        players_per_game = team_size * 2  # Players needed for one full game (e.g., 5v5)
        print("players_per_game", players_per_game)
        print("num_players", num_players)
     
     

        players_in_field_at_once = min(num_players, max_participants if max_participants > 0 else num_players, players_per_game) # Consider max_participants if set, default to total players if max_participants is 0 or not set
        num_sitting_out = num_players - players_in_field_at_once if num_players > players_in_field_at_once else 0

        print("field:", players_in_field_at_once)

        num_games_needed_estimate = math.ceil(num_players / players_per_game) if players_per_game > 0 else 1 # Estimate games, at least 1 if team size is valid
        estimated_game_duration_minutes = total_event_duration_minutes # For now, assume each game roughly equals event duration, simplify rotation first

        game_setups = []
        available_players = list(players) # Start with all players available

        for game_number in range(1, num_games_needed_estimate + 1): # Iterate based on estimated games needed
            if not available_players: # No more players to form games
                break

            current_game_setup = {
                'game_number': game_number,
                'team_a': [],
                'team_b': [],
                'sitting_out': [],
                'estimated_playtime_minutes': estimated_game_duration_minutes # For now, same for each game setup
            }

            random.shuffle(available_players) # Randomize player order

            team_a_count = min(team_size, len(available_players)) # Team A can have at most team_size, or fewer if players run out
            current_game_setup['team_a'] = available_players[:team_a_count]
            available_players = available_players[team_a_count:] # Remove team A players from available

            team_b_count = min(team_size, len(available_players)) # Team B count, same logic
            current_game_setup['team_b'] = available_players[:team_b_count]
            
            # ensure the length of the two arrays are equal, if not, rebalance teams
            if len(current_game_setup['team_a']) != len(current_game_setup['team_b']):
                current_game_setup['team_b'].append(current_game_setup['team_a'].pop())
                
            current_game_setup['sitting_out'] = available_players[team_b_count:] # Remaining players sit out this game
            available_players = [] # Reset for next game if needed - for simple rotation, everyone not in team A or B sits out this iteration



            game_setups.append(current_game_setup)


        return game_setups
    except Exception as e:
        print(e)
        return []
    

def generate_random_users(num_users=10):
    """
    Generates random user profiles for testing purposes.

    Args:
        num_users: The number of user profiles to generate.

    Returns:
        A list of UserProfile objects with random data.
    """
    users = []
    #  user Faker
    for i in range(num_users):
        print("Creating User# ", i)
        user = UserProfile(
            username=fake.user_name(),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.email(),
            score=random.randint(0, 10),
            password="password123",
            is_staff= fake.boolean(),
            is_superuser= fake.boolean(),
            is_active= True,
            date_joined= str(fake.date_time_this_year()),
            last_login= None
        )
        user.save()
    return users
