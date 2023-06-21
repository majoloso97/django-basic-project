import time
from datetime import datetime, timedelta
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from pytz import timezone
from .models import AdditionalUser, UpcomingCall
from .serializers import (UserSerializer,
                         GroupSerializer,UpdateUserFieldsSerializer,
                         UpcomingCallSerializer)
from .permissions import SuperUserOnlyPermission
from .utils import universal_notify


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated]


class UpcomingCallsViewSet(viewsets.ModelViewSet):
    """This is the Upcoming Calls endpoint."""

    serializer_class = UpcomingCallSerializer

    @staticmethod
    def _notify_upcoming_call_participants(coach, participants, upcoming_call):
        timestamp_dt = datetime.fromtimestamp(upcoming_call.timestamp/1000.0)
        default_time_zone = 'America/Denver'
        coach_time_zone = coach.time_zone if coach.time_zone else default_time_zone
        dt = timezone(coach_time_zone).localize(timestamp_dt)

        for _participant in participants:
            timestamp_dt = datetime.fromtimestamp(
                upcoming_call.timestamp/1000.0)
            
            participant = AdditionalUser.objects.get(id=_participant.id)
            tz = timezone(
                participant.time_zone if participant.time_zone else default_time_zone)
            aware_timestamp_dt = dt.astimezone(tz=tz)
            dt = aware_timestamp_dt
            signal_kwargs = {
                'notification_type': "INVITED_YOU_TO_UPCOMING_CALL",
                'upcoming_call': upcoming_call,
                "datetime": dt.strftime("%d %b, %Y, %I:%M %p"),
                "time_zone": tz.zone,
                "participant": participant
            }
            universal_notify(
                coach,
                recipient=participant,
                **signal_kwargs
            )

    def get_permissions(self):
        """Assign permissions based on action."""
        if self.action in ['user_upcoming_calls']:
            permissions = [IsAuthenticated]
        else:
            permissions = [IsAuthenticated,
                           SuperUserOnlyPermission]
        return [p() for p in permissions]

    def get_queryset(self):
        current_user = self.request.user
        return UpcomingCall.objects \
            .filter(user=current_user).order_by('-timestamp')

    def perform_create(self, serializer):
        request_user = self.request.user
        upcoming_call = serializer.save(user=request_user)
        current_user = AdditionalUser.objects.get(id=request_user.id)
        tz = self.request.data['time_zone']
        if current_user.time_zone != tz:
            user_profile = UpdateUserFieldsSerializer(current_user).data
            user_profile['time_zone'] = tz
            user_serializer = UpdateUserFieldsSerializer()
            user_serializer.update(current_user, user_profile)
        user = get_object_or_404(AdditionalUser, pk=current_user.id)
        self._notify_upcoming_call_participants(
            user, set(serializer.instance.participants.all()), serializer.instance)

    def list(self, serializer):
        """Get the upcoming calls for the current coach/admin """
        current_user = self.request.user
        ts = time.time()
        upcoming_calls = UpcomingCall.objects.filter(user=current_user).filter(Q(timestamp__gte=ts) | Q(recours_weekly=True)) \
            .order_by('-timestamp')
        serializer = UpcomingCallSerializer(upcoming_calls, many=True)
        data = serializer.data
        return Response(data)

    @action(detail=False, methods=['get'])
    def user_upcoming_calls(self, serializer):
        """Get current user upcoming calls where he appears as participant"""
        current_user = self.request.user
        ts = time.time()
        upcoming_calls = UpcomingCall.objects.filter(participants=current_user)\
            .filter(Q(timestamp__gte=ts) | Q(recours_weekly=True)) \
            .order_by('-timestamp')
        serializer = UpcomingCallSerializer(upcoming_calls, many=True)
        data = serializer.data
        return Response(data)

    @staticmethod
    def _send_reminder_15_minutes_before_call(coach, upcoming_call, participants):
        timestamp_dt = datetime.fromtimestamp(upcoming_call.timestamp/1000.0)
        default_time_zone = 'America/Denver'
        coach_time_zone = coach.time_zone if coach .time_zone else default_time_zone
        dt = timezone(coach_time_zone).localize(timestamp_dt)

        for participant in participants:
            timestamp_dt = datetime.fromtimestamp(
                upcoming_call.timestamp/1000.0)
            tz = timezone(
                participant.time_zone if participant.time_zone else default_time_zone)
            aware_timestamp_dt = dt.astimezone(tz=tz)
            dt = aware_timestamp_dt
            signal_kwargs = {
                'notification_type': 'REMINDER_UPCOMING_CALL',
                'upcoming_call': upcoming_call,
                "datetime": dt.strftime("%d %b, %Y, %I:%M %p"),
                "time_zone": tz.zone,
                "participant": participant
            }
        universal_notify(
            coach,
            recipient=participant,
            **signal_kwargs
        )

    @staticmethod
    def notify_15_minutes_before_call():
        """Send reminder to participants of upcoming calls 15 minutes before the call."""
        ts = time.time()
        upcoming_calls = UpcomingCall.objects.filter(Q(timestamp__gte=ts) | Q(recours_weekly=True)) \
            .order_by('-timestamp')

        for call in upcoming_calls:
            serializer = UpcomingCallSerializer(call)
            if call.recours_weekly:
                # Recalculate the date based on the day of the week.
                timestamp_dt = datetime.fromtimestamp(call.timestamp/1000.0)
                default_time_zone = 'America/Denver'
                coach_time_zone = call.user.time_zone if call.user.time_zone else default_time_zone
                time_zone = timezone(coach_time_zone)
                call_time = (timestamp_dt - timedelta(minutes=15)
                             ).strftime("%H:%M")
                call_dw = timestamp_dt.isoweekday()
                now = datetime.now(time_zone)
                now_dw = now.isoweekday()
                now_time = now.strftime("%H:%M")
                #print(f"dw call:{call_dw} dw today:{now_dw}, call time: {call_time} now time: {now_time}, timezone {time_zone}")
                if call_dw == now_dw and call_time == now_time:
                    # Send the notification for this week call
                    UpcomingCallsViewSet._send_reminder_15_minutes_before_call(
                        call.user, call, set(serializer.instance.participants.all()))

            else:
                # Filter the upcoming calls that are exactly 15 minutes prior to the call.
                timestamp_dt = datetime.fromtimestamp(call.timestamp/1000.0)
                default_time_zone = 'America/Denver'
                coach_time_zone = call.user.time_zone if call.user.time_zone else default_time_zone
                time_zone = timezone(coach_time_zone)
                call_time = (timestamp_dt - timedelta(minutes=15)
                             ).strftime("%H:%M")
                call_date = timestamp_dt.strftime("%m/%d/%y")
                now = datetime.now(time_zone)
                now_date = now.strftime("%m/%d/%y")
                now_time = now.strftime("%H:%M")

                if call_date == now_date and call_time == now_time:
                    # Send the notification for upcoming call
                    print('notification sent')
                    UpcomingCallsViewSet._send_reminder_15_minutes_before_call(
                        call.user, call, set(serializer.instance.participants.all()))
