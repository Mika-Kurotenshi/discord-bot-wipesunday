import discord
from discord.ext import tasks
from datetime import datetime, timedelta
import pytz
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
TEST_NOW = os.getenv("TEST_NOW", "false").lower() == "true"

# Configuration
CHANNEL_ID = 1201189852889231451  # Salon où le message sera envoyé
TARGET_DAY = "saturday"
TARGET_HOUR = 13
TARGET_MINUTE = 0
TIMEZONE = pytz.timezone("Europe/Paris")

intents = discord.Intents.default()
intents.messages = True
client = discord.Client(intents=intents)
last_sent_date = None
calendar_days = ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]

# Fonction pour calculer la prochaine exécution
def next_run_time():
    now = datetime.now(TIMEZONE)
    days_ahead = (calendar_days.index(TARGET_DAY) - calendar_days.index(now.strftime("%A").lower())) % 7
    if days_ahead == 0 and (now.hour, now.minute) >= (TARGET_HOUR, TARGET_MINUTE):
        days_ahead = 7
    next_time = now + timedelta(days=days_ahead)
    return next_time.replace(hour=TARGET_HOUR, minute=TARGET_MINUTE, second=0, microsecond=0)

# Fonction pour envoyer le message public
async def send_wipesunday_ping_public():
    global last_sent_date
    now = datetime.now(TIMEZONE)
    if last_sent_date == now.date():
        return

    channel = client.get_channel(CHANNEL_ID)
    if not channel:
        print("❌ Salon introuvable")
        return

    # Message public visible par tous
    await channel.send("⚠️ Wipesunday ! Tapez la commande `!!wipesunday` dès maintenant si vous voulez participer.")
    print(f"✅ Message public envoyé le {now}")
    last_sent_date = now.date()

# Événement ready
@client.event
async def on_ready():
    print(f"✅ WipeSunday connecté en tant que {client.user}")
    print(f"Prochaine exécution prévue : {next_run_time()}")
    check_time.start()

    # Test immédiat
    if TEST_NOW:
        await send_wipesunday_ping_public()

# Boucle pour vérifier l'heure chaque minute
@tasks.loop(minutes=1)
async def check_time():
    now = datetime.now(TIMEZONE)
    if (now.strftime("%A").lower() == TARGET_DAY
        and now.hour == TARGET_HOUR
        and now.minute == TARGET_MINUTE):
        await send_wipesunday_ping_public()

# Lancer le bot
client.run(TOKEN)
