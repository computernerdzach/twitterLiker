import sys

from credentials import *
from utilities import *

logfile = open(f'twitter-like-log-{name}.log', 'a')
used_tweets = open(f'{name}_used_tweets.log', 'w+')

client = tweepy.Client(token_bearer, api_key, api_secret, access_token=access_token,
                       access_token_secret=access_token_secret)
auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token=access_token, access_token_secret=access_token_secret)
api = tweepy.API(auth=auth)

followers = api.get_follower_ids()
following = api.get_friend_ids()

message = f"[BEGIN LOG] -- {name}'s log -- {right_now()}"
report(message=message, logfile=logfile)

run = True
tweet_run = 1

while run:
    tweet_run = main(followers=followers, following=following, logfile=logfile,
                     client=client, api=api, query=query, tweet_run=tweet_run)

    run = go_again(logfile=logfile)

    log_next_run(logfile=logfile, tweet_run=tweet_run)

logfile.close()
used_tweets.close()

sys.exit()
