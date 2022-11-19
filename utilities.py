import string
import time
import datetime
import requests
import tweepy
import re

from random import randint
from typing import TextIO

from word_lists import nouns, verbs, auxiliary_verbs, ice_breakers


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
            message = f"[RANDOMLY FOLLOWED AUTHOR] -- author: {author} -- {right_now()}"
        else:
            message = f"[NO RANDOM FOLLOW] -- author: {author} -- {right_now()}"
        report(message=message, logfile=logfile)
    except Exception as oops:
        message = f"[OOPS] -- {oops} -- {right_now()}"
        report(message=message, logfile=logfile)


def follow_follower(client, follower, api, follower_index, followers, logfile):
    try:
        client.follow_user(follower)
        message = f"[FOLLOW BACK] -- now following: " \
                  f"{api.get_user(user_id=follower).screen_name} -- {right_now()}\n" \
                  f"follower index {follower_index} out of {len(followers)}"
        report(message=message, logfile=logfile)
    except Exception as oops:
        message = f"[OOPS] -- {oops} -- {right_now()}"
        report(message=message, logfile=logfile)


def follow_back(followers: list, following: list, logfile: TextIO, client: requests.session, api: tweepy.API):
    follower_index = 0
    while follower_index <= len(followers)-1:
        follower = followers[follower_index]
        if follower not in following:
            try:
                follow_follower(client, follower, api, follower_index, followers, logfile)
            except Exception as error:
                message = f"ZACH -- ERROR FOLLOWING A USER {api.get_user(user_id=follower).screen_name}\n" \
                      f"follower index {follower_index+1} out of {len(followers)}"
                report(message, logfile)

        else:
            message = f"[NO FOLLOW] -- already following {api.get_user(user_id=follower).screen_name}\n" \
                      f"follower index {follower_index+1} out of {len(followers)}"
            report(message=message, logfile=logfile)
        report("-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~", logfile)
        follower_index += 1


def maybe_like_and_report(client: requests.session, tweet: tweepy.Tweet,
                          logfile: TextIO, tweet_run: int, tweet_count: int):
    maybe = randint(1, 2)
    if maybe == 2:
        client.like(tweet.id)
        message = f"[LIKED TWEET] #: {tweet_count} of 100; run: {tweet_run}.\n\n" \
                  f"{tweet.text}\n\n" \
                  f"[TIME]: {right_now()}"
    else:
        message = f"[DID NOT LIKE TWEET] #: {tweet_count} of 100; run: {tweet_run}.\n" \
                  f"[TIME]: {right_now()}"
    report(message=message, logfile=logfile)


def like_follow_post(tweets: {requests.Response}, logfile: TextIO,
                     client: requests.session, api: tweepy.API, tweet_run: int, name: str):
    tweet_count = 1
    for tweet in tweets.data:
        try:
            random_tweet(logfile=logfile, api=api, name=name)
        except Exception as oops:
            message = f"[OOPS] -- {oops} -- {right_now()}"
            report(message=message, logfile=logfile)
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
        report("-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~", logfile)


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


def build_hashtags(tweet_choice: str) -> list[str]:
    tweet_choice = tweet_choice.translate(str.maketrans('', '', string.punctuation))
    hashes = []
    for noun in nouns:
        single = f' {noun} '.lower()
        plural = f' {noun}s '.lower()
        if single in tweet_choice:
            hashes.append(noun.lower())
        if plural in tweet_choice:
            hashes.append(f"{noun}s".lower())
        if tweet_choice.endswith(f" {noun.lower()}"):
            hashes.append(noun.lower())
    for verb in verbs:
        single = f' {verb} '.lower()
        plural = f' {verb}s '.lower()
        ing = f' {verb}ing '.lower()
        if single in tweet_choice:
            hashes.append(verb.lower())
        if plural in tweet_choice:
            hashes.append(f"{verb}s".lower())
        if ing in tweet_choice:
            hashes.append(f' {verb}ing '.lower())
        if tweet_choice.endswith(f" {verb.lower()}"):
            hashes.append(verb.lower())
    for a_verb in auxiliary_verbs:
        isolated = f" {a_verb} ".lower()
        pattern = r"(?:" + re.escape(isolated) + r"\: ).+\b"
        after_aux_verbs = re.findall(pattern=pattern, string=tweet_choice)
        for word in after_aux_verbs:
            hashes.append(word.lower())
    return hashes


def random_tweet(logfile: TextIO, api: tweepy.API, name):
    tweet_chance = randint(1, 10000)
    if tweet_chance == 42:
        tweet_roll = randint(1, len(ice_breakers))
        tweet_choice = ice_breakers[tweet_roll]
        used_file = open(f'logs/{name}_used_tweets.txt', 'w+')
        if tweet_choice not in used_file:
            try:
                tweet_choice = tweet_choice.lower()
                hashes = build_hashtags(tweet_choice)
                hashes = [*set(hashes)]
                report(message="[RANDOM TWEET POSTED]:\n", logfile=logfile)
                message = f"{tweet_choice}\n\n".lower()
                for hashtag in hashes:
                    message += f"#{hashtag} ".lower()
                api.update_status(message)
                used_file.write(f"'{tweet_choice}',\n")
                used_file.close()
                reported_tweet = f"\n\n{message}\n\n"
                report(message=reported_tweet, logfile=logfile)
            except Exception as oops:
                message = f"[OOPS] -- {oops} -- {right_now()}"
                used_file.close()
                report(message=message, logfile=logfile)
    else:
        message = f"[NO RANDOM TWEET]"
        report(message, logfile)


def main(followers: list[int], following: list[int], logfile: TextIO,
         client: requests.session, api: tweepy.API, query: str, tweet_run: int, name: str):
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
                         tweet_run=tweet_run, name=name)
        tweet_run += 1
    return tweet_run
