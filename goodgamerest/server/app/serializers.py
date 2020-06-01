from rest_framework import serializers
from djoser.serializers import UserCreateSerializer, UserSerializer
from django.db import models
from .models import *
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password

class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value

class UserSimpleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'nationality']


class UserSerializer(serializers.HyperlinkedModelSerializer):
    parties = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    class Meta:
        model = User
        fields = ['id', 'username','password', 'nationality', 'parties']
        extra_kwargs = {'password': {'write_only': True, 'required': True}}

        def create(self, validated_data):
            validated_data['password'] = make_password(validated_data['password'])
            user = User.Objects.create_user(**validated_data)
            return user

        def update(self, instance, validated_data):
            instance.username = validated_data.get('username', instance.username)
            instance.save()

class BracketSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Bracket
        fields = ['number_of_players', 'score' ,  'date_added']


class MessageSerializer(serializers.HyperlinkedModelSerializer):
    user = UserSimpleSerializer( read_only=True)
    class Meta:
        model = Message
        fields = ['text' ,  'date_added', 'user']

class PartySerializer(serializers.HyperlinkedModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    number_of_users = serializers.SerializerMethodField()
    users = UserSimpleSerializer(many=True, read_only=True)

    def get_number_of_users(self, obj):
        return obj.users.all().count()

    class Meta:
        model = Party
        fields = ['id', 'name', 'date_added', 'language', 'max_users',
        'messages', 'game', 'platform', 'number_of_users', 'description', 'users']
        extra_kwargs = {
            'messages': {'required': False},
        }

class PartySimpleSerializer(serializers.HyperlinkedModelSerializer):
    number_of_users = serializers.SerializerMethodField()
    class Meta:
        model = Party
        fields = ['id', 'name', 'date_added', 'language', 'max_users', 'game', 'platform', 'number_of_users', 'description']

    def get_number_of_users(self, obj):
        return obj.users.all().count()
