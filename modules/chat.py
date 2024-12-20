from email import message
from pyexpat import model
from typing import Optional
import discord
from discord.ext import commands
from discord.ext.commands import Bot
from discord import app_commands
from openai import OpenAI
from modules.membercvtr import DisplayNameMemberConverter

class Chat(commands.Cog):
    def __init__(self, bot: Bot, client: OpenAI):
        self.bot = bot
        self.client = client
        print("Chat cog initialized")

    async def generate_chat(
            self, 
            messages: dict,
            max_tokens: int,
            temperature: float
        ):

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        joke = response.choices[0].message.content.strip()
        return joke

    @app_commands.command(name="chat", description="Echanger avec chatgpt")
    @app_commands.describe(
        message="Message à envoyer à chatgpt",
        systemprompt="system prompt (optionel)",
        model="Model à utiliser (ex: 'gpt-4o')",
        maxtokens="Nombre de tokens maximum (default: 1500)",
        temperature="Température, représente la variation des réponses (ex: 0.7, min:0, max: 2)"
    )
    async def chat(
            self, 
            interaction: discord.Interaction, 
            message: str,
            systemprompt: Optional[str] = None,
            model: Optional[str] = 'gpt-4o',
            maxtokens: Optional[int] = 1500,
            temperature: Optional[float] = 0.8,
        ):

        await interaction.response.defer(thinking=True)

        if not systemprompt: 
            systemprompt= "Vous êtes un assistant AI qui répond aux questions de l'utilisateur"

        try:
            # await ctx.send([member.display_name for member in ctx.guild.members])
            user = await DisplayNameMemberConverter().convert(interaction, interaction.message.author.name)
            print(user)

        except commands.MemberNotFound:
            await interaction.followup.send(f"User {user} not found.")
            return

        messages = [{
            "role": "system", "content": systemprompt
        }]

        async for message in interaction.channel.history(limit=1000):
            if message.author == user:
                messages.append({"role" : "user", "content" : message.content})
            if message.author == self.bot.user:
                messages.append({"role" : "assistant", "content" : message.content})

        if not messages:
            await interaction.followup.send(f"I couldn't find any messages from {user.mention}.")
            return
        
        print(messages)

        joke = await self.generate_chat(
            message=message,
            model=model,
            max_tokens=maxtokens,
            temperature=temperature
        )

        await interaction.followup.send(joke)

    @commands.Cog.listener()
    async def on_ready(self):
        print("Chat command is ready!")

async def setup(bot, client):
    await bot.add_cog(Chat(bot, client))
