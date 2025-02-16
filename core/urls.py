"""
URL configuration for playr project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views
from core.split_views import profile_views
from core.split_views import event_views

urlpatterns = [
    path('', views.home, name='home'),
    path('unauthorized', views.unauthorized, name='unauthorized'),
    path('about', views.about, name='about'),

    path('create_users/<int:num_users>', views.create_users, name='create_users'),
    path('add_random_groups', views.add_random_groups, name='add_random_groups'),
    path('randomize_group_event_attendance', views.randomize_group_event_attendance, name='randomize_group_event_attendance'),



    path('account/', views.profile, name='profile'),
    path('account/edit', views.edit_profile, name='edit_profile'),
    path('account/signup', views.signup, name='signup'),
    path('account/login', views.login_view, name='login'),
    path('account/logout', views.logout_view, name='logout'),
    path('account/notifications/read', views.mark_all_notifications_read, name='mark_all_notifications_read'),

    path('profiles/<str:username>', profile_views.public_profile, name='public_profile'),



    path('groups', views.pickup_groups, name='pickup_groups'),
    path('groups/create', views.create_group, name='create_group'),
    path('groups/<int:group_id>', views.group_page, name='group_page'),

    path('groups/<int:group_id>/join', views.join_group_request, name='join_group'),
    path('groups/<int:group_id>/leave', views.leave_group, name='leave_group'),

    path('groups/<int:group_id>/approve/<int:user_id>', views.approve_member, name='approve_membership'),
    path('groups/<int:group_id>/remove/<int:user_id>', views.remove_member, name='remove_membership'),

    path('groups/<int:group_id>/delete', views.delete_group, name='delete_group'),

    path('groups/<int:group_id>/create_event', views.create_event_day, name='create_event_day'),
    path('groups/<int:group_id>/events/<int:event_id>', event_views.event_detail_view, name='event_page'),
    # path('groups/<int:group_id>/events/<int:event_id>/delete', views.delete_event, name='delete_event'),
    path('groups/<int:group_id>/events/<int:event_id>/edit', event_views.edit_event, name='edit_event'),
    
    path('groups/<int:group_id>/events/<int:event_id>/rsvp', event_views.event_rsvp, name='event_rsvp'),

    path('groups/<int:group_id>/events/<int:event_id>/add_comment', event_views.add_event_comment, name='add_event_comment'),




    path('groups/<int:group_id>/events/<int:event_id>/generate_game_day_teams', event_views.get_random_teams_and_games_preview, name='get_random_teams_and_games_preview'),
    path('groups/<int:group_id>/events/<int:event_id>/start_game_day_teams', event_views.confirm_game_day_teams_view, name='confirm_game_day_teams_view'),







 
]
