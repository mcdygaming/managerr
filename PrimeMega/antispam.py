from PrimeMega import DEV_USERS, dispatcher, OWNER_ID

Owner = OWNER_ID
NoResUser = [OWNER_ID, 777000, DEV_USERS]
AntiSpamValue = 25

GLOBAL_USER_DATA = {}


def antispam_restrict_user(user_id, time):
    if user_id in NoResUser:
        return True
    if GLOBAL_USER_DATA.get(user_id):
        if GLOBAL_USER_DATA.get(user_id).get("AntiSpamHard"):
            if GLOBAL_USER_DATA.get(user_id).get("AntiSpamHard").get("restrict"):
                return True
    try:
        number = GLOBAL_USER_DATA["AntiSpam"][user_id]["value"]
        status = GLOBAL_USER_DATA["AntiSpam"][user_id]["status"]
        restime = GLOBAL_USER_DATA["AntiSpam"][user_id]["restrict"]
        level = GLOBAL_USER_DATA["AntiSpam"][user_id]["level"]
    except:
        number = 0
        status = False
        restime = None
        level = 1
    if status:
        if restime:
            if int(time) <= int(restime):
                return False
    if restime:
        if int(time) <= int(restime):
            number += 1
    if number >= int(AntiSpamValue * level):
        status = True
        restrict_time = int(time) + (60 * (number / AntiSpamValue))
    else:
        status = False
        restrict_time = int(time) + AntiSpamValue
    GLOBAL_USER_DATA["AntiSpam"] = {
        user_id: {
            "status": status,
            "user": user_id,
            "value": number,
            "restrict": restrict_time,
            "level": level,
        }
    }


def antispam_cek_user(user_id, time):
    try:
        value = GLOBAL_USER_DATA["AntiSpam"]
        if value.get(user_id):
            value = GLOBAL_USER_DATA["AntiSpam"][user_id]
            if value["restrict"]:
                if int(time) >= int(value["restrict"]):
                    if value["status"]:
                        value["status"] = False
                        value["level"] += 1
                        value["restrict"] = 0
                    else:
                        value["value"] = 2 * int(value["level"])
                else:
                    if value["status"]:
                        try:
                            number = GLOBAL_USER_DATA["AntiSpamHard"][user_id]["value"]
                            status = GLOBAL_USER_DATA["AntiSpamHard"][user_id]["status"]
                            restime = GLOBAL_USER_DATA["AntiSpamHard"][user_id][
                                "restrict"
                            ]
                            level = GLOBAL_USER_DATA["AntiSpamHard"][user_id]["level"]
                        except:
                            number = 0
                            status = False
                            restime = None
                            level = 1
                        if status is False:
                            if number >= 5:
                                restrict_time = int(time) + 3600
                                status = True
                                GLOBAL_USER_DATA["AntiSpam"] = {
                                    user_id: {
                                        "status": status,
                                        "user": user_id,
                                        "value": GLOBAL_USER_DATA["AntiSpam"][user_id][
                                            "value"
                                        ],
                                        "restrict": restrict_time,
                                        "level": GLOBAL_USER_DATA["AntiSpam"][user_id][
                                            "level"
                                        ],
                                    }
                                }
                            else:
                                restrict_time = None
                                number += 1
                        else:
                            dispatcher.bot.sendMessage(
                                Owner,
                                "⚠ Alert: user `{}` was detected spam.".format(user_id),
                                parse_mode="markdown",
                            )
                            GLOBAL_USER_DATA["AntiSpamHard"] = {
                                user_id: {
                                    "status": False,
                                    "user": user_id,
                                    "value": 0,
                                    "restrict": restime,
                                    "level": level,
                                }
                            }
                            return value
                        GLOBAL_USER_DATA["AntiSpamHard"] = {
                            user_id: {
                                "status": status,
                                "user": user_id,
                                "value": number,
                                "restrict": restrict_time,
                                "level": level,
                            }
                        }
            return value
        else:
            return {
                "status": False,
                "user": user_id,
                "value": 0,
                "restrict": None,
                "level": 1,
            }
    except KeyError:
        return {
            "status": False,
            "user": user_id,
            "value": 0,
            "restrict": None,
            "level": 1,
        }


def check_user_spam(user_id):
    if GLOBAL_USER_DATA.get("AntiSpam"):
        if GLOBAL_USER_DATA["AntiSpam"].get(user_id):
            status = GLOBAL_USER_DATA["AntiSpam"].get(user_id).get("status")
        else:
            status = False
    else:
        status = False
    if GLOBAL_USER_DATA.get("AntiSpamHard"):
        if GLOBAL_USER_DATA["AntiSpamHard"].get(user_id):
            status_hard = GLOBAL_USER_DATA["AntiSpamHard"].get(user_id).get("status")
        else:
            status_hard = False
    else:
        status_hard = False
    return {"status": status, "status_hard": status_hard}


# This is will detect user
def detect_user(user_id, chat_id, message, parsing_date):
    check_spam = antispam_cek_user(user_id, parsing_date)
    check_user = check_user_spam(user_id)
    if check_spam["status"]:
        if check_user["status_hard"]:
            getbotinfo = dispatcher.bot.getChatMember(chat_id, dispatcher.bot.id)
            try:
                if getbotinfo.status in ("administrator", "creator"):
                    dispatcher.bot.kickChatMember(chat_id, user_id)
                    dispatcher.bot.sendMessage(
                        chat_id,
                        "I've banned this spammer!",
                        reply_to_message_id=message.message_id,
                    )
                    return True
            except:
                pass
            if message.chat.type != "private":
                dispatcher.bot.sendMessage(
                    chat_id,
                    "Flood was detected!\nI'm out, invite me again when admins stop flooding.\n\nThanks.",
                )
                dispatcher.bot.leaveChat(chat_id)
                return True
        dispatcher.bot.sendMessage(
            chat_id,
            "Alert! This user triggered my Antispam algorithm and will be restricted for a while.\n\nIf this continues I will ban and create a spam report for this user!",
            reply_to_message_id=message.message_id,
        )
        return True
