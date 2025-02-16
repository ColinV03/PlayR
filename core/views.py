import random
from django.shortcuts import redirect, render
from django.utils import timezone
from .forms import *
from django.contrib.auth import authenticate, login, logout
from .helpers import authentication_wrapper, generate_random_users, initialize_context
from .models import *



def home(request):
    context = initialize_context(request)
    return render(request, 'pages/home.html', context)

def unauthorized(request):
    return render(request, 'unauthorized.html')

def about(request):
    context = initialize_context(request)
    return render(request, 'pages/about.html', context)

@authentication_wrapper
def create_users(request, num_users=None):
    if num_users:
        generate_random_users(num_users=num_users)
    else:
        generate_random_users(num_users=10)
    return redirect('home')

@authentication_wrapper
def add_random_groups(request):

    users = UserProfile.objects.all()
    groups = Group.objects.all()

    for user in users:
        try:

            random_group = random.choice(groups)
            membership = GroupMembership(group=random_group, user=user, approved=True, is_organizer=False, approved_date=timezone.now())
            membership.save()
        except Exception as e:
            print(e)
            pass


    return redirect('home')

@authentication_wrapper
def randomize_group_event_attendance(request):
    # users can only join events that belong to their group memberships
    # for each user, get all group memberships
    # for each group membership, get all events
    # for each event, randomly join or leave

    users = UserProfile.objects.all()
    group_memberships = GroupMembership.objects.all()
    group_events = GroupScheduleEvent.objects.all()

    for user in users:
        for membership in group_memberships:
            if membership.user == user:
                # print(f"User: {user.username} is a member of {membership.group.name}")
                for event in group_events:
                    # print(f"Checking event: {event.description}")
                    if event.group == membership.group:
                        # print(f"Event {event.description} is in {membership.group.name}")
                        if event.is_joinable():
                            print(f"Event {event.description} is joinable")
                            if random.choice([True, False]):
                                attendance, created = GroupEventAttendance.objects.get_or_create(event=event, user=user)
                                attendance.attending = True
                                attendance.save()

    return redirect('home')



def signup(request):
    context = initialize_context(request)
    signup_form = UserForm()

    context['form'] = signup_form

    if request.method == 'POST':
        signup_form = UserForm(request.POST)
        if signup_form.is_valid():
            signup_form.save()
            return redirect('login')
        else:            
            context['signup_form'] = signup_form
            render(request, 'pages/auth/signup.html', context)

    return render(request, 'pages/auth/signup.html', context)

def login_view(request):
    context = initialize_context(request)

    if request.method == 'POST':
        form = UserLoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # Redirect to home page after login
            else:
                form.add_error(None, "Invalid username or password")
    else:
        form = UserLoginForm()
        context['form'] = form
    return render(request, 'pages/auth/login.html', context)


def logout_view(request):
    context = initialize_context(request)
    if request.user.is_authenticated:
        logout(request)
    return redirect('home')


def profile(request):
    context = initialize_context(request)
    profile = UserProfile.objects.get(username=request.user)
    context['profile'] = profile
    return render(request, 'pages/auth/profile.html', context)

@authentication_wrapper
def edit_profile(request):
    context = initialize_context(request)
    profile = UserProfile.objects.get(username=request.user)
    context['profile'] = profile
    profile_form = ProfileForm(instance=profile)
    context['form'] = profile_form    


    if request.method == 'POST':
        profile_form = ProfileForm(request.POST, instance=profile)
        if profile_form.is_valid():
            profile_form.save()
            return redirect('profile')
        else:
            context['form'] = profile_form

    return render(request, 'pages/auth/edit_profile.html', context)
    



@authentication_wrapper
def pickup_groups(request):
    context = initialize_context(request)
    groups = Group.objects.filter(public=True)
    context['groups'] = groups
    # Logic to get all groups and leagues that are public and active
    # groups = Group.objects.filter(public=True, active=True)

    return render(request, 'pages/groups/all_groups.html', context)


@authentication_wrapper
def group_page(request, group_id):
    context = initialize_context(request)
    group = Group.objects.get(id=group_id)
    context['group'] = group

    organizer = group.organizer == request.user
    context['organizer'] = organizer

    is_member = GroupMembership.objects.filter(group=group, user=request.user, approved=True).exists()
    context['is_member'] = is_member


    return render(request, 'pages/groups/group.html', context)

@authentication_wrapper
def create_group(request):
    context = initialize_context(request)
    group_form = GroupCreationForm()
    context['form'] = group_form

    if request.method == 'POST':
        group_form = GroupCreationForm(request.POST)
        if group_form.is_valid():
            # set the organizer to the current user
            group_form.instance.organizer = request.user
            group_form.save()
            group = group_form.instance.id
            group_item = Group.objects.get(id=group)

            # add membership of owner to the group
            membership = GroupMembership(group=group_item, user=request.user, approved=True, is_organizer=True, approved_date=timezone.now())
            membership.save()

            return redirect('group_page', group_id=group)
        else:
            context['form'] = group_form
            render(request, 'pages/groups/create_group.html', context)

    return render(request, 'pages/groups/create_group.html', context)

@authentication_wrapper
def join_group_request(request, group_id):
    context = initialize_context(request)
    group = Group.objects.get(id=group_id)
    context['group'] = group

    if request.method == 'POST':
        membership = GroupMembership(group=group, user=request.user)
        membership.save()
        return redirect('group_page', group_id=group_id)

    return render(request, 'pages/groups/join_group_request.html', context)

@authentication_wrapper
def leave_group(request, group_id):
    context = initialize_context(request)
    group = Group.objects.get(id=group_id)
    context['group'] = group

    membership = GroupMembership.objects.get(group=group, user=request.user)
    if membership.is_organizer:
        return redirect('group_page', group_id=group_id)

    membership.delete()

    return redirect('group_page', group_id=group_id)




@authentication_wrapper
def approve_member(request, group_id, user_id):
    context = initialize_context(request)
    group = Group.objects.get(id=group_id)
    context['group'] = group

    member = UserProfile.objects.get(id=user_id)
    membership = GroupMembership.objects.get(group=group, user=member)
    membership.approved = True
    membership.approved_date = timezone.now()
    membership.save()

    return redirect('group_page', group_id=group_id)



@authentication_wrapper
def remove_member(request, group_id, user_id):
    context = initialize_context(request)
    group = Group.objects.get(id=group_id)
    context['group'] = group

    member = UserProfile.objects.get(id=user_id)
    membership = GroupMembership.objects.get(group=group, user=member)
    membership.delete()

    return redirect('group_page', group_id=group_id)


@authentication_wrapper
def delete_group(request, group_id):
    context = initialize_context(request)
    group = Group.objects.get(id=group_id)
    context['group'] = group

    if request.method == 'POST':
        group.delete()
        return redirect('pickup_groups')

    return render(request, 'pages/groups/delete_group.html', context)




@authentication_wrapper
def create_event_day(request, group_id):

    context = initialize_context(request)
    group = Group.objects.get(id=group_id)
    context['group'] = group

    event_form = GroupEventForm()
    context['form'] = event_form
    context['create'] = True

    if request.method == 'POST':
        event_form = GroupEventForm(request.POST)
        if event_form.is_valid():
            event_form.instance.group = group
            event_form.save()
            return redirect('group_page', group_id=group_id)
        else:
            context['form'] = event_form
            render(request, 'pages/events/event_day_form.html', context)

    return render(request, 'pages/events/event_day_form.html', context)



