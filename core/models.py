import datetime
from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


#  Default UserProfile model: 
class UserProfile(AbstractUser):
    score = models.IntegerField(default=0)
    city = models.CharField(max_length=200, blank=True)
    state = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.username
    
    def get_my_groups(self):
        groups = GroupMembership.objects.filter(user=self, approved=True)
        return groups

    
    def get_my_managed_groups(self):
        groups = Group.objects.filter(organizer=self)
        return groups
    

    def public_user_groups_joined(self):
        groups = GroupMembership.objects.filter(user=self, approved=True, group__public=True)
        return groups

    def get_my_group_events(self):
        my_groups = GroupMembership.objects.filter(user=self, approved=True)
        
        events = []
        for group in my_groups:
            events += GroupScheduleEvent.objects.filter(group=group.group)
        return events


    def get_my_group_games(self):
        my_groups = GroupMembership.objects.filter(user=self, approved=True)
        
        games = []
        for group in my_groups:
            games += Game.objects.filter(group=group.group)
        return games
    
    def get_approval_requests_from_groups_managed(self):
        groups_managed = Group.objects.filter(organizer=self)
        approval_requests = GroupMembership.objects.filter(group__in=groups_managed, approved=False)
        return approval_requests
    
    def get_all_notifications(self):
        notifications = UserNotifications.objects.filter(user=self)
        return notifications
    
    def get_unread_notifications(self):
        notifications = UserNotifications.objects.filter(user=self, is_read=False)
        return notifications
    
    



class UserNotifications(models.Model):
    
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)  # The notification text
    related_object_type = models.CharField(max_length=255, blank=True, null=True) # e.g., 'Product', 'Order'
    related_object_id = models.PositiveIntegerField(blank=True, null=True) # The ID of the related object
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at'] # Show newest notifications first

    def __str__(self):
        return self.message
    
 

class GroupMembership(models.Model):
    group = models.ForeignKey('Group', on_delete=models.CASCADE)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    is_organizer = models.BooleanField(default=False)

    approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(UserProfile, related_name='approved_memberships', on_delete=models.CASCADE, null=True, blank=True)
    approved_date = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} in {self.group.name}"

    class Meta: 
        unique_together = ('group', 'user')
    


class Sports(models.Model):
    sport = models.CharField(max_length=200)

    def __str__(self):
        return self.sport



# Group Model: 
class Group(models.Model):

    competetive_level_choices = [
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Open', 'Open'),
        ('Professional', 'Professional'),
    ]


    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    organizer = models.ForeignKey(UserProfile, related_name='organized_groups', on_delete=models.SET_NULL, null=True)
    # members = models.ManyToManyField(UserProfile, related_name='joined_groups', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    sport = models.ForeignKey(Sports, related_name='sport_type', on_delete=models.RESTRICT, null=True)
    competetive_level = models.CharField(max_length=200, choices=competetive_level_choices, default='Open')
        
    public = models.BooleanField(default=True)
    active = models.BooleanField(default=True)


    # need to add location for the group and where the games are played
    city = models.CharField(max_length=200, blank=True)
    state = models.CharField(max_length=200, blank=True)
    zip_code = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.name


    def get_members(self):
        group_members = GroupMembership.objects.filter(group=self, approved=True)
        return group_members
    
    def get_member_count(self):
        member_count = GroupMembership.objects.filter(group=self, approved=True).count()
        return member_count

    def get_scheduled_events(self):
        events = GroupScheduleEvent.objects.filter(group=self)
        return events
    

    def get_upcoming_schedule_events(self):
        today = datetime.date.today()
        events = GroupScheduleEvent.objects.filter(group=self, date__gte=today)
        return events
    

    def previous_scheduled_events(self):
        today = datetime.date.today()
        events = GroupScheduleEvent.objects.filter(group=self, date__lt=today)
        return events


    


class GroupScheduleEvent(models.Model):

    status_choices = [
        ('Pending', 'Pending'),
        ('Scheduled', 'Scheduled'),
        ('Completed', 'Completed'),
        ('Canceled', 'Canceled'),
    ]



    group = models.ForeignKey(Group, related_name='events', on_delete=models.CASCADE)
    
    date = models.DateField(default=None, null=True)
    location = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)
    team_size = models.IntegerField(default=0)
    max_participants = models.IntegerField(default=0)

    game_duration = models.IntegerField(default=0)


    status = models.CharField(max_length=200, choices=status_choices, default='Pending')

    # Soft delete field
    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True)
    deleted_by = models.ForeignKey(UserProfile, related_name='deleted_events', on_delete=models.SET_NULL, null=True)
    




    def __str__(self):
        return f"{self.group.name} event on {self.date.strftime('%Y-%m-%d')} Players ({self.get_rsvp_count()}/{self.max_participants})"


    def get_rsvp_count(self):
        rsvp_count = GroupEventAttendance.objects.filter(event=self, attending=True).count()
        return rsvp_count


    def is_joinable(self):
        if self.get_rsvp_count() < self.max_participants:
            return True
        return False


    def get_attendees(self):
        attendees = GroupEventAttendance.objects.filter(event=self, attending=True)
        return attendees


    def order_players_by_score(self):
        players = GroupEventAttendance.objects.filter(event=self, attending=True).order_by('user__score')
        return players



class GroupEventAttendance(models.Model):
    event = models.ForeignKey(GroupScheduleEvent, on_delete=models.CASCADE)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    attending = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} attending {self.event.group.name} event on {self.event.date.strftime('%Y-%m-%d')}"
    class Meta: 
        unique_together = ('event', 'user')


class GroupEventComments(models.Model):
    event = models.ForeignKey(GroupScheduleEvent, on_delete=models.CASCADE)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} commented on {self.event.group.name} event on {self.event.date.strftime('%Y-%m-%d')}"


# class ScheduledGame(models.Model):
#     event = models.ForeignKey(GroupScheduleEvent, on_delete=models.CASCADE)
#     game = models.ForeignKey('Game', on_delete=models.CASCADE)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Game in {self.event.group.name} event on {self.event.date.strftime('%Y-%m-%d')}"


class Game(models.Model):
    event = models.ForeignKey(GroupScheduleEvent, on_delete=models.CASCADE, null=True)
    group = models.ForeignKey(Group, related_name='games', on_delete=models.CASCADE)
    date_time = models.DateTimeField()
    location = models.CharField(max_length=200, blank=True) # Or use a more structured location model
    teams = models.ManyToManyField(UserProfile, through='TeamAssignment', related_name='game_participations')
    winning_team = models.CharField(max_length=10, blank=True, null=True) # e.g., 'Team A', 'Team B' - consider enums for better structure
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Game in {self.group.name} on {self.date_time.strftime('%Y-%m-%d %H:%M')}"


class TeamAssignment(models.Model):
    team_name_choices = [
        ('Team A', 'Team A'),
        ('Team B', 'Team B'),
    ]


    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    team_name = models.CharField(max_length=10, choices=team_name_choices) # e.g., 'Team A', 'Team B'

    def __str__(self):
        return f"{self.user.username} in {self.game.group.name} game on {self.game.date_time.strftime('%Y-%m-%d %H:%M')}"
    






    

