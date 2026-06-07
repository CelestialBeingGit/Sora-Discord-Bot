import discord
from discord import app_commands
from discord.ext import commands
import aiohttp
import sqlite3
import asyncio
import random
import os
from flask import Flask
from threading import Thread
from dotenv import load_dotenv
from bs4 import BeautifulSoup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)
load_dotenv()
def init_db():
    conn = sqlite3.connect('notes.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
@bot.event
async def on_ready():
    init_db()
    try:
        synced = await bot.tree.sync()
        print(f"Synchronized commands: {len(synced)}")
    except Exception as e:
        print(f"Synchronization error: {e}")
    print("Sora loves humanity")
@bot.command(name="shiro", description="My sister: Shows a random cute picture of Shiro!")
async def shiro(ctx):
    shiro_images = [
        "https://images.steamusercontent.com/ugc/2425628385214170390/2317E4295A26C052ED9C28B5304A60C844E0AACE/?imw=5000&imh=5000&ima=fit&impolicy=Letterbox&imcolor=%23000000&letterbox=false",
        "https://external-preview.redd.it/shiro-is-so-cute-v0-U1Y1y0q5MWMhVA5Y9BFi5uuAcn65edvbEPUNhDLaTR0.jpg?auto=webp&s=eae38f88ed2486592e90080fdb00ac0944d39e6b",
        "https://i.pinimg.com/originals/cd/78/61/cd78616d1ff37e9f39b8911b7e71dcdd.gif",
        "https://media2.giphy.com/media/v1.Y2lkPTZjMDliOTUyY3M5dmlqMWNiM25sNmJqZXNibjNtamNpaXYyeGJmb3IwanFrNHBzMSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/uEV4RB1fjv3AA/200.gif",
        "https://media.tenor.com/xaSiKZZiD-EAAAAM/siro.gif"
    ]
    chosen_url = random.choice(shiro_images)
    embed = discord.Embed(
        title="Shiro: Chess is no different from Tic-Tac-Toe.",
        color=discord.Color.from_rgb(220, 208, 255)
    )
    embed.set_image(url=chosen_url)
    embed.set_footer(text="No Game No Life • 『　　』 never loses")
    await ctx.send(embed=embed)
class NoteGroup(app_commands.Group, name="note"):
    """Commands for managing your personal notes"""
    @app_commands.command(name="add", description="Create a new personal note.")
    @app_commands.describe(title="The title of your note.", content="The main text of your note.")
    async def add_note(self, interaction: discord.Interaction, title: str, content: str):
        user_id = interaction.user.id
        conn = sqlite3.connect('notes.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO notes (user_id, title, content) VALUES (?, ?, ?)", (user_id, title, content))
        conn.commit()
        conn.close()
        await interaction.response.send_message(f"✅ Note **«{title}»** has been created!", ephemeral=True)
    @app_commands.command(name="list", description="Display all your saved notes.")
    async def list_notes(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        conn = sqlite3.connect('notes.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, content FROM notes WHERE user_id = ?", (user_id,))
        notes = cursor.fetchall()
        conn.close()
        if not notes:
            await interaction.response.send_message("❌ You don't have any notes yet.", ephemeral=True)
            return
        embed = discord.Embed(title="📝 Your Personal Notes", color=discord.Color.blue())
        for note_id, title, content in notes:
            short_content = content if len(content) <= 100 else f"{content[:97]}..."
            embed.add_field(name=f"📌 [ID: {note_id}] {title}", value=short_content, inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    @app_commands.command(name="delete", description="Delete a specific note using its ID.")
    @app_commands.describe(note_id="The ID of the note you want to remove.")
    async def delete_note(self, interaction: discord.Interaction, note_id: int):
        user_id = interaction.user.id
        conn = sqlite3.connect('notes.db')
        cursor = conn.cursor()
        cursor.execute("SELECT title FROM notes WHERE id = ? AND user_id = ?", (note_id, user_id))
        note = cursor.fetchone()
        if not note:
            await interaction.response.send_message("❌ Note not found or it does not belong to you.", ephemeral=True)
            conn.close()
            return
        cursor.execute("DELETE FROM notes WHERE id = ? AND user_id = ?", (note_id, user_id))
        conn.commit()
        conn.close()
        await interaction.response.send_message(f"🗑️ Note **«{note[0]}»** has been deleted.", ephemeral=True)
bot.tree.add_command(NoteGroup())
@bot.command(name="help", description="Shows a list of all available commands.")
async def help_command(ctx):
    embed = discord.Embed(
        title="Sora can do anything!",
        description="Well then, shall we begin the game?",
        color=discord.Color.green()
    )
    embed.add_field(
        name="ℹ️ General Commands",
        value=(
            "`!help` - Shows this help menu.\n"
            "`!pomodoro <minutes>` - Starts a productivity timer.\n"
            "`!guide` - Shows game guides for ZZZ.\n"
            "`!socials` - Displays creator social media links.\n"
            "`!anime <name>` - Searches info about an anime via MyAnimeList.\n"
            "`!gamenews` - Fetches the latest gaming news from iXBT.Games.\n"
            "`!books` - Displays popular books from Chitai-Gorod."
        ),
        inline=False
    )
    embed.add_field(
        name="📝 Slash Commands (Type `/` to use)",
        value=(
            "`/note add` - Create a new personal note.\n"
            "`/note list` - Display all your saved notes (Private).\n"
            "`/note delete` - Delete a specific note using its ID."
        ),
        inline=False
    )
    embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
    await ctx.send(embed=embed)
@bot.command(name="pomodoro", description="Starts a productivity timer.")
async def pomodoro(ctx, minutes: int):
    await ctx.send(f"⏰ Timer started for {minutes} minutes.")
    await asyncio.sleep(minutes * 60)
    await ctx.send(f"{ctx.author.mention}, time is up!")
@bot.command(name="guide", description="Shows game guides.")
async def guide(ctx):
    embed = discord.Embed(
        description="[ZZZ Guides](https://vk.com/zzz_academy)",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed)
@bot.command(name="socials", description="Shows social media links.")
async def socials(ctx):
    embed = discord.Embed(
        title="Creativity",
        description=(
            "[Steam](https://steamcommunity.com/profiles/76561199811582844/) | "
            "[Twitch](https://www.twitch.tv/axiomavt) | "
            "[TikTok](https://www.tiktok.com/@chilll_view)"
        ),
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed)
@bot.command(name="anime", description="Shows information about an anime.")
async def anime(ctx, *, name: str):
    url = "https://api.jikan.moe/v4/anime"
    payload = {"q": name, "limit": 1}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=payload) as response:
            if response.status != 200:
                await ctx.send("❌ Failed to connect to MyAnimeList servers.")
                return
            data = await response.json()
            if not data['data']:
                await ctx.send("🔍 No anime found with that title.")
                return
            anime_data = data['data'][0]
            title = anime_data.get('title', 'Unknown')
            title_en = anime_data.get('title_english') or "None"
            score = anime_data.get('score', 'N/A')
            episodes = anime_data.get('episodes', 'Airing')
            status = anime_data.get('status', 'Unknown')
            synopsis = anime_data.get('synopsis', 'No description available.')
            images = anime_data.get('images', {})
            jpg_data = images.get('jpg', {})
            image_url = jpg_data.get('large_image_url', '')
            anime_url = anime_data.get('url', '')
            if len(synopsis) > 500:
                synopsis = synopsis[:500] + "..."
            embed = discord.Embed(
                title=title, 
                description=f"**English Title:** {title_en}\n\n{synopsis}", 
                color=discord.Color.orange(),
                url=anime_url
            )
            if image_url:
                embed.set_thumbnail(url=image_url)
            embed.add_field(name="⭐ Score", value=str(score), inline=True)
            embed.add_field(name="🎬 Episodes", value=str(episodes), inline=True)
            embed.add_field(name="📊 Status", value=str(status), inline=True)
            embed.set_footer(text="Information provided by MyAnimeList")
            await ctx.send(embed=embed)
@bot.command(name="gamenews", description="Displays the latest gaming news.")
async def gamenews(ctx):
    url = "https://ixbt.games/news/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    async with ctx.typing():
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers) as response:
                    if response.status != 200:
                        await ctx.send("❌ Failed to load iXBT.games website.")
                        return
                    html = await response.text()
            except Exception as e:
                await ctx.send(f"❌ An error occurred during the request: {e}")
                return
        soup = BeautifulSoup(html, 'html.parser')
        titles = soup.find_all('h3', class_='py-2 text-base font-medium text-neutral-900 group-hover:underline dark:text-gray-100')
        descriptions = soup.find_all('span', class_='rounded text-xs text-gray-800 dark:text-gray-400')
        if not titles:
            await ctx.send("🔍 Could not find any news. The website layout might have changed.")
            return
        embed = discord.Embed(title="🎮 Latest Gaming News", url=url, color=discord.Color.dark_red())
        for title_tag, desc_tag in zip(titles[:10], descriptions[:10]):
            title_text = title_tag.get_text(strip=True)
            desc_text = desc_tag.get_text(strip=True)
            link_tag = title_tag.find('a')
            if link_tag and link_tag.get('href'):
                href = link_tag.get('href')
                if link_tag and link_tag.get('href'):
                    href = link_tag.get('href')
                    link = href if href.startswith('http') else f"https://ixbt.games/news/{href}"
                    value_text = f"{desc_text}\n👉 [Read Full Article]({link})"
                else:
                    value_text = desc_text
                
            embed.add_field(name=f"🔹 {title_text}", value=value_text, inline=False)
            
        embed.set_footer(text="Powered by iXBT.Games")
        await ctx.send(embed=embed)
@bot.command(name="books", description="Displays a list of books.")
async def books(ctx):
    url = "https://chitai-gorod.ru"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    async with ctx.typing():
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers) as response:
                    if response.status != 200:
                        await ctx.send("❌ Failed to load Chitai-Gorod website.")
                        return
                    html = await response.text()
            except Exception as e:
                await ctx.send(f"❌ An error occurred during the request: {e}")
                return
        soup = BeautifulSoup(html, 'html.parser')
        titles = soup.find_all('div', class_='product-card__title') or soup.find_all('a', class_='product-card__title')
        authors = soup.find_all('div', class_='product-card__author') or soup.find_all('span', class_='product-card__subtitle')
        prices = soup.find_all('div', class_='product-card__price') or soup.find_all('span', class_=['product-mini-card-price__price', 'product-card__price'])
        if not titles:
            await ctx.send("🔍 Could not find any books. The website layout might have changed.")
            return
        embed = discord.Embed(title="📚 Popular New Releases & Bestsellers from Chitai-Gorod", url=url, color=discord.Color.blue())
        for title_tag, author_tag, price_tag in zip(titles[:5], authors[:5], prices[:5]):
            title_text = title_tag.get_text(strip=True)
            author_text = author_tag.get_text(strip=True) if author_tag else "Author not specified"
            price_text = price_tag.get_text(strip=True) if price_tag else "Price not specified"
            href = title_tag.get('href') or (title_tag.find('a').get('href') if title_tag.find('a') else None)
            value_text = f"✍️ **Author:** {author_text}\n💰 **Price:** {price_text}"
            if href:
                link = href if href.startswith('http') else f"https://chitai-gorod.ru{href}"
                value_text += f"\n👉 [View on Website]({link})"
            embed.add_field(name=f"📖 {title_text}", value=value_text, inline=False)
        embed.set_footer(text="Powered by Chitai-Gorod")
        await ctx.send(embed=embed)
app = Flask(__name__)
@app.route('/')
def home():
    return "Humanity will live forever" 
def run_web_server():
    app.run(host='0.0.0.0', port=8080)
def keep_alive():
    t = Thread(target=run_web_server)
    t.start()
keep_alive()
bot.run(os.getenv('DISCORD_TOKEN'))
