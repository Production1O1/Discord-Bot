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


