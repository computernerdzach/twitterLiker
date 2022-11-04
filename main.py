from credentials import *
from utilities import *

# create a dynamic log writer
logfile = open(f'twitter-like-log-{name}.log', 'a')

# Build bot using preferred credentials from above
client = tweepy.Client(token_bearer, api_key, api_secret,
                       access_token=access_token, access_token_secret=access_token_secret)
auth = tweepy.OAuth1UserHandler(api_key, api_secret,
                                access_token=access_token, access_token_secret=access_token_secret)
api = tweepy.API(auth=auth)

# build lists of followers and following to compare and follow back followers
followers = api.get_followers()
following = api.get_friends()

# heading for log and readout
message = f"[BEGIN LOG] -- {name}'s log -- {right_now()}"
report(message=message, logfile=logfile)

# main loop
main = True
tweet_run = 1
while main:
    # follow back all followers
    follow_back(followers=followers, following=following, logfile=logfile, client=client, api=api)

    # set log sub-heading
    logfile.write(set_sub_heading(tweet_run=tweet_run))

    # get 100 tweets matching hashtags, and returning desired data
    tweets = client.search_recent_tweets(query=query, tweet_fields=['context_annotations', 'created_at'],
                                         expansions=['entities.mentions.username', 'author_id'],
                                         user_fields=['username'], max_results=100)

    # like the tweets and randomly select a few authors to follow
    like_tweet_random_follow(tweets=tweets, tweet_run=tweet_run, logfile=logfile, client=client, api=api)

    # increment and initiate next run of 100 tweets
    log_next_run(logfile=logfile)
    tweet_run += 1
