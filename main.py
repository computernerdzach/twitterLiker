import sys

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
followers = api.get_follower_ids()
following = api.get_friend_ids()
# heading for log and readout
message = f"[BEGIN LOG] -- {name}'s log -- {right_now()}"
report(message=message, logfile=logfile)
# main loop
run = True
tweet_run = 1

while run:
    main(followers=followers, following=following, logfile=logfile,
         client=client, api=api, query=query)
    # another round?
    run = go_again(logfile=logfile)
    # increment and initiate next run of 100 tweets
    log_next_run(logfile=logfile, tweet_run=tweet_run)
sys.exit()
