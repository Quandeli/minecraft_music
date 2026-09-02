import discord
from discord.ext import commands
import yt_dlp
import asyncio
import eyed3
import os
import subprocess
from dotenv import load_dotenv
load_dotenv()
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
REPO_NAME = os.getenv("REPO_NAME")
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# --- CONFIGURATION STRUCTURE ---
# --- TO THIS PLAIN DIRECTORY LAYOUT ---
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
REPO_NAME = os.getenv("REPO_NAME")
# ENSURE THIS LINE SAYS THIS EXACTLY:
MUSIC_REPO_DIR = os.path.dirname(os.path.abspath(__file__))

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    print("Automated Permanent GitHub Core Stream Scanner Active!")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    content = message.content.strip()
    words = content.split()
    
    url = None
    for word in words:
        if "spotify.com" in word.lower() or "youtube.com" in word.lower() or "youtu.be" in word.lower():
            url = word
            break

    if not url:
        return

    ctx = await bot.get_context(message)
    await ctx.send("⏳ Link detected! Initializing secure tracking download...")

    # Unique epoch timestamp string prevents file namespace collisions
    unique_stamp = str(int(asyncio.get_event_loop().time()))
    temp_outtmpl = os.path.join(MUSIC_REPO_DIR, f"track_{unique_stamp}")

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': temp_outtmpl + '.%(ext)s', 
        'ignoreerrors': True,
        'quiet': True,
        'noplaylist': True,
        'no_warnings': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        },
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    try:
        title = "Unknown Song"
        artist = "Unknown Artist"

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if not info:
                await ctx.send("❌ Track signature missing or rejected by provider.")
                return
            
            title = info.get('track', info.get('title', 'Unknown Song'))
            artist = info.get('artist', 'Unknown Artist')

            if " - " in title and artist == "Unknown Artist":
                parts = title.split(" - ", 1)
                artist = parts[0].strip()
                title = parts[1].strip()

            ydl.download([url])
        
        generated_mp3 = temp_outtmpl + ".mp3"
        
        if os.path.exists(generated_mp3):
            # Stamp metadata natively for the Minecraft mod UI container layout
            audiofile = eyed3.load(generated_mp3)
            if audiofile.tag is None:
                audiofile.initTag()
            audiofile.tag.title = title
            audiofile.tag.artist = artist
            audiofile.tag.save()

            # Format structural filename safe for Git terminal queries
            safe_name = f"{artist}_{title}_{unique_stamp}.mp3".replace(" ", "_").replace("/", "_").replace("\\", "_").replace("?", "")
            permanent_filepath = os.path.join(MUSIC_REPO_DIR, safe_name)
            
            # Move the file to its permanent repo index position
            os.rename(generated_mp3, permanent_filepath)

            # --- FIX: SELF-INITIALIZING GIT PIPELINE ---
                        # --- STABLE HARDCODED REPOSITORY PUSH PIPELINE ---
            def push_to_github():
                # 1. If the hidden .git directory is missing, build it automatically!
                if not os.path.exists(os.path.join(MUSIC_REPO_DIR, ".git")):
                    print("🔧 Initializing Git repository automatically...")
                    subprocess.run("git init", shell=True, cwd=MUSIC_REPO_DIR, check=True)
                    subprocess.run("git remote add origin https://github.com", shell=True, cwd=MUSIC_REPO_DIR, check=True)
                    subprocess.run("git branch -M main", shell=True, cwd=MUSIC_REPO_DIR, check=True)
                
                # 2. Run standard file handoff sequences
                subprocess.run("git add .", shell=True, cwd=MUSIC_REPO_DIR, check=True)
                subprocess.run(f'git commit -m "Added track: {safe_name}"', shell=True, cwd=MUSIC_REPO_DIR, check=True)
                
                # --- FIXED: HARDCODED TO PUSH TO MAIN WITH ZERO ACCIDENTAL STRING DROPS ---
                subprocess.run("git push -u origin main", shell=True, cwd=MUSIC_REPO_DIR, check=True)

            await asyncio.to_thread(push_to_github)



            # Generate the true raw direct audio streaming URL pipe
            direct_streaming_url = f"https://raw.githubusercontent.com/{GITHUB_USERNAME}/{REPO_NAME}/main/{safe_name}"

            await ctx.send(
                f"🎵 **Track Permanently Anchored!**\n"
                f"**Song:** {title}\n"
                f"**Artist:** {artist}\n\n"
                f"📋 **Copy & Paste this link into the Music Disc Maker machine:**\n"
                f"```{direct_streaming_url}```"
            )
        else:
            await ctx.send("❌ Local audio file structure mismatch.")
    except Exception as e:
        await ctx.send("❌ Deployment pipeline failed. Make sure Git is authenticated on your desktop.")
        print(f"GitHub Thread Error: {e}")

token = os.getenv("DISCORD_TOKEN")
bot.run(token)