from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

class User(AbstractUser):
    isSubscribed = models.BooleanField(default = False)

class API(models.Model):
    data = models.JSONField(null=False, default=dict)
    pointsteamlist = models.CharField(max_length = 500)
    updatetime = models.DateTimeField(auto_now=True, verbose_name="Updated at")

class myPrediction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    first = models.CharField(max_length=30)
    second = models.CharField(max_length=30)
    third = models.CharField(max_length=30)
    fourth = models.CharField(max_length=30)
    fifth = models.CharField(max_length=30)
    sixth = models.CharField(max_length=30)
    seventh	= models.CharField(max_length=30)
    eighth = models.CharField(max_length=30)
    ninth = models.CharField(max_length=30)
    tenth = models.CharField(max_length=30)
    eleventh = models.CharField(max_length=30)
    twelfth	= models.CharField(max_length=30)
    thirteenth = models.CharField(max_length=30)
    fourteenth = models.CharField(max_length=30)
    fifteenth = models.CharField(max_length=30)
    sixteenth = models.CharField(max_length=30)
    seventeenth	= models.CharField(max_length=30)
    eighteenth = models.CharField(max_length=30)
    nineteenth = models.CharField(max_length=30)
    twentieth = models.CharField(max_length=30)
    currentScore = models.IntegerField(default = 0)

class leagueList(models.Model):
    userManager = models.ForeignKey(User, on_delete=models.CASCADE, default=0)
    leagueName = models.CharField(max_length=30, unique=True)
    numbMembers = models.IntegerField(default=1)
    key = models.CharField(max_length = 6)

class leagueMember(models.Model):
    userid = models.ForeignKey(User, on_delete=models.CASCADE, default=0)
    user = models.CharField(max_length=30)
    leagueName = models.CharField(max_length=30)
    isManager = models.BooleanField(default = False)
    


