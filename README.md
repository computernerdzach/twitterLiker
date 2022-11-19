# TwitterLiker
### V1.1: 
* TwitterLiker is a bot that likes tweets based on hashtags, and randomly follows some of the authors of those tweets.
### V1.2: 
* TwitterLiker now likes about 50% of the tweets it finds, follows about 5% of the authors of tweets it likes, and for each tweet has a 0.1% chance of randomly publishing an icebreaker tweet, complete with hashtags.

# Setup

### Create a Twitter bot
   * Apply for a Twitter developer account.
   * Create a Twitter project and app.
   * Edit the Twitter application's settings.
   * Generate access token and secret access token

### Fill in bot credentials
* Rename the file `credentials_template.py` to `credentials.py`.
* Uncomment the credentials dictionary.
* Change the placeholder values to the appropriate values based on your Twitter bot.

### Set query
* Learn to build Twitter queries click [here](https://developer.twitter.com/en/docs/twitter-api/tweets/search/integrate/build-a-query).
* A basic query is used for a placeholder value as an example for the user.

# Running
Navigate to the root directory and enter the following command to run the app.
```bash
python3 main.py --name BOTNAME
```
Replace the `BOTNAME` string with the name of your bot, making sure to match the value in the credentials dictionary found in `credentials.py`.
# Stopping
* After each set of 4 runs (1 run consisting of 100 tweets) the user will be asked if they want to continue.
* You can terminate gracefully with a keyboard interrupt `[ctrl]` + `[C]`. The program will close any open files and exit with 

# Contributing
The repo is currently open for all, but please inquire before making changes since this is a learning opportunity for me.