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
