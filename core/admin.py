from django.contrib import admin
from .models import * 
# Register your models here.


admin.site.register(Group)
admin.site.register(Sports)

admin.site.register(GroupEventComments)


# admin.site.register(ScheduledGame)
admin.site.register(Game)
admin.site.register(TeamAssignment)



@admin.register(GroupScheduleEvent)
class GroupScheduleEventAdmin(admin.ModelAdmin):
    list_display = ('group', 'date', 'start_time', 'end_time', 'location', 'max_participants', 'team_size')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'score', 'city', 'state')

@admin.register(GroupMembership)
class GroupMembershipAdmin(admin.ModelAdmin):
    list_display = ('group', 'user', 'approved', 'is_organizer', 'approved_date')


@admin.register(GroupEventAttendance)
class GroupEventAttendanceAdmin(admin.ModelAdmin):
    list_display = ('event', 'user', 'attending', 'created_at')