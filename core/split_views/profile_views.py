from django.shortcuts import redirect, render
from django.utils import timezone
from ..forms import *
from django.contrib.auth import authenticate, login, logout
from ..helpers import authentication_wrapper, initialize_context
from ..models import *

@authentication_wrapper
def public_profile(request, username):
    context = initialize_context(request)
    user = UserProfile.objects.get(username=username)
    context['user'] = user
    return render(request, 'pages/profile/public_profile.html', context)

