from openai import OpenAI
import discord
from discord.ext import commands
from dotenv import dotenv_values
from modules.roast import setup as setup_roast
from modules.visualize import setup as setup_visualize
from modules.visualize_edit import setup as setup_visualize_edit
from modules.visualize_variation import setup as setup_visualize_variation
from modules.chat import setup as setup_chat


config = dotenv_values(".env")

# Set OpenAI API key
bot_token = config["discord_bot_token"]

# Permissions we need
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.members = True

#openai
client = OpenAI(
    api_key=config["openai_api_key"],  # This is the default and can be omitted
)

# Declaring that our bot is named bot and that its command is !!
# It also gives the intents we set in the section above
bot = commands.Bot(command_prefix="!!", intents=intents)

@bot.event
async def on_ready():
    # Ajoute les cogs et démarre le bot
    await setup_roast(bot, client)
    print("Roast cog successfully added.")
    await setup_visualize(bot, client)
    print("Visualize cog successfully added.")
    await setup_visualize_edit(bot, client)
    print("Visualize Edit cog successfully added.")
    await setup_visualize_variation(bot, client)
    print("Visualize variation cog successfully added.")
    await setup_chat(bot, client)
    print("Chat cog successfully added.")

    try:
        guild = discord.Object(id=1213048098008342568)
        bot.tree.clear_commands(guild=guild)
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands synchronized.")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

    print(f"{bot.user.name} is online.")

bot.run(bot_token)