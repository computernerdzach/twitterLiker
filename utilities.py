import time
import datetime
import requests
import tweepy

from random import randint
from typing import TextIO


# pick this exact moment right now (at any given moment)
def right_now() -> str:
    return datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")


def report(message: str, logfile: TextIO):
    print(message)
    logfile.write(message)


# set now and write heading
def set_sub_heading(tweet_run: int, logfile: TextIO) -> str:
    message = f"[TWEET RETRIEVAL] -- # {tweet_run} -- {right_now()}"
    report(message=message, logfile=logfile)
    return message


def make_and_report_number(logfile: TextIO) -> int:
    random_number = randint(1, 20)
    message = f"[FOLLOW DECISION] -- #[{random_number}] -- must match [15]"
    report(message=message, logfile=logfile)
    return random_number


def follow_and_report(random_number: int, logfile: TextIO, client: requests.session, author_id: int, author: str):
    # compare random number for user
    message = f"{random_number} = 15... {random_number==15}"
    report(message=message, logfile=logfile)

    # follow tweet author and report
    client.follow_user(author_id)
    message = f"[FOLLOWED AUTHOR] -- author id: {author} -- {right_now()}"
    report(message=message, logfile=logfile)


# randomly select accounts to follow
def random_follow(tweet: tweepy.Tweet, logfile: TextIO, client: requests.session, api: tweepy.API):
    try:
        # generate random number and report to log
        random_number = make_and_report_number(logfile=logfile)

        # capture the author_id and screen_name of the tweet's author
        author_id = tweet.data['author_id']
        author = api.get_user(user_id=author_id).screen_name

        # randomly follow authors of 5% of liked tweets
        if random_number == 15:
            follow_and_report(random_number=random_number, logfile=logfile,
                              client=client, author_id=author_id, author=author)
            return

        # report no follow
        else:
            message = f"[NO FOLLOW] -- did not follow author/id: {author}/{author_id} -- {right_now()}"
            report(message=message, logfile=logfile)
            return

    # report oopsies
    except Exception as oops:
        message = f"[OOPS] -- {oops} -- {right_now()}"
        report(message=message, logfile=logfile)


# follow back all followers
def follow_back(followers: list, following: list, logfile: TextIO, client: requests.session, api: tweepy.API):
    # build a list of id's of accounts followed
    following_ids = []
    for followed in following:
        following_ids.append(followed._json['id'])

    for follower in followers:
        # each follower captures id and screen_name
        follower_id = follower._json['id']
        follower_name = api.get_user(user_id=follower_id).screen_name

        # if not following, follow and report
        if follower._json['id'] not in following_ids:
            try:
                client.follow_user(follower_id)
                message = f"[FOLLOW BACK] -- now following: {follower_name} -- {right_now()}"
                report(message=message, logfile=logfile)

            # report oopsies
            except Exception as oops:
                message = f"[OOPS] -- {oops} -- {right_now()}"
                report(message=message, logfile=logfile)

        # else report already following
        else:
            message = f"[FOLLOW BACK] -- already following {follower_name}"
            report(message=message, logfile=logfile)


def like_and_report(client: requests.session, tweet: tweepy.Tweet, logfile: TextIO):
    # like each tweet that is found and report
    client.like(tweet.id)
    message = f"[LIKED TWEET] -- # {tweet.text} -- {right_now()}"
    report(message=message, logfile=logfile)


# like each tweet
def like_tweet_random_follow(tweets: {requests.Response}, tweet_run: int, logfile: TextIO,
                             client: requests.session, api: tweepy.API, tweet_count: int):
    for tweet in tweets.data:
        try:
            # increment tweet count and report
            tweet_count += 1
            report(message=f"tweet_count: {tweet_count}", logfile=logfile)

            # like and report
            like_and_report(client=client, tweet=tweet, logfile=logfile)

            # randomly follow (or not) the tweet author
            random_follow(tweet=tweet, logfile=logfile, client=client, api=api)

            # log the run count (100 tweets per run)
            message = f"[CURRENT RUN] -- of 100 tweets -- {tweet_run}"
            report(message=message, logfile=logfile)

            # chill for a bit
            time.sleep(35)
            return tweet_count

        # report oopsies
        except Exception as e:
            message = f"{e} --- {right_now()}"
            report(message=message, logfile=logfile)
            time.sleep(10)


# report that the next run is starting
def log_next_run(logfile: TextIO):
    message = f"[INITIATE TWEET RETRIEVAL] -- of 100 tweets -- {right_now()}"
    report(message=message, logfile=logfile)


def go_again():
    user_answer = ""
    while (user_answer != "y") and (user_answer != "n"):
        user_answer = input("Continue? [y] or [n]\n> ")
        if user_answer.lower() == 'y':
            run = True
        elif user_answer.lower() == 'n':
            run = False
        else:
            print('Please enter "y" or "n" and press enter.')
    return run

