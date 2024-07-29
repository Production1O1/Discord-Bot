import shutil

import datetime, glob, json, os, random, requests, string
from pathlib import Path
import config

from cogs.exceptions import APIException
from cogs.request_generator import make_discord_users_request, make_users_request, make_active_bots_request, \
    make_unlinked_discord_uids_request

# [name str] => bot id
bot_ids = {}

# [ai arena id] => [user name, True]
# [user name, discord linked = false]
# [discord id, discord linked = True]
author_names = {}


def get_patreon_users():
    request_url = make_users_request()
    response = requests.get(request_url, headers=config.AUTH)
    if response.status_code != 200:
        raise APIException("Could not users!", request_url, response)
    users = json.loads(response.text)["results"]
    patrean_users = []
    for user in users:
        if user["patreon_level"] != "none":
            patrean_users.append(user["id"])

    return patrean_users



def get_patreon_unlinked_uids():
    request_url = make_unlinked_discord_uids_request()
    response = requests.get(request_url, headers=config.AUTH)
    if response.status_code != 200:
        raise APIException("Could not get unlinked discord uids!", request_url, response)
    results = json.loads(response.text)["results"]
    discord_uids = []
    for uid in results:
        discord_uids.append(uid["discord_uid"])

    return discord_uids


def get_bot_author_users():
    request_url = make_active_bots_request()
    response = requests.get(request_url, headers=config.AUTH)
    if response.status_code != 200:
        raise APIException("Could not retrieve top 10 bots!", request_url, response)
    bots = json.loads(response.text)["results"]

    active_bot_ids = []
    for bot in bots:
        active_bot_ids.append(bot["bot"])
    active_bot_author_ids = set()
    for bot_id in active_bot_ids:
        request_url = f"{config.BOT_INFO}{bot_id}/"
        response = requests.get(request_url, headers=config.AUTH)
        if response.status_code != 200:
            raise APIException(f"A bot with id {bot_id} could not be located.", request_url, response)
        bot_info = json.loads(response.text)
        active_bot_author_ids.add(bot_info["user"])

    return active_bot_author_ids




def get_discord_users():
    request_url = make_discord_users_request()
    response = requests.get(request_url, headers=config.AUTH)
    if response.status_code != 200:
        raise APIException("Could not retrieve discord users", request_url, response)
    users = json.loads(response.text)["results"]
    discord_users = {}
    for user in users:
        discord_users[user["user"]] = user["uid"]

    return discord_users


def get_author_name_by_id(user_id: str):
    if user_id not in author_names.keys():
        request_url = f"{config.DISCORD_USER_INFO}?user={user_id}"
        response = requests.get(request_url, headers=config.AUTH)
        user = json.loads(response.text)
        if response.status_code != 200 or len(user["results"]) == 0:
            print(f"AI Arena id {user_id} does not have a linked discord account, "
                  f"falling back to getting ai arena name", request_url, response)
            request_url = f"{config.USER_INFO}/{user_id}"
            response = requests.get(request_url, headers=config.AUTH)
            if response.status_code != 200:
                raise APIException(f"An AI Arena user with id {user_id} could not be found. CRITICAL ERROR,"
                                   f"this ID is tied to a bot, but the id doesn't exist", request_url, response)
            user = json.loads(response.text)
            author_names[user_id] = [user["username"], False]
            print(author_names[user_id])
            return author_names[user_id]
        # discord id exists
        else:
            author_names[user_id] = [user["results"][0]["uid"], False]
            author_names[user_id][1] = True
    return author_names[user_id]


def get_bot_id_by_name(bot_name: str):
    if bot_name not in bot_ids.keys():
        request_url = f"{config.BOT_INFO}?name={bot_name}"
        response = requests.get(request_url, headers=config.AUTH)
        if response.status_code != 200:
            raise APIException(f"A bot with the name {bot_name} could not be located.", request_url, response)
        bot = json.loads(response.text)
        if len(bot["results"]) == 0:
            raise APIException(f"A bot with the name {bot_name} could not be located.", request_url, response)
        bot_ids[bot_name] = bot["results"][0]["id"]
    return bot_ids[bot_name]


def get_bot_info(bot_id: str) -> dict:
    request_url = f"{config.BOT_INFO}{bot_id}/"
    response = requests.get(request_url, headers=config.AUTH)
    if response.status_code != 200:
        raise APIException(f"A bot with id {bot_id} could not be located.", request_url, response)
    bot_info = json.loads(response.text)
    bot_info["author_info"] = get_author_name_by_id(bot_info["user"])
    return bot_info


def download_replay(replay_file: str, won: bool, file_path: str):
    if replay_file is None:
        return False
    result = "won"
    if not won:
        result = "loss"
    response = requests.get(replay_file, headers=config.AUTH)
