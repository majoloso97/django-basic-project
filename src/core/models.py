from django.contrib.auth.models import User
from django.db import models


class AdditionalUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    time_zone = models.TextField(blank=True, null=True)
    coach = models.ManyToManyField('self',
                                   related_name='students',
                                   symmetrical=False,
                                   blank=True)


# Create your models here.
class UpcomingCall(models.Model):
    """Upcoming Calls Model"""
    call_name = models.CharField(
        "Call Name", max_length=255, help_text="Name of the upcoming call")
    user = models.ForeignKey(User, related_name='+', on_delete=models.CASCADE,
                             help_text="User that created the upcoming call")
    participants = models.ManyToManyField(
        User, related_name='+', help_text="Users attending the upcoming call")
    timestamp = models.BigIntegerField()
    meeting_link = models.CharField(
        max_length=500, default='', help_text="Meeting Link (Zoom)")
    recours_weekly = models.BooleanField(
        default=False, help_text="Determine if the upcoming call should be recurring for every week")

    def __str__(self):
        return self.call_name
