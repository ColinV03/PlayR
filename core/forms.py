from .models import *
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ModelForm

class UserForm(UserCreationForm):
    class Meta:
        model = UserProfile
        fields = ['username', 'email', 'password1', 'password2']


    def clean_username(self):
        username = self.cleaned_data['username']
        if UserProfile.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists.")
        # Add other username validation if needed (length, allowed characters, etc.)
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if UserProfile.objects.filter(email=email).exists():
            raise forms.ValidationError("Email address already exists.")
        return email

    def clean(self):  # For cross-field validation (e.g., password matching)
        cleaned_data = super().clean()  # Call the parent's clean method
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Passwords do not match.")

        return cleaned_data



class ProfileForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name']


class UserLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class GroupForm(ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'description']

class GameForm(ModelForm):
    class Meta:
        model = Game
        fields = ['date_time', 'location']

class TeamAssignmentForm(ModelForm):
    class Meta:
        model = TeamAssignment
        fields = ['team_name']



class GroupCreationForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'description', 'sport', 'competetive_level', 'public', 'active', 'city', 'state', 'zip_code']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}), # Adjust rows for textarea
        }
        help_texts = {
            'public': 'Public groups are visible to everyone. Private groups are invite-only.',
            'active': 'Inactive groups are hidden from general listings.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # You can customize form fields here if needed, e.g., add placeholders
        self.fields['name'].widget.attrs.update({'placeholder': 'Enter group name'})
        self.fields['city'].widget.attrs.update({'placeholder': 'City'})
        self.fields['state'].widget.attrs.update({'placeholder': 'State'})
        self.fields['zip_code'].widget.attrs.update({'placeholder': 'Zip Code'})



# class GroupEventForm(forms.ModelForm):
#     date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'})) # HTML5 date input
#     start_time = forms.TimeField(widget=forms.DateTimeInput()) # HTML5 time input
#     end_time = forms.TimeField(widget=forms.DateTimeInput(), required=False) # End time optional

#     class Meta:
#         model = GroupScheduleEvent
#         fields = ['date', 'start_time', 'end_time', 'location', 'description', 'max_participants']
#         widgets = {
#             'description': forms.Textarea(attrs={'rows': 2}), # Adjust rows for textarea
#             'max_participants': forms.NumberInput(attrs={'min': 0}), # Ensure min participants is 0
#         }
#         help_texts = {
#             'max_participants': 'Set to 0 for unlimited participants.',
#         }

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # Customize form fields here, e.g., placeholders
#         self.fields['location'].widget.attrs.update({'placeholder': 'Enter location'})
#         self.fields['description'].widget.attrs.update({'placeholder': 'Brief event description (optional)'})
#         # Make 'end_time' optional in the form label as well
#         self.fields['end_time'].label = 'End Time (Optional)'
class GroupEventForm(forms.ModelForm):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'})) # HTML5 date input
    
    
    start_time = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})) # HTML5 datetime-local input
    end_time = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}), required=False) # End datetime optional

    class Meta:
        model = GroupScheduleEvent
        fields = [ 
            'date',
             'start_time',
             'end_time',
             'location',
             'description',
             'max_participants',
             'team_size',
             'game_duration',
             ] # Removed date, start_time, end_time; Added start_datetime, end_time
        widgets = {
            'description': forms.Textarea(attrs={'rows': 2}), # Adjust rows for textarea
            'max_participants': forms.NumberInput(attrs={'min': 0}), # Ensure min participants is 0
            'team_size': forms.NumberInput(attrs={'min': 0}), # Ensure min team
        }
        labels = {
            'start_time': 'Start Date and Time', # More descriptive label
            'end_time': 'End Date and Time (Optional)', # More descriptive and indicate optional
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize form fields here, e.g., placeholders
        self.fields['location'].widget.attrs.update({'placeholder': 'Enter location'})
        self.fields['description'].widget.attrs.update({'placeholder': 'Brief event description (optional)'})



class GroupEventAttendanceForm(forms.ModelForm):
    class Meta:
        model = GroupEventAttendance
        fields = ['attending']
        widgets = {
            'attending': forms.RadioSelect(choices=((True, 'Yes, I will attend'), (False, 'No, I cannot attend'))),
        }
        labels = {
            'attending': 'Will you be attending this event?',
        }
