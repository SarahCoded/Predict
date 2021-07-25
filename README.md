# Predict the League

This is a predictions game website, in which you submit a forecast of how you think the English Premier League standings will be at the end of the season. You can join leagues to compare your predictions with friends, and get monthly updates via email on how you are doing.

The project was built using Django as a backend framework, with JavaScript for the front end DOM manipulation. Jinja was used to control HTML content, and SASS was used for styling. During production, a SQLite database was used. I used Heroku to deploy the application, with Gunicorn and Postgres.

![Alt text](predict/static/predict/images/dscreenshot3.png?raw=true "Website Screenshot")

# Contents

- [Running the Application](#Running-the-Application)
- [Scoring System](#Scoring-System)
- [Files](#Files)
  * [models.py](#models.py)
    + [User](#User)
    + [API](#myPrediction)
    + [leagueList and leagueMember](#leagueList-and-leagueMember)
  * [views.py](#views.py)
  * [Management Commands](#Management-Commands)
- [Forms](#Forms)
- [Styling](#Styling)
- [Timing](#Timing)
- [Video Demonstration](#Video-Demonstration)
- [Concluding Remarks](#Concluding-Remarks)

## <a name="Running-The-Application"></a>Running the Application

I deployed this application on Heroku with Gunicorn, Postgres, and an AWS S3 bucket. It can be accessed [here](https://predictheleague.herokuapp.com/).

## <a name="Scoring-System"></a>Scoring System

The scoring system for measuring a user's predictions is as follows. Ideally, you want as few points as possible. Every team that you predict incorrectly gives you points depending on how far off from the real position that you are. For example, if you had Manchester United to finish 3rd and they finish 1st, you get 2 points. This isn't as bad as predicting them to finish 20th, which would earn you 19 negative points! On the other hand, each correctly guessed team will earn you 0 points.

To demonstrate this in a table, I had used JavaScript to colour code the individual rows, with green being a team is spot on with 0 points, and red being bad with over 6 points gained.

## <a name="Files"></a>Files

### <a name="models.py"></a>models.py

I used 5 different models for the application. Below I have outlined what each one contains.

#### <a name="User"></a>User

The first one was 'User', which I borrowed from Django's built in framework. This is due to the security that it maintains such as the hashing of passwords. I then copied some boilerplate code from a previous CS50w project, such as login/logout/register forms and their views to save a little time. I added one extra field to this table, a boolean 'is Subscribed' which would indicate to myself whether the user wants to receive monthly updates on how their prediction is going.

#### <a name="API"></a>API

As the name suggests, this model uses an external API to get the latest football results. I used a free API from [football-data](https://www.football-data.org/) to receive the positions of all of the teams. Incidentally, this was the last model that I wrote. Initially, my plan had simply been for the API data to be received in the views.py file whenever someone logged in. However, I noticed this caused a delay in loading time for the user. It also meant that in the unlikely event that 6 people had refreshed the page in the space of a minute, the site would break. As I was toying with the idea of uploading the application to the real world, I looked around for alternative ways for the data to be received and came across Django's management commands. I wrote a function that updates the API to the API model when called, and stored the data in the model with a JSON field.

#### <a name="myPrediction"></a>myPrediction

This model stores the prediction data that the user has submitted in a form along with their current score. It is joined by a Foreign Key to the user's id. Looking back, I should had used a JSON field for storing the data, like I had done with the API (instead I stored 20 separate rows, 1 row for each team). This would had saved some time with typing out the tables rows in HTML using a loop instead of typing out 20 rows for each model column.

#### <a name="leagueList-and-leagueMember"></a>leagueList and leagueMember

I have grouped these last two models together as they exist to serve the same function - provide a league table to find out how your friends are doing. The idea is that you can either create a league, in which you become the manager and it is up to you to share the key code with friends and encourage them to join, or join a league in which another user is the manager. As the manager, you have admin privileges to remove an unwanted player from the league, change the key code, or delete the league. If you decide to delete your account, as a consequence, the league will also be deleted.

The other model, leagueList, is a list of each unique league that has been created, along with the manager who created the league, and how many members there currently are. This model provides a list of all users who have joined a league with a boolean field of if they are the manager or not.

Both tables have the user as a Foreign key, so the user's entry in the league will be deleted if they delete their account.

![Alt text](predict/static/predict/images/dscreenshot2.png?raw=true "Website Screenshot")

### <a name="views.py"></a>views.py

This contains all the functions that are ran when the user makes a request to the web server. The responses include showing the user's current league table predictions, the current real time positions of the teams (fetched from the football-data API), and friend leagues. I also made a settings view in which a user could change various aspects of their account, such as email, password, to delete their account, to leave or manage a league, and to change their email preferences. The one view that I didn't write was the resetting of the password, as Django had an inbuilt function that was able to handle this.

### <a name="Management-Commands"></a>Management Commands

I have written 3 commands to be set up and ran on Heroku's task scheduler.

The first, apicall.py, is called every 10 minutes from Heroku's task scheduler to get the latest football data. This then updates the API model, which talks to views.py when the user logs in. In terms of error checking, I will receive an email if the API call does not work and returns an error code.

The next function, updateusers.py, was written as an edge case I realized could realistically happen - a user signs up and logs in, but then never revisits the site so their points will never be updated. This function goes through all the users that have submitted their predictions and updates the points in the model. It runs once a day as this was the most infrequent time frame the free Heroku add-on offered. Realistically it only needs to be ran once a month, but I don't want to take any chances on it failing to run, and it does not exhaust dyno hours (Heroku's calculation of your use of their resources) by any means.

The last file, sendmonthly.py was the hardest to write, but perhaps also the most rewarding and unique feature of the application. I wanted to have an email sent out to each subscriber with an update on how their predictions are coming along. I realized this could feasibly be done using a standard HTML template with Jinja passed through it (as jinja is simply used to render the HTML information before the email actually sends). Fortunately, Django had a built in mail function, which I had already used to send each user an email upon registration. However, to use this send mail function for each user would be a waste of resources, and take a long time to execute, one request alone takes around 4 seconds to send. This would be a problem when considering upscaling. Therefore, I turned to Django's send mass mail function. However, it was a little more tricky to pass html through this. Luckily, there were answers on stackoverflow which dealt with this problem using a get_connection function. I added a few additional bits of information to the HTML sendmonthly template which would differentiate itself from the site, such as what your worst prediction is currently, and how many teams you have forecast as spot on. To get around Heroku's task scheduler only operating on a 10 minute, hourly or daily basis, I ended up setting up a rule using bash, which was for the send an email command to only run if it is the first day of the month.

There were a couple of drawbacks from using HTML emails. One is that you have to define CSS in the actual file. Gmail requires the styling to be in line with the HTML tags, for example. As I didn't think it would be feasible to test this on multiple email platforms, I placed the styling in the header and in the tags, so hopefully it will be caught somewhere in most browsers. I also included a plain text version of the email in case an old email provider is used which cannot cope with HTML. In emails, I was not able to use JavaScript to colour the tables like I have done on the homepage. This makes sense, as it would be a security vulnerability otherwise! Instead, using the inline styling gave me the idea to use Jinja to colour the table rows in a if - else if - else scenario. Although this made the HTML code look horrendously long, it didn't take that effort to do with some mindless copy and pasting.

## <a name="Forms"></a>Forms

One of the most crucial elements of this project, I felt, was the initial form that the user would be presented with upon registering on the site. It would need to allow unique selections only from the current list of teams in the league. I decided that the best way to achieve this would be using 20 individual select rows on a HTML form. Initially, I had imported a library which could remove a team once it had been selected from a row, but I realized once you had selected 20 teams, it was impossible to change one prediction say, by swapping the places of two teams. Therefore, using JavaScript, I implemented an undo button which would appear on any row that had a selection applied to it. Yet this caused issues with the imported function as it would not recognize this remove action that JavaScript was doing all the time, and the undone teams would sometimes not reappear on other selects.

After trying a few different ways to get around this, such as adding the team back on myself, or recalling the function again, and using a different library, I stumbled upon some jQuery code online which worked without error.

Another form used to create a league, uses a JavaScript function to generate a random string of 6 letters/numbers. This acts as a key that other users of the site can enter to create their own leagues.

Other forms on the site are in settings to change passwords, emails, league memberships etc. I probably spent more time on the animation than the actual Python logic to make the settings forms functional.

## <a name="Styling"></a>Styling

The general theme of the website was football, so I decided the colour palette would be various shades of green. For the background, initially I had used a grassy field, but I found it was just taking a bit too long to load, no matter how much I had compressed the file without compromising on pixelation quality. Instead, I went for a plain background, which subtly changed colour from light to dark green over a period of time. This meant I did not have to worry too much about the contrast with other text, or how it was going to resize on different screens, as long as I maintained the rules for it to cover 100%.

I made the logo quickly on a mobile phone logo making app. At the time, I thought to myself I just needed to do something quickly so I could make sure sizing rules work out, but I ended up keeping the logo as it was, because it wasn't too bad. I also ended up using the football icon as the image to be displayed on a tab window.

The form buttons were all a shade of green, with white angular borders. I chose the design to look like this to reflect the white lines running across a football field. Looking back, it makes the website look a bit dated by not going with the border radius rounding, but my main aim of the website was for it to be functional, so I didn't take into consideration the appearance as much as I perhaps should had. By choosing not to use Bootstrap for the website, I had to spend longer styling out all the elements than I realized, but nevertheless it was good practice for myself to keep on top of CSS techniques that I had forgotten from a few months ago.

The hardest part of styling in this project, I found, was animation. Initially when trying to create a glide effect when a user taps on a menu icon in mobile, nothing would happen. I found out this was because of two instructions I had made which CSS animation did not like - I had set the height to auto, and I had got the menu to have visibility of hidden. This makes sense, as the computer will need to calculate how fast the animation should be, which is impossible if it does not know what the end height will be in advance. Therefore, I had to give a height, which meant a little quality was lost as on some screens the drop down would look slightly too big, but the most important thing was for all the menu items to be visible. I made a couple of media queries in CSS for the different screen heights. Secondly, I unhid all the menu items - in reality they didn't need to be hidden, because the menu height would mean they don't show anyway. In JavaScript, previously it was changing the menu size depending on whether an element was hidden or not. I changed this to call the function depending on what the menu height is currently.

## <a name="Timing"></a>Timing

One hurdle I face is how time sensitive making this was. I know for certain that the English Premier League starts on the 13th August 2021. If I wanted people to submit predictions, ideally I would need to finish the website a few weeks beforehand. Onn the other hand, I didn't really want to make a cutoff point for people able to submit predictions, as this would make the app unusable for visitors 80% of the time. But then if people could predict the outcome any time of the year, it would be too easy to cheat and say, get the right outcome one day before the season finishes.

The compromise I had made is to allow users to submit a prediction at any time. However, once a prediction has been submitted, it cannot be changed, even if the season has not begun yet. A date time field was added to the myPredictions model, so that anyone could look at a user's account and see when they submitted their prediction. Also, the manager of a league could remove a user if they wished, perhaps because they have made a new account and resubmitted better scoring predictions.

When calculating user's scores for the application in settings.py, I was fortunate in that the API had not yet updated for the new season because the match fixtures had not come out yet. This meant I could run the code against the finishing scores, which gave myself some reassurance the points system devised was working. Once the API did update, the list of teams became an alphabetical list, each with 0 points. Once a user had submitted their results, the table would appear with their current score. This didn't feel right, as the season would not start for a few weeks yet. Using the Python library datetime, I specified using unix time, that an alternative table should be shown with ? for points in the rows, instead of the coloured tables, if the league has not yet started.

## <a name="Video-Demonstration"></a>Video Demonstration

As part of the submissions criteria for CS50W, I made a video [here](https://youtu.be/bVy-E8UFhfM) demonstrating its use.

## <a name="Concluding-Remarks"></a>Concluding remarks

Currently, this website is only going to be functional while the present football season lasts. Around June next year, I hope to go over the code and prepare the website for a new season. I imagine I will create a new model to redirect all of the API toward, so that the previous year's results are not lost. I might end up redoing the CSS, to make it look a bit neater and finished. However, the main aim for this season was for it to be functional and without any major code breaking bugs. So far, this seems to have worked.