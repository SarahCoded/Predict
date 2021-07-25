from django.contrib import admin
from .models import User, myPrediction, leagueList, leagueMember, API

# Register your models here.
admin.site.register(User)
admin.site.register(myPrediction)
admin.site.register(leagueList)
admin.site.register(leagueMember)

# View timestamp in admin for API model
class APIadmin(admin.ModelAdmin):
    list_display = ('updatetime',)
admin.site.register(API, APIadmin)