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


def random_follow(tweet: tweepy.Tweet, logfile: TextIO, client: requests.session, api: tweepy.API):
    try:
        author_id = tweet.data['author_id']
        author = api.get_user(user_id=author_id).screen_name
        random_number = randint(1, 20)
        if random_number == 15:
            client.follow_user(author_id)
            message = f"/ / / / [RANDOMLY FOLLOWED AUTHOR] -- author: {author} -- {right_now()}"
        else:
            message = f"/ / / / [NO RANDOM FOLLOW] -- author: {author} -- {right_now()}"
        report(message=message, logfile=logfile)
    except Exception as oops:
        message = f"[OOPS] -- {oops} -- {right_now()}"
        report(message=message, logfile=logfile)


def follow_back(followers: list, following: list, logfile: TextIO, client: requests.session, api: tweepy.API):
    follower_index = 1
    for follower in followers:

        if follower not in following:
            try:
                client.follow_user(follower)
                message = f"[FOLLOW BACK] -- now following: " \
                          f"{api.get_user(user_id=follower).screen_name} -- {right_now()}\n" \
                          f"follower index {follower_index} out of {len(followers)}"
                report(message=message, logfile=logfile)
                follower_index += 1
            except Exception as oops:
                message = f"[OOPS] -- {oops} -- {right_now()}"
                report(message=message, logfile=logfile)
                follower_index += 1
        else:
            message = f"[NO FOLLOW] -- already following {api.get_user(user_id=follower).screen_name}\n" \
                      f"follower index {follower_index} out of {len(followers)}"
            report(message=message, logfile=logfile)
            follower_index += 1


def maybe_like_and_report(client: requests.session, tweet: tweepy.Tweet,
                          logfile: TextIO, tweet_run: int, tweet_count: int):
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


def like_follow_post(tweets: {requests.Response}, logfile: TextIO,
                     client: requests.session, api: tweepy.API, tweet_run: int, used_tweets: TextIO):
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
            random_tweet(logfile=logfile, api=api, used_file=used_tweets)
        except Exception as oops:
            message = f"[OOPS] -- {oops} -- {right_now()}"
            report(message=message, logfile=logfile)


def log_next_run(logfile: TextIO, tweet_run: int):
    message = f"[INITIATE TWEET RETRIEVAL] Run {tweet_run}: 100 tweets " \
              f"(asks to continue after every 4 runs) -- {right_now()}"
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
    for word in word_filter:
        single = f' {word} '.lower()
        plural = f' {word}s '.lower()
        if single in tweet_choice:
            [].append(word.lower())
        elif plural in tweet_choice:
            [].append(f"{word}s".lower())
    return []


def aux_verb_hash(tweet_choice: str) -> list[str]:
    for a_verb in auxiliary_verbs:
        isolated = f" {a_verb} ".lower()
        pattern = r"(?:" + re.escape(isolated) + r"\: ).+\b"
        after_aux_verbs = re.findall(pattern=pattern, string=tweet_choice)
        for word in after_aux_verbs:
            [].append(word.lower())
    return []


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
                report(message="[RANDOM TWEET POSTED]:\n")
                message = f"{tweet_choice}\n\n".lower()
                for hashtag in hashes:
                    message += f"#{hashtag} ".lower()
                api.update_status(message)
                used_file.write(f"{tweet_choice}\n")
                report(message=message, logfile=logfile)
            except Exception as oops:
                message = f"[OOPS] -- {oops} -- {right_now()}"
                report(message=message, logfile=logfile)


def main(followers: list[int], following: list[int], logfile: TextIO,
         client: requests.session, api: tweepy.API, query: str, tweet_run: int, used_tweets: TextIO):
    try:
        follow_back(followers=followers, following=following, logfile=logfile, client=client, api=api)
    except Exception as oops:
        message = f"[OOPS] -- {oops} -- {right_now()}"
        report(message=message, logfile=logfile)
    for i in range(0, 4):
        tweets = client.search_recent_tweets(query=query, tweet_fields=['context_annotations', 'created_at'],
                                             expansions=['entities.mentions.username', 'author_id'],
                                             user_fields=['username'], max_results=100)
        like_follow_post(tweets=tweets, logfile=logfile, client=client, api=api,
                         tweet_run=tweet_run, used_tweets=used_tweets)
        tweet_run += 1
