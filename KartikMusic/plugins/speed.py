# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# This file is part of KartikMusic


import time

from pyrogram import filters, types

from KartikMusic import Kartik, app, db, lang, queue
from KartikMusic.helpers import buttons, can_manage_vc

checker = []


@app.on_message(
    filters.command(["cspeed", "speed", "cslow", "slow", "playback", "cplayback"])
    & filters.group
    & ~app.bl_users
)
@lang.language()
@can_manage_vc
async def playback_hndlr(_, m: types.Message):
    chat_id = m.chat.id
    if not await db.get_call(chat_id):
        return await m.reply_text(m.lang["queue_2"])

    media = queue.get_current(chat_id)
    if not media:
        return await m.reply_text(m.lang["queue_2"])

    if not media.duration_sec:
        return await m.reply_text(m.lang["admin_27"])

    if media.file_path and "downloads" not in media.file_path:
        return await m.reply_text(m.lang["admin_27"])

    return await m.reply_text(
        text=m.lang["admin_28"].format(app.mention),
        reply_markup=buttons.speed_markup(m.lang, chat_id),
    )


@app.on_callback_query(filters.regex("SpeedUP") & ~app.bl_users)
@lang.language()
@can_manage_vc
async def speed_cb(_, query: types.CallbackQuery):
    data = query.data.split()
    temp = data[1].split("|")
    chat_id = int(temp[0])
    speed = float(temp[1])

    if not await db.get_call(chat_id):
        return await query.answer(query.lang["general_5"], show_alert=True)

    media = queue.get_current(chat_id)
    if not media:
        return await query.answer(query.lang["queue_2"], show_alert=True)

    if not media.duration_sec:
        return await query.answer(query.lang["admin_27"], show_alert=True)

    if media.file_path and "downloads" not in media.file_path:
        return await query.answer(query.lang["admin_27"], show_alert=True)

    if media.speed == speed:
        return await query.answer(query.lang["admin_29"], show_alert=True)

    if chat_id in checker:
        return await query.answer(query.lang["admin_30"], show_alert=True)

    checker.append(chat_id)
    try:
        await query.answer(query.lang["admin_31"])
    except Exception:
        pass

    mystic = await query.edit_message_text(
        text=query.lang["admin_32"].format(query.from_user.mention),
    )

    try:
        current_pos = media.time
        if media.played_at:
            current_pos += int((time.time() - media.played_at) * media.speed)

        media.speed = speed
        await Kartik.play_media(chat_id, mystic, media, seek_time=int(current_pos))
    except Exception:
        if chat_id in checker:
            checker.remove(chat_id)
        return await mystic.edit_text(
            query.lang["admin_33"],
            reply_markup=types.InlineKeyboardMarkup(
                [
                    [
                        types.InlineKeyboardButton(
                            query.lang["close"], callback_data="close"
                        )
                    ]
                ]
            ),
        )

    if chat_id in checker:
        checker.remove(chat_id)

    await mystic.edit_text(
        text=query.lang["admin_34"].format(speed, query.from_user.mention),
        reply_markup=types.InlineKeyboardMarkup(
            [[types.InlineKeyboardButton(query.lang["close"], callback_data="close")]]
        ),
    )
