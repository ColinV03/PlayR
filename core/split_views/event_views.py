from django.shortcuts import render, get_object_or_404
from ..models import *
from ..helpers import *
from ..forms import *

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages # For user feedback messages





@authentication_wrapper
def event_detail_view(request, group_id, event_id):
    context = initialize_context(request)
    
    event = get_object_or_404(GroupScheduleEvent, pk=event_id)
    
    attendees = GroupEventAttendance.objects.filter(event=event, attending=True) # Get attendees who RSVP'd yes
    comments = GroupEventComments.objects.filter(event=event).order_by('-created_at')[:3] # Get latest 3 comments

    if request.user.is_authenticated:
        user_attendance = GroupEventAttendance.objects.filter(event=event, user=request.user).first()
        users_attending_status = user_attendance.attending if user_attendance else False
        
    comment_form = GroupEventCommentForm()


    context = {
        'event': event,
        'attendees': attendees,
        'attendee_count': attendees.count(),
        'comments': comments,
        'users_attending_status': users_attending_status,
        'comment_form': comment_form,
    }
    return render(request, 'pages/events/event.html', context)

@authentication_wrapper
def add_event_comment(request, group_id, event_id):
    event = get_object_or_404(GroupScheduleEvent, pk=event_id)
    user = request.user

    if request.method == 'POST':
        form = GroupEventCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.event = event
            comment.user = user
            comment.save()
            # Redirect to event page with success message
            # messages.success(request, "Comment added successfully.")
            redirect('event_page', group_id=group_id, event_id=event_id)
        else:
            messages.error(request, "Error adding comment.")
    return redirect('event_page', group_id=group_id, event_id=event_id)





@authentication_wrapper
def edit_event(request, group_id, event_id):
    context = initialize_context(request)
    event = get_object_or_404(GroupScheduleEvent, pk=event_id)
    context['create'] = False

    if request.method == 'POST':
        form = GroupEventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, "Event updated successfully.")
            return redirect('event_page', group_id=group_id, event_id=event_id)
    else:
        form = GroupEventForm(instance=event)

    context = {
        'event': event,
        'form': form,
    }
    return render(request, 'pages/events/event_day_form.html', context)




@authentication_wrapper
def event_rsvp(request, group_id, event_id):
    context = initialize_context(request)
    event = get_object_or_404(GroupScheduleEvent, pk=event_id)
    user = request.user

    attendance, created = GroupEventAttendance.objects.get_or_create(event=event, user=user)
    attendance.attending = not attendance.attending
    attendance.save()

    return redirect('event_page', group_id=group_id, event_id=event_id)


@authentication_wrapper
def confirm_game_day_teams_view(request, group_id, event_id):
    event = get_object_or_404(GroupScheduleEvent, pk=event_id)
    game_setups = request.session.get('event_team_setups_' + str(event_id))

    if not game_setups:
        messages.error(request, "No team setups found in session. Please generate teams first.") # Error if no session data
        return redirect('event_detail', event_id=event_id) # Redirect to event detail page with error

    # --- Data Validation (Optional but recommended) ---
    # Here you could add checks to ensure game_setups is in the expected format, etc.

    try:
        for game_setup in game_setups:
            game = Game.objects.create(event=event, date_time=event.start_datetime) # Create Game object for each setup - adjust date_time as needed
            team_a_players = game_setup['team_a']
            team_b_players = game_setup['team_b']

            for player_id in team_a_players: # player_ids are stored in session
                TeamAssignment.objects.create(game=game, user_id=player_id, team_name='Team A')
            for player_id in team_b_players:
                TeamAssignment.objects.create(game=game, user_id=player_id, team_name='Team B')

        # Clear session data after successful save
        del request.session['event_team_setups_' + str(event_id)]
        messages.success(request, "Game day teams have been successfully created and saved.") # Success message

    except Exception as e: # Catch potential errors during DB save
        messages.error(request, f"Error saving game day teams: {e}") # Error message
        # Optionally log the error: logger.exception("Error saving game day teams") # If you have logging setup
        return redirect('event_page', event_id=event_id) # Redirect back to event detail with error message

    return redirect('event_page', event_id=event_id)


@authentication_wrapper
def get_random_teams_and_games_preview(request, group_id, event_id):
    """
        Placeholder for a ajax view that will return randomized teams and games for a pickup game day.

        To be used with HTMX or similar to update the page without a full page reload.

        Args:
            request: The request object.
            group_id: The group ID.
            event_id: The event ID.

        Returns:
            view response

    """

    event = get_object_or_404(GroupScheduleEvent, pk=event_id)
    # attendees = GroupEventAttendance.objects.filter(event=event, attending=True).select_related('user')
    attendees = event.get_attendees().select_related('user') # Use custom method to get attendees

    total_event_duration_minutes = 120  # Example, make dynamic later

    # game_setups_result = generate_random_game_day_teams(list(attendees.values_list('user__first_name', 'user__last_name')), event=event, total_event_duration_minutes=total_event_duration_minutes)


    game_setups_result = generate_even_teams(list(attendees), event=event) # Pass event

    if "error" in game_setups_result:
        error_message = game_setups_result["error"]
        context = {'event': event, 'error_message': error_message}
        return render(request, 'events/game_day_teams_preview.html', context) # Or game_day_teams.html if not using preview

    game_setups = game_setups_result

    context = {
        'event': event,
        'game_setups': game_setups,
    }
    return render(request, 'pages/events/game_day_teams_preview.html', context) # Or game_day_teams.html



    # if "error" in game_setups_result:
    #     error_message = game_setups_result["error"]
    #     context = {'event': event, 'error_message': error_message}
    #     return render(request, 'events/game_day_teams_preview.html', context) # Render preview template even on error for consistent UI

    # game_setups = game_setups_result

    # # Store game_setups in session
    # request.session['event_team_setups_' + str(event_id)] = game_setups

    # context = {
    #     'event': event,
    #     'game_setups': game_setups,
    # }
    # return render(request, 'pages/events/game_day_teams_preview.html', context)
