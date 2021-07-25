from django.core.management.base import BaseCommand, CommandError
from predict.models import User, myPrediction, leagueList, leagueMember
from predict_game.settings import EMAIL_HOST_USER
from django.core.mail import send_mail, send_mass_mail
from django.core.mail import get_connection, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

import os
import http.client
import json
import smtplib, ssl
import math
import datetime

class Command(BaseCommand):
    help = 'Send the monthly email'
    # Make an API call to ensure latest data is used
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

        # Filter to only recipients who are subscribed
        recipients = User.objects.filter(isSubscribed = True)
        # Get the current month and year for the update subject line
        mydate = datetime.datetime.now()
        month = mydate.strftime("%B")   
        year = datetime.datetime.now().year
        subject = f"{month} {year} Update"
        
        # Use a list to collect the necesarry mailing info
        mailinfo = []
        # Loop through the recipients list to make their emails
        for r in recipients:
            # Collect their prediction/user data
            predictions = myPrediction.objects.filter(user = r.id)
            name = r.username
            if predictions:
                predictionsfilter = myPrediction.objects.filter(user = r.id).values_list('first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eighth', 'ninth', 'tenth', 'eleventh', 'twelfth', 'thirteenth', 'fourteenth', 'fifteenth', 'sixteenth', 'seventeenth', 'eighteenth', 'nineteenth', 'twentieth')
                points = 0
                pointslog = []
                correct = []
                for x in range(20):
                    # User guessed the perfect score, 0 points recorded
                    if predictionsfilter[0][x] == pointsteamlist[x]:
                        pointslog.append(0)
                        correct.append(pointsteamlist[x])
                    # Calculate the difference between guess and actual score
                    else:
                    # Keep track of loop index
                        z = 0
                    # Loop through the list of teams
                        for y in pointsteamlist:
                            # If a match is found, calc difference and add to overall points, and append to the log of points
                            if y == predictionsfilter[0][x]:
                                dif = math.dist((x,), (z,))
                                pointslog.append(int(dif))
                                points += dif
                            else:
                            # Add to loop index
                                z += 1
                # Remove the .0 
                points = int(points)
                myPrediction.objects.filter(user = r.id).update(currentScore = points)
                # Find out the users worst prediction points score
                worst = []
                worstm = max(pointslog)
                # Get the position of that prediction
                worstp = pointslog.index(worstm)
                # Retrieve the team from that position
                worstteam = predictionsfilter[0][worstp]
                # Prepare the list for jinja
                worst.extend([worstm, worstteam])
            else:
                # Fixing weird heroku bug that needs variable defining
                pointslog = []
                worst = []
                correct = []
            # Find out if a user belongs to a league
            myLeagues = leagueMember.objects.filter(user = name).values_list('leagueName')
            # If they belong to another league, render extra html
            league = []
            if myLeagues:
                emptydict = {}
                participants = leagueMember.objects.filter(leagueName__in = myLeagues).values_list('user')
                # Find out the participants user ids
                ids = User.objects.filter(username__in = participants).values('id')
                for x in User.objects.filter(username__in = participants):
                    for y in myPrediction.objects.filter(user = x.id):
                        emptydict[y.currentScore] = x.username, x.id
                        #emptylist.append(p.user)
                # Reorder the dict by their key
                items = emptydict.items()
                league = sorted(items)
            # Make the message in html
            html_message = render_to_string('predict/monthly.html', {
                'predictions': predictions,
                'name': name,
                'pointslog': pointslog,
                'leagues': league,
                'worst': worst,
                'correct': correct})
            # Store as plain message in case old email system is used
            plain_message = strip_tags(html_message)
            
            # Append all the info to the list with extra [] so the next email will be seperated
            mailinfo.extend([[ subject, plain_message, html_message, EMAIL_HOST_USER, [r.email] ]])
        
        messages = []
        for subject, text, html, from_email, recipient in mailinfo:
            message = EmailMultiAlternatives(subject, text, from_email, recipient)
            message.attach_alternative(html, 'text/html')
            messages.append(message)
        # Send the emails only making one call to the server
        get_connection(fail_silently = False).send_messages(messages)

        #DONT USEsend_mass_mail(mailinfo, fail_silently = False)
        
        def handle(self, *args, **options):
            recipients = User.objects.filter(isSubscribed = True)
            # Count out how many there are
            recipients_size = len(recipients)
            # Return success message
            self.stdout.write(self.style.SUCCESS('Successfully sent %i emails' % recipients_size))
    else:
        # Notify myself via email that it was not successful
        email = EMAIL_HOST_USER
        recepient = EMAIL_HOST_USER
        subject = "Monthly emails have failed"
        message = str(response)
        send_mail(subject, message, EMAIL_HOST_USER, [recepient], fail_silently = False)
        def handle(self, *args, **options):
            # Return unsuccessful message
            self.stdout.write(self.style.ERROR(f'Monthly email failed'))