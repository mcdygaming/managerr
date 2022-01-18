import html

from telegram import ParseMode, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import BadRequest
from telegram.ext import CallbackContext, CommandHandler, Filters, run_async
from telegram.utils.helpers import mention_html

from PrimeMega import DRAGONS, dispatcher
from PrimeMega.modules.disable import DisableAbleCommandHandler
from PrimeMega.modules.helper_funcs.chat_status import (
    bot_admin,
    can_pin,
    can_promote,
    connection_status,
    user_admin,
    ADMIN_CACHE,
)

from PrimeMega.modules.helper_funcs.admin_rights import user_can_changeinfo, user_can_promote
from PrimeMega.modules.helper_funcs.extraction import (
    extract_user,
    extract_user_and_text,
)
from PrimeMega.modules.log_channel import loggable
from PrimeMega.modules.helper_funcs.alternate import send_message
from PrimeMega.modules.language import gs


@bot_admin
@user_admin
def set_sticker(update: Update, context: CallbackContext):
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    if user_can_changeinfo(chat, user, context.bot.id) is False:
        return msg.reply_text(text=gs(chat_id, "user_change_info").format(html.escape(chat.title)))

    if msg.reply_to_message:
        if not msg.reply_to_message.sticker:
            return msg.reply_text(text=gs(chat_id, "set_sticker").format(html.escape(chat.title)))
        stkr = msg.reply_to_message.sticker.set_name
        try:
            context.bot.set_chat_sticker_set(chat.id, stkr)
            msg.reply_text(text=gs(chat_id, "set_sticker_success").format(html.escape(chat.title)))
        except BadRequest as excp:
            if excp.message == "Participants_too_few":
                return msg.reply_text(text=gs(chat.id, "set_sticker_restrictions").format(html.escape(chat.tittle)))
            msg.reply_text(text=gs(chat.id, "set_error").format(html.escape(chat.title)))
    else:
        msg.reply_text(text=gs(chat_id, "set_sticker").format(html.escape(chat.title)))
       
    
@bot_admin
@user_admin
def setchatpic(update: Update, context: CallbackContext):
    chat = update.effective_chat
    msg = update.effective_message
    user = update.effective_user

    if user_can_changeinfo(chat, user, context.bot.id) is False:
        msg.reply_text(text=gs(chat_id, "user_change_info").format(html.escape(chat.title)))
        return

    if msg.reply_to_message:
        if msg.reply_to_message.photo:
            pic_id = msg.reply_to_message.photo[-1].file_id
        elif msg.reply_to_message.document:
            pic_id = msg.reply_to_message.document.file_id
        else:
            msg.reply_text(text=gs(chat_id, "set_chatpic").format(html.escape(chat.title)))
            return
        dlmsg = msg.reply_text(text=gs(chat_id, "set_chatpic_loading").format(html.escape(chat.title)))
        tpic = context.bot.get_file(pic_id)
        tpic.download("gpic.png")
        try:
            with open("gpic.png", "rb") as chatp:
                context.bot.set_chat_photo(int(chat.id), photo=chatp)
                msg.reply_text(text=gs(chat_id, "set_chatpic_success").format(html.escape(chat.title)))
        except BadRequest as excp:
            msg.reply_text(text=gs(chat.id, "set_error").format(html.escape(chat.title)))
        finally:
            dlmsg.delete()
            if os.path.isfile("gpic.png"):
                os.remove("gpic.png")
    else:
        msg.reply_text(text=gs(chat.id, "set_chatpic_none").format(html.escape(chat.title)))
        
@bot_admin
@user_admin
def rmchatpic(update: Update, context: CallbackContext):
    chat = update.effective_chat
    msg = update.effective_message
    user = update.effective_user

    if user_can_changeinfo(chat, user, context.bot.id) is False:
        msg.reply_text(text=gs(chat.id, "rm_chatpic").format(html.escape(chat.title)))
        return
    try:
        context.bot.delete_chat_photo(int(chat.id))
        msg.reply_text(text=gs(chat.id, "rm_chatpic_success").format(html.escape(chat.title)))
    except BadRequest as excp:
        msg.reply_text(text=gs(chat.id, "set_error").format(html.escape(chat.title)))
        return
    
@bot_admin
@user_admin
def set_desc(update: Update, context: CallbackContext):
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    if user_can_changeinfo(chat, user, context.bot.id) is False:
        return msg.reply_text(text=gs(chat_id, "user_change_info").format(html.escape(chat.title)))

    tesc = msg.text.split(None, 1)
    if len(tesc) >= 2:
        desc = tesc[1]
    else:
        return msg.reply_text(text=gs(chat_id, "set_desc").format(html.escape(chat.title)))
    try:
        if len(desc) > 255:
            return msg.reply_text(text=gs(chat_id, "set_desc_len").format(html.escape(chat.title)))
        context.bot.set_chat_description(chat.id, desc)
        msg.reply_text(text=gs(chat_id, "set_desc_success").format(html.escape(chat.title)))
    except BadRequest as excp:
        msg.reply_text(text=gs(chat_id, "set_error").format(html.escape(chat.title)))        
        
@bot_admin
@user_admin
def setchat_title(update: Update, context: CallbackContext):
    chat = update.effective_chat
    msg = update.effective_message
    user = update.effective_user
    args = context.args

    if user_can_changeinfo(chat, user, context.bot.id) is False:
        msg.reply_text(text=gs(chat_id, "user_change_info").format(html.escape(chat.title)))
        return

    title = " ".join(args)
    if not title:
        msg.reply_text(text=gs(chat_id, "set_chat_title").format(html.escape(chat.title)))
        return

    try:
        context.bot.set_chat_title(int(chat.id), str(title))
        msg.reply_text(text=gs(chat_id, "set_chat_title_success").format(html.escape(chat.title)),
                      parse_mode=ParseMode.HTML,
                      )
    except BadRequest as excp:
        msg.reply_text(text=gs(chat_id, "set_error").format(html.escape(chat.title)))
        return
        
        
@connection_status
@bot_admin
@can_promote
@user_admin
@loggable
def promote(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    args = context.args

    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    promoter = chat.get_member(user.id)

    if (
        not (promoter.can_promote_members or promoter.status == "creator")
        and user.id not in DRAGONS
    ):
        message.reply_text(text=gs(chat_id, "promote_creator").format(html.escape(chat.title)))
        return

    user_id = extract_user(message, args)

    if not user_id:
        message.reply_text(text=gs(chat_id, "promote_id_error").format(html.escape(chat.title)))
        return

    try:
        user_member = chat.get_member(user_id)
    except:
        return

    if user_member.status in ('administrator', 'creator'):
        message.reply_text(text=gs(chat_id, "promote_admin").format(html.escape(chat.title)))
        return

    if user_id == bot.id:
        message.reply_text(text=gs(chat_id, "promote_self").format(html.escape(chat.title)))
        return

    # set same perms as bot - bot can't assign higher perms than itself!
    bot_member = chat.get_member(bot.id)

    try:
        bot.promoteChatMember(
            chat.id,
            user_id,
            can_change_info=bot_member.can_change_info,
            can_post_messages=bot_member.can_post_messages,
            can_edit_messages=bot_member.can_edit_messages,
            can_delete_messages=bot_member.can_delete_messages,
            can_invite_users=bot_member.can_invite_users,
            # can_promote_members=bot_member.can_promote_members,
            can_restrict_members=bot_member.can_restrict_members,
            can_pin_messages=bot_member.can_pin_messages,
        )
    except BadRequest as err:
        if err.message == "User_not_mutual_contact":
            message.reply_text(text=gs(chat_id, "promote_error1").format(html.escape(chat.title)))
        else:
            message.reply_text(text=gs(chat_id, "promote_error2").format(html.escape(chat.title)))
        return

    bot.sendMessage(text=gs(chat_id, "promote_success").format(html.escape(chat.title)),
                   parse_mode=ParseMode.HTML,
                   )
    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#PROMOTED\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>User:</b> {mention_html(user_member.user.id, user_member.user.first_name)}"
    )

    return log_message


@connection_status
@bot_admin
@can_promote
@user_admin
@loggable
def fullpromote(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    args = context.args

    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    promoter = chat.get_member(user.id)

    if (
        not (promoter.can_promote_members or promoter.status == "creator")
        and user.id not in DRAGONS
    ):
        message.reply_text(text=gs(chat_id, "promote_creator").format(html.escape(chat.title)))
        return

    user_id = extract_user(message, args)

    if not user_id:
        message.reply_text(text=gs(chat_id, "promote_id_error").format(html.escape(chat.title)))
        return

    try:
        user_member = chat.get_member(user_id)
    except:
        return

    if user_member.status in ('administrator', 'creator'):
        message.reply_text(text=gs(chat_id, "promote_admin").format(html.escape(chat.title)))
        return

    if user_id == bot.id:
        message.reply_text(text=gs(chat_id, "promote_self").format(html.escape(chat.title)))
        return

    # set same perms as bot - bot can't assign higher perms than itself!
    bot_member = chat.get_member(bot.id)

    try:
        bot.promoteChatMember(
            chat.id,
            user_id,
            can_change_info=bot_member.can_change_info,
            can_post_messages=bot_member.can_post_messages,
            can_edit_messages=bot_member.can_edit_messages,
            can_delete_messages=bot_member.can_delete_messages,
            can_invite_users=bot_member.can_invite_users,
            can_promote_members=bot_member.can_promote_members,
            can_restrict_members=bot_member.can_restrict_members,
            can_pin_messages=bot_member.can_pin_messages,
            can_manage_voice_chats=bot_member.can_manage_voice_chats,
        )
    except BadRequest as err:
        if err.message == "User_not_mutual_contact":
            message.reply_text(text=gs(chat_id, "promote_error1").format(html.escape(chat.title)))
        else:
            message.reply_text(text=gs(chat_id, "promote_error2").format(html.escape(chat.title)))
        return

    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton(
            "Demote", callback_data="demote_({})".format(user_member.user.id))
    ]])

    bot.sendMessage(text=gs(chat_id, "full_promote_success").format(html.escape(chat.title)),
                   parse_mode=ParseMode.HTML,
                   )
    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#FULLPROMOTED\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>User:</b> {mention_html(user_member.user.id, user_member.user.first_name)}"
    )

    return log_message


@connection_status
@bot_admin
@can_promote
@user_admin
@loggable
def demote(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    args = context.args

    chat = update.effective_chat
    message = update.effective_message
    user = update.effective_user

    user_id = extract_user(message, args)
    if not user_id:
        message.reply_text(text=gs(chat_id, "promote_id_error").format(html.escape(chat.title)))
        return

    try:
        user_member = chat.get_member(user_id)
    except:
        return

    if user_member.status == "creator":
        message.reply_text(text=gs(chat_id, "demote_creator").format(html.escape(chat.title)))
        return

    if not user_member.status == "administrator":
        message.reply_text(text=gs(chat_id, "demote_admin").format(html.escape(chat.title)))
        return

    if user_id == bot.id:
        message.reply_text(text=gs(chat_id, "demote_self").format(html.escape(chat.title)))
        return

    try:
        bot.promoteChatMember(
            chat.id,
            user_id,
            can_change_info=False,
            can_post_messages=False,
            can_edit_messages=False,
            can_delete_messages=False,
            can_invite_users=False,
            can_restrict_members=False,
            can_pin_messages=False,
            can_promote_members=False,
            can_manage_voice_chats=False,
        )

        bot.sendMessage(text=gs(chat_id, "demote_success").format(html.escape(chat.title)),
                       parse_mode=ParseMode.HTML,
                       )
        log_message = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#DEMOTED\n"
            f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
            f"<b>User:</b> {mention_html(user_member.user.id, user_member.user.first_name)}"
        )

        return log_message
    except BadRequest:
        message.reply_text(text=gs(chat_id, "demote_error").format(html.escape(chat.title)))
        return


@user_admin
def refresh_admin(update, _):
    try:
        ADMIN_CACHE.pop(update.effective_chat.id)
    except KeyError:
        pass

    update.effective_message.reply_text(text=gs(chat_id, "admin_refresh").format(html.escape(chat.title)))


@connection_status
@bot_admin
@can_promote
@user_admin
def set_title(update: Update, context: CallbackContext):
    bot = context.bot
    args = context.args

    chat = update.effective_chat
    message = update.effective_message

    user_id, title = extract_user_and_text(message, args)
    try:
        user_member = chat.get_member(user_id)
    except:
        return

    if not user_id:
        message.reply_text(text=gs(chat_id, "promote_id_error").format(html.escape(chat.title)))
        return

    if user_member.status == "creator":
        message.reply_text(text=gs(chat_id, "set_title_creator").format(html.escape(chat.title)))
        return

    if user_member.status != "administrator":
        message.reply_text(text=gs(chat_id, "set_title_admin").format(html.escape(chat.title)))
        return

    if user_id == bot.id:
        message.reply_text(text=gs(chat_id, "set_title_self").format(html.escape(chat.title)))
        return

    if not title:
        message.reply_text(text=gs(chat_id, "set_title_none").format(html.escape(chat.title)))
        return

    if len(title) > 16:
        message.reply_text(text=gs(chat_id, "set_title_len").format(html.escape(chat.title)))

    try:
        bot.setChatAdministratorCustomTitle(chat.id, user_id, title)
    except BadRequest:
        message.reply_text(text=gs(chat_id, "set_title_error").format(html.escape(chat.title)))
        return

    bot.sendMessage(text=gs(chat_id, "set_title_success").format(html.escape(chat.title)),
                   parse_mode=ParseMode.HTML,
                   )

@bot_admin
@can_pin
@user_admin
@loggable
def pin(update: Update, context: CallbackContext) -> str:
    bot, args = context.bot, context.args
    user = update.effective_user
    chat = update.effective_chat
    msg = update.effective_message
    msg_id = msg.reply_to_message.message_id if msg.reply_to_message else msg.message_id

    if msg.chat.username:
        # If chat has a username, use this format
        link_chat_id = msg.chat.username
        message_link = f"https://t.me/{link_chat_id}/{msg_id}"
    elif (str(msg.chat.id)).startswith("-100"):
        # If chat does not have a username, use this
        link_chat_id = (str(msg.chat.id)).replace("-100", "")
        message_link = f"https://t.me/c/{link_chat_id}/{msg_id}"

    is_group = chat.type not in ("private", "channel")
    prev_message = update.effective_message.reply_to_message

    if prev_message is None:
        msg.reply_text(text=gs(chat_id, "pin_none").format(html.escape(chat.title)))
        return

    is_silent = True
    if len(args) >= 1:
        is_silent = (
            args[0].lower() != "notify"
            or args[0].lower() == "loud"
            or args[0].lower() == "violent"
        )

    if prev_message and is_group:
        try:
            bot.pinChatMessage(
                chat.id, prev_message.message_id, disable_notification=is_silent
            )
            msg.reply_text(text=gs(chat_id, "pin_none").format(html.escape(chat.title)),
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text=gs(chat.id, "pin_button"), url=f"{message_link}")
                        ]
                    ]
                ), 
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
            )
        except BadRequest as excp:
            if excp.message != "Chat_not_modified":
                raise

        log_message = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"MESSAGE-PINNED-SUCCESSFULLY\n"
            f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}"
        )

        return log_message


@bot_admin
@can_pin
@user_admin
@loggable
def unpin(update: Update, context: CallbackContext):
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message
    msg_id = msg.reply_to_message.message_id if msg.reply_to_message else msg.message_id
    unpinner = chat.get_member(user.id)

    if (
        not (unpinner.can_pin_messages or unpinner.status == "creator")
        and user.id not in DRAGONS
    ):
        message.reply_text(text=gs(chat_id, "promote_creator").format(html.escape(chat.title)))
        return

    if msg.chat.username:
        # If chat has a username, use this format
        link_chat_id = msg.chat.username
        message_link = f"https://t.me/{link_chat_id}/{msg_id}"
    elif (str(msg.chat.id)).startswith("-100"):
        # If chat does not have a username, use this
        link_chat_id = (str(msg.chat.id)).replace("-100", "")
        message_link = f"https://t.me/c/{link_chat_id}/{msg_id}"

    is_group = chat.type not in ("private", "channel")
    prev_message = update.effective_message.reply_to_message

    if prev_message and is_group:
        try:
            context.bot.unpinChatMessage(
                chat.id, prev_message.message_id
            )
            msg.reply_text(text=gs(chat_id, "unpin_success").format(html.escape(chat.title)),
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
            )
        except BadRequest as excp:
            if excp.message != "Chat_not_modified":
                raise

    if not prev_message and is_group:
        try:
            context.bot.unpinChatMessage(chat.id)
            msg.reply_text(text=gs(chat_id, "unpin_last_msg").format(html.escape(chat.title)))
        except BadRequest as excp:
            if excp.message == "Message to unpin not found":
               msg.reply_text(text=gs(chat_id, "unpin_error").format(html.escape(chat.title)))
            else:
                raise

    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"MESSAGE-UNPINNED-SUCCESSFULLY\n"
        f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}"
    )

    return log_message


@bot_admin
def pinned(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    msg = update.effective_message
    msg_id = (
        update.effective_message.reply_to_message.message_id
        if update.effective_message.reply_to_message
        else update.effective_message.message_id
    )

    chat = bot.getChat(chat_id=msg.chat.id)
    if chat.pinned_message:
        pinned_id = chat.pinned_message.message_id
        if msg.chat.username:
            link_chat_id = msg.chat.username
            message_link = f"https://t.me/{link_chat_id}/{pinned_id}"
        elif (str(msg.chat.id)).startswith("-100"):
            link_chat_id = (str(msg.chat.id)).replace("-100", "")
            message_link = f"https://t.me/c/{link_chat_id}/{pinned_id}"

        msg.reply_text(text=gs(chat_id, "pinned").format(html.escape(chat.title)),
            reply_to_message_id=msg_id,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text=gs(chat.id, "pin_button"), url=f"https://t.me/{link_chat_id}/{pinned_id}"),
                    ]
                ]
            ),
        )

    else:
        msg.reply_text(text=gs(chat_id, "pinned_none").format(html.escape(chat.title)),
            parse_mode=ParseMode.HTML,
        )

@bot_admin
@user_admin
@connection_status
def invite(update: Update, context: CallbackContext):
    bot = context.bot
    chat = update.effective_chat

    if chat.username:
        update.effective_message.reply_text(f"https://t.me/{chat.username}")
    elif chat.type in [chat.SUPERGROUP, chat.CHANNEL]:
        bot_member = chat.get_member(bot.id)
        if bot_member.can_invite_users:
            invitelink = bot.exportChatInviteLink(chat.id)
            update.effective_message.reply_text(invitelink)
        else:
            update.effective_message.reply_text(text=gs(chat_id, "invite_error1").format(html.escape(chat.title)))
    else:
        update.effective_message.reply_text(text=gs(chat_id, "invite_error2").format(html.escape(chat.title)))


@bot_admin
@can_promote
@user_admin
@loggable
def button(update: Update, context: CallbackContext) -> str:
    query: Optional[CallbackQuery] = update.callback_query
    user: Optional[User] = update.effective_user
    bot: Optional[Bot] = context.bot
    match = re.match(r"demote_\((.+?)\)", query.data)
    if match:
        user_id = match.group(1)
        chat: Optional[Chat] = update.effective_chat
        member = chat.get_member(user_id)
        bot_member = chat.get_member(bot.id)
        bot_permissions = promoteChatMember(
            chat.id,
            user_id,
            can_change_info=bot_member.can_change_info,
            can_post_messages=bot_member.can_post_messages,
            can_edit_messages=bot_member.can_edit_messages,
            can_delete_messages=bot_member.can_delete_messages,
            can_invite_users=bot_member.can_invite_users,
            can_promote_members=bot_member.can_promote_members,
            can_restrict_members=bot_member.can_restrict_members,
            can_pin_messages=bot_member.can_pin_messages,
            can_manage_voice_chats=bot_member.can_manage_voice_chats,
        )                
        demoted = bot.promoteChatMember(
                      chat.id,
                      user_id,
                      can_change_info=False,
                      can_post_messages=False,
                      can_edit_messages=False,
                      can_delete_messages=False,
                      can_invite_users=False,
                      can_restrict_members=False,
                      can_pin_messages=False,
                      can_promote_members=False,
                      can_manage_voice_chats=False,
        )
        if demoted:
        	update.effective_message.edit_text(
        	    f"Admin {mention_html(user.id, user.first_name)} Demoted {mention_html(member.user.id, member.user.first_name)}!",
        	    parse_mode=ParseMode.HTML,
        	)
        	query.answer("Demoted!")
        	return (
                    f"<b>{html.escape(chat.title)}:</b>\n" 
                    f"#DEMOTE\n" 
                    f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
                    f"<b>User:</b> {mention_html(member.user.id, member.user.first_name)}"
                )
    else:
        update.effective_message.edit_text(
            "This user is not promoted or has left the group!"
        )
        return ""

  
def helps(chat):
    return gs(chat, "admin_help")

SET_DESC_HANDLER = CommandHandler("setdesc", set_desc, filters=Filters.chat_type.groups, run_async=True)
SET_STICKER_HANDLER = CommandHandler("setsticker", set_sticker, filters=Filters.chat_type.groups, run_async=True)
SETCHATPIC_HANDLER = CommandHandler("setgpic", setchatpic, filters=Filters.chat_type.groups, run_async=True)
RMCHATPIC_HANDLER = CommandHandler("delgpic", rmchatpic, filters=Filters.chat_type.groups, run_async=True)
SETCHAT_TITLE_HANDLER = CommandHandler("setgtitle", setchat_title, filters=Filters.chat_type.groups, run_async=True)

ADMINLIST_HANDLER = DisableAbleCommandHandler("admins", adminlist, run_async=True)

PIN_HANDLER = CommandHandler("pin", pin, filters=Filters.chat_type.groups, run_async=True)
UNPIN_HANDLER = CommandHandler("unpin", unpin, filters=Filters.chat_type.groups, run_async=True)
PINNED_HANDLER = CommandHandler("pinned", pinned, filters=Filters.chat_type.groups, run_async=True)

INVITE_HANDLER = DisableAbleCommandHandler("invitelink", invite, run_async=True)

PROMOTE_HANDLER = DisableAbleCommandHandler("promote", promote, run_async=True)
FULLPROMOTE_HANDLER = DisableAbleCommandHandler("fullpromote", fullpromote, run_async=True)
DEMOTE_HANDLER = DisableAbleCommandHandler("demote", demote, run_async=True)

SET_TITLE_HANDLER = CommandHandler("title", set_title, run_async=True)
ADMIN_REFRESH_HANDLER = CommandHandler("admincache", refresh_admin, filters=Filters.chat_type.groups, run_async=True)

dispatcher.add_handler(SET_DESC_HANDLER)
dispatcher.add_handler(SET_STICKER_HANDLER)
dispatcher.add_handler(SETCHATPIC_HANDLER)
dispatcher.add_handler(RMCHATPIC_HANDLER)
dispatcher.add_handler(SETCHAT_TITLE_HANDLER)
dispatcher.add_handler(ADMINLIST_HANDLER)
dispatcher.add_handler(PIN_HANDLER)
dispatcher.add_handler(UNPIN_HANDLER)
dispatcher.add_handler(PINNED_HANDLER)
dispatcher.add_handler(INVITE_HANDLER)
dispatcher.add_handler(PROMOTE_HANDLER)
dispatcher.add_handler(FULLPROMOTE_HANDLER)
dispatcher.add_handler(DEMOTE_HANDLER)
dispatcher.add_handler(SET_TITLE_HANDLER)
dispatcher.add_handler(ADMIN_REFRESH_HANDLER)

__mod_name__ = "Admins"
__command_list__ = [
    "setdesc"
    "setsticker"
    "setgpic"
    "delgpic"
    "setgtitle"
    "adminlist",
    "admins", 
    "invitelink", 
    "promote", 
    "fullpromote",
    "lowpromote",
    "demote", 
    "admincache"
]
__handlers__ = [
    SET_DESC_HANDLER,
    SET_STICKER_HANDLER,
    SETCHATPIC_HANDLER,
    RMCHATPIC_HANDLER,
    SETCHAT_TITLE_HANDLER,
    ADMINLIST_HANDLER,
    PIN_HANDLER,
    UNPIN_HANDLER,
    PINNED_HANDLER,
    INVITE_HANDLER,
    PROMOTE_HANDLER,
    FULLPROMOTE_HANDLER,
    DEMOTE_HANDLER,
    SET_TITLE_HANDLER,
    ADMIN_REFRESH_HANDLER,
]
