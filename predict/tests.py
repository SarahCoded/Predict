from django.test import TestCase
from django.contrib import auth
import http.client, os, json
from .models import User, myPrediction, leagueList, leagueMember, API

# Create your tests here.
class UserTestCase(TestCase):
    def setUp(self):
        # Create user and log in
        self.user = User.objects.create_user(username='testuser', password='12345')
        login = self.client.login(username='testuser', password='12345')
        # Create API data
        connection = http.client.HTTPSConnection('api.football-data.org')
        myAPI = os.environ.get('myAPI')
        headers = { 'X-Auth-Token': myAPI }
        connection.request('GET', '/v2/competitions/PL/standings', None, headers )
        # Receive the json response
        response = json.loads(connection.getresponse().read().decode())
        teams = []
        # Declare a team array for points calc
        pointsteamlist = []
        # Loop over 20 times as there are 20 teams in the league
        for x in range(20):
            team = {}
            team["position"] = x + 1
            team["name"] = response["standings"][0]["table"][x]["team"]["name"]
            team["points"] = response["standings"][0]["table"][x]["points"]
            p = response["standings"][0]["table"][x]["team"]["name"]
            teams.append(team)
            pointsteamlist.append(p)
            API.objects.create(data = teams, pointsteamlist = pointsteamlist)
        # Create dummy predictions
        myPrediction.objects.create(user = self.user)
        
    def test_login(self):
        user = auth.get_user(self.client)
        assert user.is_authenticated
    
    def test_predictions(self):
        user = self.client
        response = user.get(f"/user/{self.user.id}/{self.user.username}")
        self.assertEqual(response.status_code, 200)