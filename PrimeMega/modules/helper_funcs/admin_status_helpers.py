# admin status module by Luke (@itsLuuke - t.me/itsLuuke)
# written for OdinRobot
# copyright 2022
# this module contains various helper functions/classes to help with the admin status module

from enum import Enum
from cachetools import TTLCache

from telegram import (
  InlineKeyboardMarkup,
  InlineKeyboardButton,
  ParseMode,
  Message,
)
from PrimeMega import (
  OWNER_ID,
  DEV_USERS,
  DRAGONS,
  DEMONS,
  TIGERS,
  WOLVES,
  SPAMMERS,
)

# stores admin in memory for 10 min.
ADMINS_CACHE = TTLCache(maxsize=512, ttl=60 * 30)

# stores bot admin status in memory for 10 min.
BOT_ADMIN_CACHE = TTLCache(maxsize=512, ttl=60 * 30)
DEV_USERS = DEV_USERS
SUDO_USERS = DRAGONS
WHITELIST_USERS = WOLVES
SUPPORT_USERS = TIGERS
MOD_USERS = DEMONS


class AdminPerms(Enum):
    CAN_RESTRICT_MEMBERS = "can_restrict_members"
    CAN_PROMOTE_MEMBERS = "can_promote_members"
    CAN_INVITE_USERS = "can_invite_users"
    CAN_DELETE_MESSAGES = "can_delete_messages"
    CAN_CHANGE_INFO = "can_change_info"
    CAN_PIN_MESSAGES = "can_pin_messages"
    IS_ANONYMOUS = "is_anonymous"


class ChatStatus(Enum):
    CREATOR = "creator"
    ADMIN = "administrator"


def anon_reply_markup(cb_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(text="Prove identity", callback_data=cb_id)]]
    )


anon_reply_text = (
    "Seems like you're anonymous, click the button below to prove your identity"
)


def edit_anon_msg(msg: Message, text: str):
    """
    edit anon check message and remove the button
    """
    msg.edit_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=None)


def user_is_not_admin_errmsg(
    message: Message, permission: AdminPerms = None, noreply: bool = False
):
    errmsg = (
        f"You lack the following permission for this command:\n`{permission.value}`!"
    )
    if noreply:
        return message.callback_query.answer(errmsg, show_alert=True)
    return message.reply_text(errmsg, parse_mode=ParseMode.MARKDOWN)


anon_callbacks = {}
