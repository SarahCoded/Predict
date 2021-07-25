from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import render
from django.urls import reverse
from predict_game.settings import EMAIL_HOST_USER
from django.core.mail import send_mail, send_mass_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from jinja2 import Template

import datetime, os, http.client, json, smtplib, ssl, math, numpy, ast

from .models import User, myPrediction, leagueList, leagueMember, API

# Create your views here.
def index(request):
    # Retrieve a list of the teams in order in the table
    teamlist = API.objects.all().values_list('pointsteamlist')
    # First, loop to force it into a list
    for p in teamlist:
        new = list(p)
    # Do another loop as it thinks there is only one item in the list
    for n in new:
        nn = n
    # Convert from a string to a list
    pointsteamlist = ast.literal_eval(nn)
    
    # Return if user is not logged in
    api = API.objects.all()
    if not request.user.is_authenticated:
        return render(request, "predict/index.html", {
            "teams": pointsteamlist,
            "api": api
        })
    # Find out the user's username as they are logged in
    user = User.objects.get(username = request.user)
    # Calculate points if user has submitted predictions and season has started
    predictions = myPrediction.objects.filter(user = user)
    if predictions:
        # Get the current time in unix
        unixtime = int(datetime.datetime.now().timestamp())
        # If the season hasn't started yet (before 13/08/21), show a different page
        if not unixtime > 1628852400:
            return render (request, "predict/pre.html", {
                "predictions": predictions
            })
        # The season has started so calculate the user's points
        predictionsfilter = myPrediction.objects.filter(user = user).values_list('first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eighth', 'ninth', 'tenth', 'eleventh', 'twelfth', 'thirteenth', 'fourteenth', 'fifteenth', 'sixteenth', 'seventeenth', 'eighteenth', 'nineteenth', 'twentieth')
        points = 0
        pointslog = []
        for x in range(20):
            # User guessed the perfect score, 0 points recorded
            if predictionsfilter[0][x] == pointsteamlist[x]:
                pointslog.append(0)
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
        
        # Update the user's current score
        myPrediction.objects.filter(user = user).update(currentScore = points)
        predictions = myPrediction.objects.filter(user = user)
        
        # Return with their predictions with scores, and current standings
        return render(request, "predict/index.html", {
            "teams": pointsteamlist,
            "predictions": predictions,
            "pointslog": pointslog,
            "api": api
        })
    # If user has just submitted their predictions, add form to db
    elif request.method == 'POST':
        # Get predictions from the form
        team1 = request.POST.get("team1")
        team2 = request.POST.get("team2")
        team3 = request.POST.get("team3")
        team4 = request.POST.get("team4")
        team5 = request.POST.get("team5")
        team6 = request.POST.get("team6")
        team7 = request.POST.get("team7")
        team8 = request.POST.get("team8")
        team9 = request.POST.get("team9")
        team10 = request.POST.get("team10")
        team11 = request.POST.get("team11")
        team12 = request.POST.get("team12")
        team13 = request.POST.get("team13")
        team14 = request.POST.get("team14")
        team15 = request.POST.get("team15")
        team16 = request.POST.get("team16")
        team17 = request.POST.get("team17")
        team18 = request.POST.get("team18")
        team19 = request.POST.get("team19")
        team20 = request.POST.get("team20")
        
        # Add prediction to the database
        myPrediction.objects.create(
        user = user,
        first = team1, 
        second = team2,
        third = team3,
        fourth = team4,
        fifth = team5,
        sixth = team6,
        seventh = team7,
        eighth = team8,
        ninth = team9,
        tenth = team10,
        eleventh = team11,
        twelfth = team12,
        thirteenth = team13,
        fourteenth = team14,
        fifteenth = team15,
        sixteenth = team16,
        seventeenth = team17,
        eighteenth = team18,
        nineteenth = team19,
        twentieth = team20
        )
    # Redirect to the index homepage to calculate points
        return HttpResponseRedirect(reverse("index"))
    else:
        # User is logged in but hasn't submitted a prediction yet
        return render(request, "predict/index.html", {
            "teams": pointsteamlist,
            "api": api
        })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        
        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "predict/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "predict/login.html")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "predict/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "predict/register.html", {
                "message": "Username already taken."
            })
        login(request, user)

        # Send a welcome email
        user = User.objects.get(username = request.user)
        email = user.email
        recepient = email
        subject = "Welcome to Predict the League"

        # Work out whether they want monthly updates or not
        subscribe = request.POST.get("subscribe")
        if subscribe == 'on':
            html_message = render_to_string('predict/welcomemail.html', {"username": username})
            # Update the database (set as false by default)
            User.objects.filter(username = username).update(isSubscribed = True)
        else:
            html_message = render_to_string('predict/welcomemailnosub.html', {"username": username})
        # Store as plain message in case old email system is used
        plain_message = strip_tags(html_message)
        # Send the email
        send_mail(subject, plain_message, EMAIL_HOST_USER, [recepient], fail_silently = False, html_message=html_message)
        # Redirect user to homepage with user logged in
        return HttpResponseRedirect(reverse("index")
        )
    else:
        return render(request, "predict/register.html")

@login_required
def create(request):
    user = User.objects.get(username = request.user)
    # Check if user has made predictions yet
    predictions = myPrediction.objects.filter(user = user)
    return render(request, "predict/create.html", {
        "predictions": predictions
    })

@login_required
def myleagues(request):
    user = User.objects.get(username = request.user)
    predictions = myPrediction.objects.filter(user = user)
    if request.method == 'POST':
        # Add the new league to the database
        cleaguename = request.POST.get("leaguename")
        key = request.POST.get("randomkey")
        
        # Make sure leaguename/pin is not blank
        if cleaguename == "":
            messages.error(request, "Please enter a league name")
            return HttpResponseRedirect("create")
        elif key == "":
            messages.error(request, "Please generate a key")
            return HttpResponseRedirect("create")
        # Make sure league name is not already taken when adding to database
        try:
            league = leagueList.objects.create(userManager = user, leagueName = cleaguename, key = key)
            league.save()
        except IntegrityError:
            messages.error(request, "League name already taken")
            return HttpResponseRedirect("create")
        # Add info to second db
        leagueMember.objects.create(userid = user, user = user, leagueName = cleaguename, isManager = True)
        # Successfully redirect user
        messages.success(request, f"League {cleaguename} has been successfully created")
        return HttpResponseRedirect("myleagues")
    # Get info on the user's joined leagues information
    else:
        myleaguenames = leagueMember.objects.filter(user = user).values_list('leagueName')
        leagueinfo = leagueList.objects.filter(leagueName__in = myleaguenames)
        return render(request, "predict/myleagues.html", {
            "leagueinfo": leagueinfo
        })

@login_required
def join(request):
    user = User.objects.get(username = request.user)
    # Check if user has made predictions yet
    predictions = myPrediction.objects.filter(user = user)
    if request.method == "POST":
        # Find out what pin the user has entered
        formkey = request.POST.get("key")
        user = User.objects.get(username = request.user)
        # Loop over the current keys in the database to see if theres a match
        for k in leagueList.objects.all():
            if k.key == formkey:
                # Make sure the user is not entering their own league
                if k.userManager == user:
                    messages.error(request, f"You are already a member of the {k.leagueName} League, as you created it!")
                    return HttpResponseRedirect("join")
                # Check user is not a member of the league already
                for l in leagueMember.objects.all():
                    if l.user == str(user) and l.leagueName == k.leagueName:
                        messages.error(request, f"You have already joined {k.leagueName} League.")
                        return HttpResponseRedirect("join")
                # Let user join the league as checks have all passed
                # Loop over the query set to add a member
                for n in leagueList.objects.filter(key = k.key):
                    leagueList.objects.filter(key = k.key).update(numbMembers = int(n.numbMembers) + 1)
                # Add a league member to the other table
                leagueMember.objects.create(userid = user, user = user, leagueName = k.leagueName)
                # Return success and redirect to myleagues view
                messages.success(request, f"You have successfully joined {k.leagueName}")
                return HttpResponseRedirect("myleagues")
        # Else key is not valid so let the user know
        else:
            messages.error(request, "Sorry, this is not a valid key")
            return HttpResponseRedirect("join")
    # Return original form
    return render(request, "predict/join.html", {
        "leagues": leagueList.objects.all(),
        "predictions": predictions
    })

@login_required
def friendtable(request):
    # Request made using get
    # Find out what league the user wants to see, and who is in that league
    username = User.objects.get(username = request.user)
    leaguename = request.GET.get("league")
    participants = leagueMember.objects.filter(leagueName = leaguename).values('user')
    # Get the current time in unix
    unixtime = int(datetime.datetime.now().timestamp())
    # If the season hasn't started yet, show a different page
    if not unixtime > 1628852400:
        participants = User.objects.filter(username__in = participants)
        info = leagueList.objects.filter(leagueName = leaguename)
        return render (request, "predict/prefriendtable.html", {
            "participants": participants,
            "leaguename": leaguename,
            "info": info
        }) 
    # Season started, so update the points for each member in the league
    # Retrieve a list of the teams in order in the table
    teamlist = API.objects.all().values_list('pointsteamlist')
    # First, loop to force it into a list
    for p in teamlist:
        new = list(p)
    # Do another loop as it thinks there is only one item in the list
    for n in new:
        nn = n
    # Convert from a string to a list
    pointsteamlist = ast.literal_eval(nn)
    # Find out the participants user ids
    ids = User.objects.filter(username__in = participants).values('id')
    predictions = myPrediction.objects.filter(user__in = ids)
    # Get the predictions from the users
    predictionsfilter = myPrediction.objects.filter(user__in = ids).values_list('first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eighth', 'ninth', 'tenth', 'eleventh', 'twelfth', 'thirteenth', 'fourteenth', 'fifteenth', 'sixteenth', 'seventeenth', 'eighteenth', 'nineteenth', 'twentieth', 'user')
    # Set an integeer to ensure all the users are looped through
    qq = 0
    for q in predictionsfilter:
        points = 0
        pointslog = []
        for x in range(20):
            # User guessed the perfect score, 0 points recorded
            if predictionsfilter[qq][x] == pointsteamlist[x]:
                pointslog.append(0)
            # Calculate the difference between guess and actual score
            else:
            # Keep track of loop index
                z = 0
            # Loop through the list of teams
                for y in pointsteamlist:
                    # If a match is found, calc difference and add to overall points, and append to the log of points
                    if y == predictionsfilter[qq][x]:
                        dif = math.dist((x,), (z,))
                        pointslog.append(int(dif))
                        points += dif
                    else:
                    # Add to loop index
                        z += 1      
        # Remove the .0 
        points = int(points)
        # Update the user's current score
        myPrediction.objects.filter(user = predictionsfilter[qq][x+1]).update(currentScore = points)
        # Increase by one as the loop has ended for one user, and the next user is abbout to get points tallied
        qq += 1    
    # Now order the users by prediction points.
    emptydict = {}
    for x in User.objects.filter(username__in = participants):
        for y in myPrediction.objects.filter(user = x.id):
            emptydict[x.username] = y.currentScore, x.id
    # Sort the dict by the first key so duplicate scores are not removed
    league = dict(sorted(emptydict.items(), key=lambda item: item[1]))
    # Find out if there are any users on the same number of points
    drawlist = []
    for key in league:
        drawlist.append(league[key][0])
    # Remove the unique values from drawlist that won't tie, to pass on to jinja
    drawlist = set(i for i in drawlist if drawlist.count(i) > 1)
    # Pull the league info from db
    info = leagueList.objects.filter(leagueName = leaguename)
    # Return the relevant info
    return render(request, "predict/friendtable.html", {
        "leagues": league,
        "leaguename": leaguename,
        "info": info,
        "drawlist": drawlist
    })

@login_required
def user(request, id, name):
    # Get up to date list from the api model
    # Retrieve a list of the teams in order in the PL table
    teamlist = API.objects.all().values_list('pointsteamlist')
    # First, loop to force it into a list
    for p in teamlist:
        new = list(p)
    # Do another loop as it thinks there is only one item in the list
    for n in new:
        nn = n
    # Convert from a string to a list
    pointsteamlist = ast.literal_eval(nn)
    
    # Get the user from url address
    user = User.objects.get(username = name)
    # Calculate points if user has submitted predictions
    predictions = myPrediction.objects.filter(user = user)
    predictionsfilter = myPrediction.objects.filter(user = user).values_list('first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eighth', 'ninth', 'tenth', 'eleventh', 'twelfth', 'thirteenth', 'fourteenth', 'fifteenth', 'sixteenth', 'seventeenth', 'eighteenth', 'nineteenth', 'twentieth')
    points = 0
    pointslog = []
    for x in range(20):
        # User guessed the perfect score, 0 points recorded
        if predictionsfilter[0][x] == pointsteamlist[x]:
            pointslog.append(0)
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
    # Update the user's current score
    myPrediction.objects.filter(user = user).update(currentScore = points)
    predictions = myPrediction.objects.filter(user = user)
    return render(request, "predict/friendpredictions.html", {
        "teams": pointsteamlist,
        "predictions": predictions,
        "pointslog": pointslog,
        "name": name
    })

@login_required
def settings(request):
    # Find out current user info
    user = User.objects.get(username = request.user)
    # See if user is subscribed to the emails
    for u in User.objects.filter(username = user):
        if u.isSubscribed == True:
            unsubmessage = "You are currently subscribed to receive a monthly update. Would you like to unsubscribe?"
            submessage =""
        else:
            submessage = "You are not currently subscribed to receive a monthly update. Would you like to subscribe?"
            unsubmessage = ""
    # See what leagues the user is a member of, but not head of
    leagues = leagueMember.objects.filter(user = user, isManager = False)
    
    # See what leagues the user created
    createdleagues = leagueList.objects.filter(userManager = user)
    
    # See the players from a league that a user manages, excluding themselves
    createdleaguesm = leagueList.objects.filter(userManager = user).values_list('leagueName')
    players = leagueMember.objects.filter(leagueName__in = createdleaguesm).exclude(user = user)
    if request.method == 'POST':
        # Work out which form is submitted
        if request.POST.get("cpassword") == "Confirm New Password":
            # Check the two passwords match
            if not request.POST.get("password") == request.POST.get("confirmation"):
                messages.error(request, "Sorry, the passwords did not match")
                return HttpResponseRedirect("settings")
            # Change the passwords on the db
            user.set_password(request.POST.get("password"))
            user.save()
            # Let the user know their password has been updated
            messages.success(request, 'Your password has been updated')
            # Relog the user in as password has been changed
            login(request, user)
            return HttpResponseRedirect("settings")
        elif not request.POST.get("cemail") == None:
            newemail = request.POST.get("updateemails")
            # Update in the db
            User.objects.filter(username = user).update(email = newemail)
            messages.success(request, 'Your email address has been changed')
            return HttpResponseRedirect("settings")
        elif request.POST.get("emailchange") == "Subscribe":
            # Change db to subscribe
            User.objects.filter(username = user).update(isSubscribed = True)
            messages.success(request, 'Thanks, you are now subscribed to receive monthly updates')
            return HttpResponseRedirect("settings")
        elif request.POST.get("emailchange") == "Unsubscribe":
            # Change db to unsubscribe
            User.objects.filter(username = user).update(isSubscribed = False)
            messages.success(request, 'Thanks, you are now not subscribed to receive monthly updates')
            return HttpResponseRedirect("settings")
        elif not request.POST.get("leave") == None:
        # User wants to leave a league
            # Find out the name of the league user wants to leave
            leaveleaguename = request.POST.get("leave")
            # Reduce number of members in leagueList db by -1
            for n in leagueList.objects.filter(leagueName = leaveleaguename):
                leagueList.objects.filter(leagueName = leaveleaguename).update(numbMembers = int(n.numbMembers) - 1)
            # Delete your entry into the league in the db
            leagueMember.objects.filter(user = user, leagueName = leaveleaguename).delete()
            messages.success(request, f"You have just left {leaveleaguename}.")
            return HttpResponseRedirect("settings")
        elif not request.POST.get("updatepin") == None:
            # Get form info
            newpin = request.POST.get("randomkey")
            leaguename = request.POST.get("updatepin")
            # Throw user out if pin was not generated
            if newpin == "":
                messages.error(request, "Please generate a key")
                return HttpResponseRedirect("settings")
            # Update the league as pin has been generated successfully
            leagueList.objects.filter(leagueName = leaguename).update(key = newpin)
            messages.success(request, f"You have just updated the key for {leaguename}. It is now {newpin}.")
            return HttpResponseRedirect("settings")
        elif not request.POST.get("remove") == None:
            # Find out which user wants removing from which league
            leaguename = request.POST.get("remove")
            evictedplayer = request.POST.get("selectremove")
            # Reduce the number of members by one
            for n in leagueList.objects.filter(leagueName = leaguename):
                leagueList.objects.filter(leagueName = leaguename).update(numbMembers = int(n.numbMembers) - 1)
            # Delete that player's entry into the league in the db
            leagueMember.objects.filter(user = evictedplayer, leagueName = leaguename).delete()
            messages.success(request, f"You have just removed {evictedplayer} from {leaguename}.")
            return HttpResponseRedirect("settings")
        elif not request.POST.get("deletetheleague") == None:
            deleteyourleague = request.POST.get("deletetheleague")
            # Delete the requested league
            leagueList.objects.filter(leagueName = deleteyourleague).delete()
            # Remove participants from the db
            leagueMember.objects.filter(leagueName = deleteyourleague).delete()
            messages.success(request, f"Your league, {deleteyourleague} has now been deleted.")
            return HttpResponseRedirect("settings")
        elif not request.POST.get("deleteaccount") == None:
            del_user = request.POST.get("deleteaccount")
            # Reduce numbers in a league if they were a member (not manager)
            if leagues:
                for l in leagues:
                    minusName = l.leagueName
                for n in leagueList.objects.filter(leagueName = minusName):
                    leagueList.objects.filter(leagueName = minusName).update(numbMembers = int(n.numbMembers) - 1)
            # Remove potential league members from leagues that are not the user's
            # Find out what leagues the user manages
            delleagues = leagueMember.objects.filter(user = user, isManager = True)
            # If user does maange a league, delete the members from it(apart from user that will be deleted due to foriegn key)
            if delleagues:
                for x in delleagues:
                    leagueMember.objects.filter(leagueName = x.leagueName).exclude(user = user).delete()
            # Log the user out
            logout(request)
            # Remove the account from the db
            User.objects.filter(username = del_user).delete()
            # Let user know account has been deleted
            messages.success(request, f"Your account, {del_user}, has been successfully deleted. Thank you for playing Predict the League.")
            return HttpResponseRedirect(reverse("index"))
        else:
            # An error has occurred
            return HttpResponseNotFound('<h1>Error, response not submitted.</h1>')
    else:
        # Return the forms as normal
        return render(request, "predict/settings.html", {
            "submessage": submessage,
            "unsubmessage": unsubmessage,
            "leagues": leagues,
            "createdleagues": createdleagues,
            "players": players
        })
