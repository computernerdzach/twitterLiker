# TwitterLiker
TwitterLiker is a bot that likes tweets based on hashtags, and randomly follows some of the authors of those tweets.

## Setup

### Create a Twitter bot
   * Apply for a Twitter developer account.
   * Create a Twitter project and app.
   * Edit the Twitter application's settings.
   * Generate access token and secret access token

### Fill in bot credentials
* Create a file in the root folder called `credentials.py`.
* Copy the contents of `credentials_template.py` to the new file.
* Change the placeholder values to the appropriate values based on your Twitter bot.

### Set name and query
* The `name` variable in `credentials.py` is used only to name the logfile.
* The `query` variable:
  * learn to build Twitter queries click [here](https://developer.twitter.com/en/docs/twitter-api/tweets/search/integrate/build-a-query).

## Running
Navigate to the root directory and enter the following command to run the app.
```bash
python3 main.py
```

## Contributing
The repo is currently open for all, but please inquire before making changes.