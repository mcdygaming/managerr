# Create a new config.py or rename this to config.py file in same dir and import, then extend this class.
import json
import os


def get_user_list(config, key):
    with open("{}/PrimeMega/{}".format(os.getcwd(), config), "r") as json_file:
        return json.load(json_file)[key]


# Create a new config.py or rename this to config.py file in same dir and import, then extend this class.
class Config(object):
    LOGGER = True
    # REQUIRED
    # Login to https://my.telegram.org and fill in these slots with the details given by it

    API_ID = 123456  # integer value, dont use ""
    API_HASH = "awoo"
    TOKEN = "BOT_TOKEN"  # This var used to be API_KEY but it is now TOKEN, adjust accordingly.
    OWNER_ID = 1423479724  # If you dont know, run the bot and do /id in your private chat with it, also an integer
    OWNER_USERNAME = "Tonic880"
    SUPPORT_CHAT = "PrimeSupportGroup"  # Your own group for support, do not add the @
    JOIN_LOGGER = (
        -1001376025003
    )  # Prints any new group the bot is added to, prints just the name and ID.
    EVENT_LOGS = (
        -1001376025003
    )  # Prints information like gbans, sudo promotes, AI enabled disable states that may help in debugging and shit
    ERROR_LOGS = -1001376025003
    # RECOMMENDED
    SQLALCHEMY_DATABASE_URI = "something://somewhat:user@hosturl:port/databasename"  # needed for any database modules
    LOAD = []
    NO_LOAD = ["rss", "cleaner", "connection", "math"]
    WEBHOOK = False
    INFOPIC = True
    URL = None
    SPAMWATCH_API = ""  # go to support.spamwat.ch to get key
    SPAMWATCH_SUPPORT_CHAT = "@SpamWatchSupport"
    MONGO_DB_URI = "mongo+srv"
    ARQ_API = ""
    ARQ_API_KEY = ""
    ARQ_API_URL = ""
    BOT_NAME = "Prime Mega"
    BOT_USERNAME = "PrimeMegaBot"
    BOT_ID = "2109887867"
    OPENWEATHERMAP_ID = "22322"
    

    # OPTIONAL
    ##List of id's -  (not usernames) for users which have sudo access to the bot.
    DRAGONS = get_user_list("elevated_users.json", "sudos")
    ##List of id's - (not usernames) for developers who will have the same perms as the owner
    DEV_USERS = get_user_list("elevated_users.json", "devs")
    ##List of id's (not usernames) for users which are allowed to gban, but can also be banned.
    DEMONS = get_user_list("elevated_users.json", "supports")
    # List of id's (not usernames) for users which WONT be banned/kicked by the bot.
    TIGERS = get_user_list("elevated_users.json", "tigers")
    WOLVES = get_user_list("elevated_users.json", "whitelists")
    DONATION_LINK = None  # EG, paypal
    CERT_PATH = None
    PORT = 5000
    DEL_CMDS = True  # Delete commands that users dont have access to, like delete /ban if a non admin uses it.
    STRICT_GBAN = True
    WORKERS = (
        8  # Number of subthreads to use. Set as number of threads your processor uses
    )
    BAN_STICKER = ""  # banhammer marie sticker id, the bot will send this sticker before banning or kicking a user in chat.
    ALLOW_EXCL = True  # Allow ! commands as well as / (Leave this to true so that blacklist can work)
    CASH_API_KEY = (
        "awoo"  # Get your API key from https://www.alphavantage.co/support/#api-key
    )
    TIME_API_KEY = "awoo"  # Get your API key from https://timezonedb.com/api
    WALL_API = (
        "awoo"  # For wallpapers, get one from https://wall.alphacoders.com/api.php
    )
    AI_API_KEY = "awoo"  # For chatbot, get one from https://coffeehouse.intellivoid.net/dashboard
    HEROKU_API_KEY = "YES"
    REM_BG_API_KEY = "yahoo"
    LASTFM_API_KEY = "yeah"
    CF_API_KEY = "jk"
    HEROKU_APP_NAME = "siap"
    BL_CHATS = []  # List of groups that you want blacklisted.
    SPAMMERS = None
    ALLOW_CHATS = None
    MONGO_DB = "Prime"
    TEMP_DOWNLOAD_DIRECTORY = "./"
    STRING_SESSION = "1BVtsOMQBu4OWQcqgIHDD6cR-Pvu47XV69rrEZWJthenLrvB23MhDYXAC4V-EZ5XEgu6OFNtM5bFTgGVoKnuB-_s4DvoO8fx3CnoueRdwLn61Khky0aT6qiAccWN31wkG1PJfyckgV59VC0T3v-wwQV62syy3ug_7iQ4Wx8AzhCjiYah-qVcozdA8k8NsX6q5sx-sqZfpc_ZkJIyoBQyJlUwe7-v-WboR6EQAoaggIgZZHEu5L_2TDANfbE4jMqedSl6fI9sKhWjBeXKZdipbtZShAmO5uEJVS6DoMOsZiOzm-ehh2Rkc8u3OPSdf744gIi5OWulmNT6_zgnPoNs8r5gB0AH3XvA="


class Production(Config):
    LOGGER = True


class Development(Config):
    LOGGER = True
