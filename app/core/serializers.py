from django.contrib.auth.models import User, Group
from rest_framework import serializers
from .models import UpcomingCall


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['id',
                  'username',
                  'first_name',
                  'last_name',
                  'email',
                  'groups']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['name']


class UpdateUserFieldsSerializer(serializers.Serializer):
    time_zone = serializers.CharField(max_length=100)

    def update(self, instance, validated_data):
        instance.time_zone = validated_data.get(
            'time_zone', instance.time_zone)
        instance.save()
        return instance


class UpcomingCallSerializer(serializers.ModelSerializer):
    """Upcoming Call Serializer."""

    class Meta:
        model = UpcomingCall
        fields = [ 'id', 'call_name', 'timestamp', 'participants', 'meeting_link', 'recours_weekly' ]


    def validate(self, data):
        """Check that at least one participant is required."""
        try:
            if len(data['participants']) == 0:
                raise serializers.ValidationError("At least one participant is required")
            return data 
        except KeyError as ex:
            raise serializers.ValidationError("At least one participant is required")
           