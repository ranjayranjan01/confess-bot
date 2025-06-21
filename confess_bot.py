from pyrogram import Client, filters
from pyrogram.types import Message
import config
import re

bot = Client("confess_bot", api_id=config.API_ID, api_hash=config.API_HASH, bot_token=config.BOT_TOKEN)

confession_counter = 1
confession_map = {}

def escape(text):
    return re.sub(r'([*_`])', r'\\\1', text)

def is_admin(user_id):
    return user_id in config.ADMINS

def is_whitelisted(user_id):
    return user_id in config.WHITELIST

@bot.on_message(filters.private & filters.command("start"))
def start(client, message: Message):
    user_id = message.from_user.id
    if is_admin(user_id):
        message.reply("👋 *Welcome Admin!*\n\nUse /allow or /block to manage users.\nSend a confession to test.", quote=True)
    elif is_whitelisted(user_id):
        message.reply("✅ Welcome! Send your confession now.")
    else:
        message.reply("❌ You are not allowed to send confessions.")

@bot.on_message(filters.private & filters.command("allow"))
def allow_user(client, message: Message):
    if not is_admin(message.from_user.id):
        return message.reply("❌ You are not authorized.")
    try:
        user_id = int(message.text.split()[1])
        if user_id not in config.WHITELIST:
            config.WHITELIST.append(user_id)
            message.reply(f"✅ User `{user_id}` allowed.")
        else:
            message.reply(f"ℹ️ User `{user_id}` is already allowed.")
    except:
        message.reply("⚠️ Usage: /allow user_id")

@bot.on_message(filters.private & filters.command("block"))
def block_user(client, message: Message):
    if not is_admin(message.from_user.id):
        return message.reply("❌ You are not authorized.")
    try:
        user_id = int(message.text.split()[1])
        if user_id in config.WHITELIST:
            config.WHITELIST.remove(user_id)
            message.reply(f"🚫 User `{user_id}` blocked.")
        else:
            message.reply(f"ℹ️ User `{user_id}` not in whitelist.")
    except:
        message.reply("⚠️ Usage: /block user_id")

@bot.on_message(filters.private & ~filters.command(["start", "allow", "block", "reply"]))
def confess(client, message: Message):
    global confession_counter
    user_id = message.from_user.id

    if not is_whitelisted(user_id):
        message.reply("❌ You are not allowed to send confessions.")
        return

    confession_text = message.text
    post = f"💌 #{confession_counter}:\n{confession_text}"
    client.send_message(chat_id=config.GROUP_ID, text=post)
    confession_map[confession_counter] = user_id
    message.reply(f"✅ Your confession has been posted as #{confession_counter}")
    confession_counter += 1

@bot.on_message(filters.command("reply") & filters.group)
def reply_to_confession(client, message: Message):
    try:
        parts = message.text.split(maxsplit=2)
        reply_id = int(parts[1])
        reply_msg = parts[2]

        if reply_id in confession_map:
            user_id = confession_map[reply_id]
            sender = message.from_user
            sender_info = f"[{sender.first_name}](tg://user?id={sender.id})"
            reply_text = f"🔁 Anonymous reply to your confession #{reply_id}:\n{reply_msg}"
            client.send_message(chat_id=user_id, text=reply_text)
            for admin in config.ADMINS:
                client.send_message(chat_id=admin, text=f"👀 Reply sent to #{reply_id}\nFrom: {sender_info}\nMessage: {reply_msg}", parse_mode="Markdown")
            message.reply("✅ Reply sent anonymously!")
        else:
            message.reply("❌ Invalid confession number.")
    except:
        message.reply("⚠️ Format: /reply confession_number your message", quote=True)

bot.run()