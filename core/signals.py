from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import *  # Replace YourModel with the model you're monitoring

@receiver(post_save, sender=GroupScheduleEvent)
@receiver(post_save, sender=GroupEventAttendance)
@receiver(post_save, sender=GroupEventComments)
def create_group_notification(sender, instance, created, **kwargs):
    if created:  # Only create notifications for new instances

        if sender == GroupScheduleEvent:
            group_members = GroupMembership.objects.filter(group=instance.group)

        elif sender == GroupEventAttendance:
            group_members = GroupMembership.objects.filter(group=instance.event.group)

        elif sender == GroupEventComments:
            group_members = GroupMembership.objects.filter(group=instance.event.group)

        for member in group_members:
            message = f"A new {instance.__class__.__name__} has been added: {instance}" # Customize message
            UserNotifications.objects.create(
                user=member.user,
                message=message,
                related_object_type=instance.__class__.__name__,
                related_object_id=instance.pk
            )

