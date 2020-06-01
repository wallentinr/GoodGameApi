from django.db import models
from django.contrib.auth.models import AbstractUser
from rest_framework import serializers



class Party(models.Model):
    name = models.CharField(max_length=100)
    date_added = models.DateTimeField(auto_now_add=True)
    language = models.CharField(max_length=100)
    game = models.CharField(max_length=100)
    platform = models.CharField(max_length=100)
    max_users = models.IntegerField(default=20)
    description = models.CharField(max_length=1000)
    REQUIRED_FIELDS = ['name', 'max_users']

    def __str__(self):
        return self.name


class User(AbstractUser):
    username = models.CharField(max_length=100, unique=True)
    nationality = models.CharField(max_length=100)
    resent_logged_in = models.DateTimeField(auto_now_add=True)
    date_added = models.DateTimeField(auto_now_add=True)
    parties = models.ManyToManyField(Party, related_name='users')

    REQUIRED_FIELDS = ['nationality']
    USERNAME_FIELD = 'username'

    def get_username(self):
        return self.username

    def __str__(self):
        return self.username

class Message(models.Model):
    party = models.ForeignKey(Party, related_name='messages', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='messages',null=True, on_delete=models.SET_NULL)
    date_added = models.DateTimeField(auto_now_add=True)
    text = models.CharField(max_length=300)

    def __str__(self):
        return self.text




class Bracket(models.Model):
    name = models.CharField(max_length=100)
    numbers_of_players = models.IntegerField()
    score = models.CharField(max_length=100)
    date_added = models.DateTimeField(auto_now_add=True)
     
    def __str__(self):
        return self.name


