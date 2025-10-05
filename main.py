import discord
from discord.ext import tasks
from datetime import datetime, timedelta
import pytz
import os
from dotenv import load_dotenv
from flask import Flask
import threading
import asyncio

# -----------------------------
# Charger les variables d'environnement
# -----------------------------
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
TEST_NOW = os.getenv("TEST_NOW", "false").lower() == "true"

# -----------------------------
# Configuration
# -----------------------------
CHANNEL_ID = 1201189852889231451  # Salon pour le ping rôle
ROLE_ID_WIPER = 933063131343769610
TARGET_DAY = "friday"  # Vendredi
TARGET_HOUR = 17       # 17h
TARGET_MINUTE = 0
TIMEZONE = pytz.timezone("Europe/Paris")

intents = discord.Intents.default()
intents.messages = True
client = discord.Client(intents=intents)

last_sent_date = None
calendar_days = ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]

# -----------------------------
# Calcul prochaine exécution
# -----------------------------
def next_run_time():
    now = datetime.now(TIMEZONE)
    days_ahead = (calendar_days.index(TARGET_DAY) - calendar_days.index(now.strftime("%A").lower())) % 7
    if days_ahead == 0 and (now.hour, now.minute) >= (TARGET_HOUR, TARGET_MINUTE):
        days_ahead = 7
    next_time = now + timedelta(days=days_ahead)
    return next_time.replace(hour=TARGET_HOUR, minute=TARGET_MINUTE, second=0, microsecond=0)

# -----------------------------
# Fonction d'envoi du message
# -----------------------------
async def send_wipesunday_ping_role():
    global last_sent_date
    now = datetime.now(TIMEZONE)
    if last_sent_date == now.date():
        return

    channel = client.get_channel(CHANNEL_ID)
    if not channel:
        print("❌ Salon introuvable")
        return

    await channel.send(f"⚠️ <@&{ROLE_ID_WIPER}> Pour le prochain Wipe Sunday, merci de taper la commande `!!wipesunday` ! 🎉✨")
    print(f"✅ Message envoyé le {now}")
    last_sent_date = now.date()

# -----------------------------
# Rattrapage si l'envoi a été manqué
# -----------------------------
async def catch_up_missed():
    global last_sent_date
    now = datetime.now(TIMEZONE)
    if now.strftime("%A").lower() == TARGET_DAY and last_sent_date != now.date():
        print("⚠️ Message manqué détecté ! Envoi immédiat de rattrapage.")
        await send_wipesunday_ping_role()

# -----------------------------
# Événement ready
# -----------------------------
@client.event
async def on_ready():
    print(f"✅ WipeSunday connecté en tant que {client.user}")
    print(f"Prochaine exécution prévue : {next_run_time()}")
    
    # Rattrapage si message manqué
    await catch_up_missed()

    # Test immédiat
    if TEST_NOW:
        await send_wipesunday_ping_role()

    check_time.start()

# -----------------------------
# Boucle pour vérifier l'heure
# -----------------------------
@tasks.loop(minutes=1)
async def check_time():
    now = datetime.now(TIMEZONE)
    if (now.strftime("%A").lower() == TARGET_DAY
        and now.hour == TARGET_HOUR
        and now.minute == TARGET_MINUTE):
        await send_wipesunday_ping_role()

# -----------------------------
# Flask pour UptimeRobot
# -----------------------------
app = Flask("")

@app.route("/")
def home():
    return "WipeSunday is alive!"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

threading.Thread(target=run_flask).start()

# -----------------------------
# Lancer le bot Discord
# -----------------------------
client.run(TOKEN)
