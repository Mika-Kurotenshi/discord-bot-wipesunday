import discord
from discord.ext import tasks
from datetime import datetime, timedelta
import pytz
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
TEST_NOW = os.getenv("TEST_NOW", "false").lower() == "true"

CHANNEL_ID = 1201189852889231451
TARGET_DAY = "saturday"
TARGET_HOUR = 13
TARGET_MINUTE = 0
TIMEZONE = pytz.timezone("Europe/Paris")

intents = discord.Intents.default()
client = discord.Client(intents=intents)
last_sent_date = None
calendar_days = ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]

def next_run_time():
    now = datetime.now(TIMEZONE)
    days_ahead = (calendar_days.index(TARGET_DAY) - calendar_days.index(now.strftime("%A").lower())) % 7
    if days_ahead == 0 and (now.hour, now.minute) >= (TARGET_HOUR, TARGET_MINUTE):
        days_ahead = 7
    next_time = now + timedelta(days=days_ahead)
    return next_time.replace(hour=TARGET_HOUR, minute=TARGET_MINUTE, second=0, microsecond=0)

async def send_wipesunday_message():
    global last_sent_date
    now = datetime.now(TIMEZONE)
    channel = client.get_channel(CHANNEL_ID)
    if not channel or last_sent_date == now.date():
        return
    # Webhook pour que Draftbot voit le message comme un utilisateur
    webhooks = await channel.webhooks()
    if webhooks:
        webhook = webhooks[0]
    else:
        webhook = await channel.create_webhook(name="WipeSunday Webhook")
    await webhook.send(
        content="!!wipesunday",
        username="WipeSunday",
        avatar_url=client.user.avatar.url if client.user.avatar else None
    )
    print(f"✅ Commande envoyée le {now}")
    last_sent_date = now.date()

@client.event
async def on_ready():
    print(f"✅ WipeSunday connecté en tant que {client.user}")
    print(f"Prochaine exécution prévue : {next_run_time()}")
    check_time.start()
    if TEST_NOW:
        await send_wipesunday_message()

@tasks.loop(minutes=1)
async def check_time():
    now = datetime.now(TIMEZONE)
    if (now.strftime("%A").lower() == TARGET_DAY
        and now.hour == TARGET_HOUR
        and now.minute == TARGET_MINUTE):
        await send_wipesunday_message()

client.run(TOKEN)
