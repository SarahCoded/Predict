from django.core.management.base import BaseCommand, CommandError
from predict.models import User, myPrediction, leagueList, leagueMember, API
import http.client, os, json, ast, math

class Command(BaseCommand):
    help = 'Update the score for all users'

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
    
    predictors = myPrediction.objects.values_list('user')
    
    # Calculate points if user has submitted predictions
    predictions = myPrediction.objects.filter(user__in = predictors)
    
    if predictions:
        predictionsfilter = myPrediction.objects.filter(user__in = predictors).values_list('first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eighth', 'ninth', 'tenth', 'eleventh', 'twelfth', 'thirteenth', 'fourteenth', 'fifteenth', 'sixteenth', 'seventeenth', 'eighteenth', 'nineteenth', 'twentieth', 'user')
        # Set an integeer to ensure all the users are looped through
        qq = 0
        for q in predictionsfilter:
            points = 0
            # TODO Another row, pointslog in models!
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

    def handle(self, *args, **options):
        predictors = myPrediction.objects.values_list('user')
        lenpredictors = len(predictors)
        # Return success message
        self.stdout.write(self.style.SUCCESS('Updated the points for %i users' % lenpredictors))
