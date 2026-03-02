import asyncio
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import MessageNotModified
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, Message, ChatMemberUpdated

from DAXXMUSIC import app, protection
from DAXXMUSIC.utils.decorators.admins import ActualAdminCB
from DAXXMUSIC.utils.decorators.language import languageCB
from DAXXMUSIC.utils.inline.settings import media_delete_markup
from DAXXMUSIC.utils.database import (
    is_media_delete_on, media_delete_on, media_delete_off,
    get_media_delete_time, set_media_delete_time, get_lang,
    get_media_delete_type, set_media_delete_type
)
from config import BANNED_USERS
from strings import get_string


@app.on_callback_query(filters.regex("MD_MENU") & ~BANNED_USERS)
@ActualAdminCB
async def md_menu_cb(client, CallbackQuery: CallbackQuery, _):
    is_enabled = await is_media_delete_on(CallbackQuery.message.chat.id)
    time_val = await get_media_delete_time(CallbackQuery.message.chat.id)
    target_type = await get_media_delete_type(CallbackQuery.message.chat.id)
    buttons = media_delete_markup(_, is_enabled, time_val, target_type)
    try:
        return await CallbackQuery.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except MessageNotModified:
        return

@app.on_callback_query(filters.regex("MD_ANSWER") & ~BANNED_USERS)
@languageCB
async def md_answer_cb(client, CallbackQuery: CallbackQuery, _):
    try:
        await CallbackQuery.answer(_["ST_B_15"], show_alert=True)
    except:
        pass

@app.on_callback_query(filters.regex("MD_ENABLE") & ~BANNED_USERS)
@ActualAdminCB
async def md_enable_cb(client, CallbackQuery: CallbackQuery, _):
    chat_id = CallbackQuery.message.chat.id
    
    # Check if bot has required privileges
    try:
        bot_member = await app.get_chat_member(chat_id, app.id)
        if not (bot_member.privileges and bot_member.privileges.can_delete_messages and bot_member.privileges.can_invite_users and bot_member.privileges.can_promote_members):
            return await CallbackQuery.answer(_["md_5"], show_alert=True)
    except Exception:
        return await CallbackQuery.answer(_["md_5"], show_alert=True)

    await CallbackQuery.answer(_["md_6"])
    
    # Ensure protection userbot is in the chat
    try:
        prot_member = await app.get_chat_member(chat_id, protection.id)
    except Exception:
        try:
            invitelink = await app.export_chat_invite_link(chat_id)
            await protection.join_chat(invitelink)
        except Exception:
            return await CallbackQuery.answer("Failed to auto-add Protection Userbot. Please add it manually.", show_alert=True)

    # Promote protection userbot
    try:
        await app.promote_chat_member(
            chat_id,
            protection.id,
            privileges=bot_member.privileges
        )
    except Exception:
        return await CallbackQuery.answer("Failed to promote Protection Userbot. Please grant it admin rights.", show_alert=True)
        
    # Verify promotion
    try:
        prot_member = await app.get_chat_member(chat_id, protection.id)
        if not (prot_member.privileges and prot_member.privileges.can_delete_messages):
            return await CallbackQuery.answer("Protection Userbot missing delete messages permission.", show_alert=True)
    except Exception:
        return await CallbackQuery.answer("Could not verify Protection Userbot permissions.", show_alert=True)

    await media_delete_on(chat_id)
    is_enabled = True
    time_val = await get_media_delete_time(chat_id)
    target_type = await get_media_delete_type(chat_id)
    buttons = media_delete_markup(_, is_enabled, time_val, target_type)
    
    try:
        await CallbackQuery.message.reply_text(_["md_1"])
    except Exception:
        pass
    
    try:
        return await CallbackQuery.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except MessageNotModified:
        return
        
@app.on_callback_query(filters.regex("MD_DISABLE") & ~BANNED_USERS)
@ActualAdminCB
async def md_disable_cb(client, CallbackQuery: CallbackQuery, _):
    chat_id = CallbackQuery.message.chat.id
    await media_delete_off(chat_id)
    is_enabled = False
    time_val = await get_media_delete_time(chat_id)
    target_type = await get_media_delete_type(chat_id)
    buttons = media_delete_markup(_, is_enabled, time_val, target_type)
    
    try:
        await CallbackQuery.message.reply_text(_["md_2"])
    except Exception:
        pass

    try:
        return await CallbackQuery.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except MessageNotModified:
        return

@app.on_callback_query(filters.regex("MD_TIME_CUR") & ~BANNED_USERS)
@languageCB
async def md_time_cur_cb(client, CallbackQuery: CallbackQuery, _):
    try:
        current_time = await get_media_delete_time(CallbackQuery.message.chat.id)
        return await CallbackQuery.answer(f"Currently set to {current_time} minutes")
    except Exception:
        pass

@app.on_callback_query(filters.regex("MD_TYPE") & ~BANNED_USERS)
@ActualAdminCB
async def md_type_cb(client, CallbackQuery: CallbackQuery, _):
    chat_id = CallbackQuery.message.chat.id
    current_type = await get_media_delete_type(chat_id)
    new_type = "Members" if current_type == "All" else "All"
    await set_media_delete_type(chat_id, new_type)
    
    is_enabled = await is_media_delete_on(chat_id)
    time_val = await get_media_delete_time(chat_id)
    buttons = media_delete_markup(_, is_enabled, time_val, new_type)
    
    try:
        await CallbackQuery.answer(_["md_7"].format(_["MD_B_11"] if new_type == "All" else _["MD_B_12"]))
    except Exception:
        pass
        
    try:
        return await CallbackQuery.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except MessageNotModified:
        return

@app.on_callback_query(filters.regex(r"^MD_TIME_([+-])$") & ~BANNED_USERS)
@ActualAdminCB
async def md_time_cb(client, CallbackQuery: CallbackQuery, _):
    chat_id = CallbackQuery.message.chat.id
    action = CallbackQuery.matches[0].group(1)
    
    current_time = await get_media_delete_time(chat_id)
    if action == "+":
        new_time = current_time + 1
    else:
        new_time = current_time - 1
        
    if new_time > 5:
        return await CallbackQuery.answer("Max limit is 5 minutes", show_alert=True)
    if new_time < 1:
        return await CallbackQuery.answer("Min limit is 1 minute", show_alert=True)
        
    await set_media_delete_time(chat_id, new_time)
    
    is_enabled = await is_media_delete_on(chat_id)
    target_type = await get_media_delete_type(chat_id)
    buttons = media_delete_markup(_, is_enabled, new_time, target_type)
    
    try:
        await CallbackQuery.answer(_["md_3"].format(new_time))
    except Exception:
        pass
        
    try:
        return await CallbackQuery.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except MessageNotModified:
        return

# background task
async def delete_media_task(chat_id, message_id, delay_seconds):
    await asyncio.sleep(delay_seconds)
    try:
        await protection.delete_messages(chat_id, message_id)
    except Exception:
        pass

@protection.on_message(
    filters.group & (filters.photo | filters.video | filters.document | filters.animation | filters.sticker)
)
async def media_message_handler(client, message: Message):
    chat_id = message.chat.id
    if not await is_media_delete_on(chat_id):
        return
        
    target_type = await get_media_delete_type(chat_id)
    if target_type == "Members" and getattr(message.from_user, "is_bot", False) is False:
        try:
            member = await app.get_chat_member(chat_id, message.from_user.id)
            if member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                return
        except Exception:
            pass
            
    delay_minutes = await get_media_delete_time(chat_id)
    delay_seconds = delay_minutes * 60
    
    asyncio.create_task(delete_media_task(chat_id, message.id, delay_seconds))


@app.on_chat_member_updated(filters.group, group=7)
async def check_protection_member_status(client, event: ChatMemberUpdated):
    if not event.new_chat_member:
        return
    
    if event.new_chat_member.user.id == protection.id:
        chat_id = event.chat.id
        status = event.new_chat_member.status
        
        is_admin_with_delete = False
        if status == ChatMemberStatus.ADMINISTRATOR and event.new_chat_member.privileges:
            is_admin_with_delete = event.new_chat_member.privileges.can_delete_messages
            
        if status in [ChatMemberStatus.LEFT, ChatMemberStatus.BANNED, ChatMemberStatus.MEMBER] or (status == ChatMemberStatus.ADMINISTRATOR and not is_admin_with_delete):
            if await is_media_delete_on(chat_id):
                await media_delete_off(chat_id)
                lang = await get_lang(chat_id)
                _ = get_string(lang)
                try:
                    await app.send_message(chat_id, _["md_4"].format(protection.username))
                except Exception:
                    pass
