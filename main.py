import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import functions as fun
import sqlite3
import asyncio
# ============
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')  # Necessary to actually communicate to the bot
if not TOKEN:
    raise ValueError("Invalid Token")

# --------------------------- Permission and Handling ---------------------------
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)  # How to reference the bot

# ------------------------------- Global Variables -------------------------------
ACTIVE_REMINDERS = {}

# ----------- SQL Pipeline: Python -> Cursor -> Connection -> Database -----------
conn = sqlite3.connect("levels.db")  # Opens live link between Python and Database
cursor = conn.cursor()  # Executes SQL queries (e.g. SELECT, INSERT, UPDATE, DELETE, fetches results, etc)
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    xp INTEGER DEFAULT 0,
    level INTEGER DEFAULT 0
    )
""")
conn.commit()

# ===================


@bot.event
async def on_ready():
    """
    on_ready runs on Snooj Prototype's startup
    :return:
    """
    print(f"Booting Up {bot.user.name}")
    channel = bot.get_channel(fun.ChannelIDs.main)
    member = bot.get_user(fun.UserIDs.noot)
    if channel and member:
        await channel.send(f"Remember the {member.mention}")

    # Start the reminder task for Bil
    # asyncio.create_task(reminder_task())


@bot.event
async def on_member_join(member):
    """
    on_member_join runs when a 'member' joins the server
    :param member:
    :return:
    """
    await member.send(f"Welcome to the server {member.name}")


@bot.event
async def on_message(message):
    """
    on_message runs when a user sends a 'message'
    :param message:
    :return:
    """
    if message.author.bot:
        return
    elif message.author.id == fun.UserIDs.noot:
        if message.content.strip().lower() == 'how are you?':
            await message.channel.send("I'm doing well, thanks.")
    elif message.author.id == fun.UserIDs.bipl:
        if len(message.content.split()) == 1:
            await fun.hugeFunction(message)

    # REQUIRED BY LAW FOR SPECIFIED REASON - DO NOT DELETE
    await bot.process_commands(message)


@bot.command(help="Starts a reminder timer; Format: #h #m #s")
async def remindme(ctx, *, time_input: str = None):
    if ctx.author.id in ACTIVE_REMINDERS:
        await ctx.send("You already have a reminder running. Cancel it first!")
        return

    if time_input is None:
        await ctx.send("How long should the timer be? (Max of 24h)\nFormat: #h #m #s")

        def check(msg):
            return (msg.author == ctx.author) and (msg.channel == ctx.channel)

        try:
            response = await bot.wait_for("message", check=check, timeout=30)
            time_input = response.content
        except asyncio.TimeoutError:
            await ctx.send("You took too long to reply.")
            return

    time_input = time_input.split()
    if not time_input:
        await ctx.send("No response entered.")
        return

    total_sec_overall = 0

    for part in time_input:
        if len(part) < 2:
            await ctx.send(f"Invalid input: '{part}'")
            return

        unit = part[-1].lower()

        if not part[:-1].isdigit():
            await ctx.send(f"'{part}' is not a valid number.")
            return

        value = int(part[:-1])

        if unit == "s":
            total_sec_overall += value
        elif unit == "m":
            total_sec_overall += value * 60
        elif unit == "h":
            total_sec_overall += value * 3600
        else:
            await ctx.send(f"'{part}' must end in s, m, or h.")
            return

    if total_sec_overall <= 0:
        await ctx.send("Time must be greater than 0.")
        return
    if total_sec_overall > 86400:
        total_sec_overall = 86400
        await ctx.send(f"Time exceeded 24h. Setting Timer to 24h...")

    total_hr = total_sec_overall // 3600
    total_min = (total_sec_overall % 3600) // 60
    total_sec = total_sec_overall % 60

    wait_time = []

    if total_hr:
        wait_time.append(f"{total_hr}h")
    if total_min:
        wait_time.append(f"{total_min}m")
    if total_sec:
        wait_time.append(f"{total_sec}s")

    async def reminderTask():
        try:
            await asyncio.sleep(total_sec_overall)
            await ctx.send(f"Hey, {ctx.author.mention}, reminded!")
            ACTIVE_REMINDERS.pop(ctx.author.id, None)
        except asyncio.CancelledError:
            await ctx.send("Your reminder was cancelled.")

    task = asyncio.create_task(reminderTask())
    ACTIVE_REMINDERS[ctx.author.id] = task
    await ctx.send(f"Timer set for {', '.join(wait_time)}!")


@bot.command(help="Cancel a reminder timer")
async def cancelreminder(ctx):
    if ctx.author.id not in ACTIVE_REMINDERS:
        await ctx.send("You don't have an active reminder.")
        return

    task = ACTIVE_REMINDERS[ctx.author.id]
    task.cancel()

    ACTIVE_REMINDERS.pop(ctx.author.id, None)
    await ctx.send("Your reminder was deleted.")


# Run the bot
bot.run(TOKEN, log_handler=handler, log_level=logging.DEBUG)
