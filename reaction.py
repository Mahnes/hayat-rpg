import random
import asyncio
from telethon import TelegramClient, events
from telethon.tl.functions.messages import SendReactionRequest
from telethon.tl.types import ReactionEmoji

# Telegram API
api_id = 4054520
api_hash = "5b3336aceb7bf56133db69b5c837d351"

# Reaksiyon ihtimali (%19)
REACTION_CHANCE = 0.19

# Mesajdan sonra reaksiyon gecikmesi
MIN_DELAY = 16
MAX_DELAY = 74

# Cooldown (insan gibi görünmesi için)
GLOBAL_COOLDOWN = (19, 43)

# Emoji havuzu
EMOJIS = [
    "👍","🔥","😂","😍","👏","💯","😎","😁","🤝","🤩",
    "😆","👌","😅","😏","🙂","🥳","🤮"
]

# Reaksiyon atılacak gruplar
TARGET_GROUPS = [
    "vahset_infaz_sansursuz",
    "https://t.me/+waCeuaW7wZkzYjgx",
    "https://t.me/+KODrPJqIjU0yYzVl",
    "https://t.me/+j8mC7PzK1VAwMjEx",
    "ingilizce_pratik_yokdil",
    "haydayvip"
]

client = TelegramClient("reaction_session", api_id, api_hash)

last_reaction_time = 0


async def is_admin(chat, user_id):
    try:
        admins = await client.get_participants(chat, filter=None)
        for a in admins:
            if a.id == user_id and getattr(a, "admin_rights", None):
                return True
    except:
        pass
    return False


@client.on(events.NewMessage)
async def handler(event):

    global last_reaction_time

    chat = await event.get_chat()

    # hedef grup kontrolü
    if getattr(chat, "username", None) not in TARGET_GROUPS:
        return

    # admin kontrolü
    sender = await event.get_sender()
    if await is_admin(chat, sender.id):
        return

    # reaksiyon ihtimali
    if random.random() > REACTION_CHANCE:
        return

    # cooldown kontrolü
    if last_reaction_time:
        cooldown = random.randint(*GLOBAL_COOLDOWN)
        if asyncio.get_event_loop().time() - last_reaction_time < cooldown:
            return

    # gecikme
    delay = random.randint(MIN_DELAY, MAX_DELAY)
    await asyncio.sleep(delay)

    emoji = random.choice(EMOJIS)

    try:
        await client(
            SendReactionRequest(
                peer=event.chat_id,
                msg_id=event.id,
                reaction=[ReactionEmoji(emoticon=emoji)]
            )
        )

        last_reaction_time = asyncio.get_event_loop().time()
        print(f"Reacted with {emoji} after {delay}s")

    except Exception as e:
        print("Reaction error:", e)


print("Auto Reaction Userbot Running...")
client.start()
client.run_until_disconnected()
