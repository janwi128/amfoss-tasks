import os
import discord
import aiohttp
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

playlists = {}

@bot.event
async def on_ready():
    try:
        guild = discord.Object(id=GUILD_ID)
        bot.tree.copy_global_to(guild=guild)
        await bot.tree.sync(guild=guild)
        print(f"✅ Synced commands for guild {GUILD_ID}")
    except Exception as e:
        print(f"❌ Error syncing commands: {e}")

    print(f"🤖 Bot is ready! Logged in as {bot.user}")

@bot.tree.command(name="help", description="Show all available commands")
async def help_command(interaction: discord.Interaction):
    await interaction.response.defer()
    help_text = (
        "**Available Commands:**\n"
        "📀 `/track <song>` → Get album, duration, release date, genre\n"
        "🎵 `/lyrics <artist> <title>` → Get lyrics of a song\n"
        "🎶 `/playlist add <song>` → Add a song to your playlist\n"
        "❌ `/playlist remove <song>` → Remove a song from your playlist\n"
        "📜 `/playlist view` → View your playlist\n"
        "🧹 `/playlist clear` → Clear your playlist\n"
        "ℹ️ `/help` → Show this help message"
    )
    await interaction.followup.send(help_text)

@bot.tree.command(name="track", description="Get track details from MusicBrainz")
async def track_command(interaction: discord.Interaction, *, track: str):
    await interaction.response.defer()
    url = f"https://musicbrainz.org/ws/2/recording/?query={track}&fmt=json"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers={"User-Agent": "LyricLoungeBot/1.0"}) as resp:
            data = await resp.json()

    if "recordings" not in data or not data["recordings"]:
        await interaction.followup.send("❌ Track not found.")
        return

    rec = data["recordings"][0]
    title = rec.get("title", "Unknown")
    album = rec["releases"][0]["title"] if "releases" in rec and rec["releases"] else "Unknown"
    duration = f"{rec['length']//60000}:{(rec['length']//1000)%60:02d}" if "length" in rec else "Unknown"
    release_date = rec["releases"][0].get("date", "Unknown") if "releases" in rec and rec["releases"] else "Unknown"
    tags = ", ".join([tag["name"] for tag in rec.get("tags", [])]) if "tags" in rec else "None"

    result = (
        f"**🎶 {title}**\n"
        f"📀 Album: {album}\n"
        f"⏱️ Duration: {duration}\n"
        f"📅 Release Date: {release_date}\n"
        f"🏷️ Genre Tags: {tags}"
    )
    await interaction.followup.send(result)

@bot.tree.command(name="lyrics", description="Get lyrics from LRClib")
async def lyrics_command(interaction: discord.Interaction, artist: str, title: str):
    await interaction.response.defer()
    url = f"https://lrclib.net/api/get?artist_name={artist}&track_name={title}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                await interaction.followup.send("❌ Lyrics not found.")
                return
            data = await resp.json()

    lyrics = data.get("syncedLyrics") or data.get("plainLyrics")
    if not lyrics:
        await interaction.followup.send("❌ Lyrics not available.")
        return

    if len(lyrics) > 1900:
        lyrics = lyrics[:1900] + "...\n(lyrics truncated)"
    await interaction.followup.send(f"**Lyrics for {title} by {artist}:**\n{lyrics}")

@bot.tree.command(name="playlist", description="Manage your personal playlist")
@app_commands.describe(action="add/remove/view/clear", song="Song name (for add/remove)")
async def playlist_command(interaction: discord.Interaction, action: str, song: str = None):
    await interaction.response.defer()
    user_id = str(interaction.user.id)

    if user_id not in playlists:
        playlists[user_id] = []

    if action == "add":
        if song:
            playlists[user_id].append(song)
            await interaction.followup.send(f"✅ Added **{song}** to your playlist.")
        else:
            await interaction.followup.send("❌ Please provide a song to add.")
    elif action == "remove":
        if song in playlists[user_id]:
            playlists[user_id].remove(song)
            await interaction.followup.send(f"❌ Removed **{song}** from your playlist.")
        else:
            await interaction.followup.send("❌ Song not found in your playlist.")
    elif action == "view":
        if playlists[user_id]:
            playlist_str = "\n".join([f"{i+1}. {s}" for i, s in enumerate(playlists[user_id])])
            await interaction.followup.send(f"📜 Your Playlist:\n{playlist_str}")
        else:
            await interaction.followup.send("🎶 Your playlist is empty.")
    elif action == "clear":
        playlists[user_id] = []
        await interaction.followup.send("🧹 Cleared your playlist.")
    else:
        await interaction.followup.send("❌ Invalid action. Use: add, remove, view, clear.")

bot.run(TOKEN)

