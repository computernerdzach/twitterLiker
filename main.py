import argparse
import sys


from credentials import credentials
from utilities import *

parser = argparse.ArgumentParser()
parser.add_argument("--name", "-n")
args = parser.parse_args()
name = args.name

token_bearer = credentials[name]['token_bearer']
api_key = credentials[name]['api_key']
api_secret = credentials[name]['api_secret']
access_token = credentials[name]['access_token']
access_token_secret = credentials[name]['access_token_secret']
query = credentials[name]['query']

logfile = open(f'logs/twitter-like-log-{name}.txt', 'a')

client = tweepy.Client(token_bearer, api_key, api_secret, access_token=access_token,
                       access_token_secret=access_token_secret)
auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token=access_token,
                                access_token_secret=access_token_secret)
api = tweepy.API(auth=auth)

followers = api.get_follower_ids()
following = api.get_friend_ids()

message = f"[BEGIN LOG] -- {name}'s log -- {right_now()}\n-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~"
report(message=message, logfile=logfile)

run = True
tweet_run = 1


try:
    while run:
        tweet_run = main(followers=followers, following=following, logfile=logfile,
                         client=client, api=api, query=query, tweet_run=tweet_run, name=name)
        run = go_again(logfile=logfile)
        log_next_run(logfile=logfile, tweet_run=tweet_run)

except KeyboardInterrupt:
    message = "\nAttempting to close files gracefully."
    report(message=message, logfile=logfile)
    logfile.close()
    print("Open files have been closed. Exiting now.")
    sys.exit()





