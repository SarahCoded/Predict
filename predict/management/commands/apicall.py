from django.core.management.base import BaseCommand, CommandError
from predict_game.settings import EMAIL_HOST_USER
from django.core.mail import send_mail, send_mass_mail
from django.core.mail import get_connection, EmailMultiAlternatives
from predict.models import User, myPrediction, leagueList, leagueMember, API
import http.client, os, json, requests

class Command(BaseCommand):
    help = 'Make an API call to get football data'
    # Had to change HTTPS to HTTP to work one morning
    connection = http.client.HTTPSConnection('api.football-data.org')
    myAPI = os.environ.get('myAPI')
    headers = { 'X-Auth-Token': myAPI }
    connection.request('GET', '/v2/competitions/PL/standings', None, headers )
    # Receive the json response
    response = json.loads(connection.getresponse().read().decode())
    # Only continue if an error is not presented
    if not 'error' in response:
        teams = []
        # Declare a team array for points calc
        pointsteamlist = []
        # Loop over 20 times as there are 20 teams in the league
        for x in range(20):
            team = {}
            team["position"] = x + 1
            team["name"] = response["standings"][0]["table"][x]["team"]["name"][:-3]# Remove FC
            team["points"] = response["standings"][0]["table"][x]["points"]
            p = response["standings"][0]["table"][x]["team"]["name"][:-3]# Remove FC
            teams.append(team)
            pointsteamlist.append(p)
        data = API.objects.all()
        
        if not data:
            API.objects.create(data = teams, pointsteamlist = pointsteamlist)
        else:
            # Use the save method to ensure actual time is updated
            obj = API.objects.first()
            obj.data = teams
            obj.pointsteamlist = pointsteamlist
            obj.save()
            #API.objects.update(data = teams, pointsteamlist = pointsteamlist)
        def handle(self, *args, **options):
            time = API.objects.first()
            # Return success message
            self.stdout.write(self.style.SUCCESS(f'Updated the API at {time.updatetime}'))
    else:
        # Notify myself via email that it was not successful
        email = EMAIL_HOST_USER
        recepient = EMAIL_HOST_USER
        subject = "API update failed"
        message = str(response)
        send_mail(subject, message, EMAIL_HOST_USER, [recepient], fail_silently = False)
        def handle(self, *args, **options):
            # Return unsuccessful message
            self.stdout.write(self.style.ERROR(f'Update failed'))
    
