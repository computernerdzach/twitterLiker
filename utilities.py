import time
import datetime
import requests
import tweepy
import re

from random import randint
from typing import TextIO

from word_lists import *


def right_now() -> str:
    return datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")


def report(message: str, logfile: TextIO):
    print(message)
    logfile.write(f"{message}\n")


def follow_and_report(logfile: TextIO, client: requests.session, author_id: int, author: str):
    client.follow_user(author_id)
    message = f"/ / / / [RANDOMLY FOLLOWED AUTHOR] -- author: {author} -- {right_now()}"
    report(message=message, logfile=logfile)


def random_follow(tweet: tweepy.Tweet, logfile: TextIO, client: requests.session, api: tweepy.API):
    try:
        author_id = tweet.data['author_id']
        author = api.get_user(user_id=author_id).screen_name
        random_number = randint(1, 20)
        if random_number == 15:
            follow_and_report(logfile=logfile, client=client, author_id=author_id, author=author)
    except Exception as oops:
        message = f"[OOPS] -- {oops} -- {right_now()}"
        report(message=message, logfile=logfile)


def follow_back(followers: list, following: list, logfile: TextIO, client: requests.session, api: tweepy.API):
    for follower in followers:
        if follower not in following:
            try:
                client.follow_user(follower)
                message = f"[FOLLOW BACK] -- now following: {api.get_user(user_id=follower).screen_name} -- {right_now()}"
                report(message=message, logfile=logfile)
            except Exception as oops:
                message = f"[OOPS] -- {oops} -- {right_now()}"
                report(message=message, logfile=logfile)
        else:
            message = f"[NO FOLLOW] -- already following {api.get_user(user_id=follower).screen_name}"
            report(message=message, logfile=logfile)


def maybe_like_and_report(client: requests.session, tweet: tweepy.Tweet, logfile: TextIO, tweet_run: int, tweet_count: int):
    maybe = randint(1, 2)
    if maybe == 2:
        client.like(tweet.id)
        message = f"[LIKED TWEET] #: {tweet_count} of 100; run: {tweet_run}.\n" \
                  f"    {tweet.text[0:70]}\n" \
                  f"    [liked time]: {right_now()}"
    else:
        message = f"[DID NOT LIKE TWEET] #: {tweet_count} of 100; run: {tweet_run}.\n" \
                  f"    [not liked time]: {right_now()}"
    report(message=message, logfile=logfile)


# like each tweet
def like_tweet_random_follow(tweets: {requests.Response}, logfile: TextIO,
                             client: requests.session, api: tweepy.API, tweet_run: int):
    tweet_count = 1
    for tweet in tweets.data:
        try:
            maybe_like_and_report(client=client, tweet=tweet, logfile=logfile,
                                  tweet_run=tweet_run, tweet_count=tweet_count)
            random_follow(tweet=tweet, logfile=logfile, client=client, api=api)
            tweet_count += 1
            time.sleep(randint(20, 45))
        except Exception as e:
            message = f"[OOPS] -- {e} --- {right_now()}"
            report(message=message, logfile=logfile)
            time.sleep(10)
        try:
            random_tweet(logfile=logfile, api=api)
        except Exception as oops:
            message = f"[OOPS] -- {oops} -- {right_now()}"
            report(message=message, logfile=logfile)


def log_next_run(logfile: TextIO, tweet_run: int):
    message = f"[INITIATE TWEET RETRIEVAL] {tweet_run}-- of 100 tweets (asks to continue after 4 runs) -- {right_now()}"
    report(message=message, logfile=logfile)


def go_again(logfile: TextIO) -> bool:
    question = "Continue? [y] or [n]\n> "
    user_answer = input(question).lower()
    while (user_answer != "y") and (user_answer != "n"):
        user_answer = input('Please enter "y" or "n" and press enter.')
    if user_answer == "n":
        message = f"C{question} -- {user_answer}"
        report(message=message, logfile=logfile)
        logfile.close()
        return False
    elif user_answer == "y":
        message = f"C{question} -- {user_answer}"
        report(message=message, logfile=logfile)
        return True
    else:
        message = "[ERROR] -- beginning next run"
        report(message=message, logfile=logfile)


def build_hashtags(word_filter: list[str], tweet_choice: str) -> list[str]:
    hashes = []
    for word in word_filter:
        single = f' {word} '.lower()
        plural = f' {word}s '.lower()
        if single in tweet_choice:
            hashes.append(word.lower())
        elif plural in tweet_choice:
            hashes.append(f"{word}s".lower())
        else:
            pass
    return hashes


def aux_verb_hash(tweet_choice: str) -> list[str]:
    hashes = []
    for a_verb in auxiliary_verbs:
        isolated = f" {a_verb} ".lower()
        pattern = r"(?:" + re.escape(isolated) + r"\: ).+\b"
        after_aux_verbs = re.findall(pattern=pattern, string=tweet_choice)
        for word in after_aux_verbs:
            hashes.append(word.lower())
    return hashes


def random_tweet(logfile: TextIO, api: tweepy.API, used_file: TextIO):
    tweet_chance = randint(1, 1000)
    if tweet_chance == 42:
        tweet_roll = randint(1, len(ice_breakers))
        tweet_choice = ice_breakers[tweet_roll]
        if tweet_choice not in used_file:
            try:
                tweet_choice = tweet_choice.lower()
                hashes = build_hashtags(word_filter=nouns, tweet_choice=tweet_choice)
                hashes += build_hashtags(word_filter=verbs, tweet_choice=tweet_choice)
                hashes += aux_verb_hash(tweet_choice=tweet_choice)
                hashes = [*set(hashes)]
                message = f"{tweet_choice}\n\n".lower()
                for hashtag in hashes:
                    message += f"#{hashtag} ".lower()
                api.update_status(message)
                used_file.write(f"{tweet_choice}\n")
                report(message=message, logfile=logfile)
            except Exception as oops:
                message = f"[OOPS] -- {oops} -- {right_now()}"
                report(message=message, logfile=logfile)
        else:
            pass
    else:
        pass


def main(followers: list[int], following: list[int], logfile: TextIO,
         client: requests.session, api: tweepy.API, query: str, tweet_run: int):
    try:
        follow_back(followers=followers, following=following, logfile=logfile, client=client, api=api)
    except Exception as oops:
        message = f"[OOPS] -- {oops} -- {right_now()}"
        report(message=message, logfile=logfile)
    for i in range(0, 4):
        tweets = client.search_recent_tweets(query=query, tweet_fields=['context_annotations', 'created_at'],
                                             expansions=['entities.mentions.username', 'author_id'],
                                             user_fields=['username'], max_results=100)
        like_tweet_random_follow(tweets=tweets, logfile=logfile, client=client, api=api, tweet_run=tweet_run)
        tweet_run += 1
    return tweet_run
