from pyrogram import filters
from DAXXMUSIC import app
from DAXXMUSIC.utils.decorators import language

@app.on_message(filters.command(["img", "image"], prefixes=["/", "!"]))
@language
async def google_img_search(client, message, _):
    await message.reply_text(_["BLOCK_CM"])
