from typing import Optional
import discord
from discord.ext import commands
from discord.ext.commands import Bot
from discord import app_commands
from openai import OpenAI
import json
from modules.helper import Helper

class Chat(commands.Cog):
    def __init__(self, bot: Bot, client: OpenAI):
        self.bot = bot
        self.client = client
        print("Chat cog initialized")

    async def generate_chat(
            self, 
            messages: dict,
            max_tokens: int,
            temperature: float,
            model: str
        ):

        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )

        return response.choices[0].message.content.strip()

    @app_commands.command(name="chat", description="Echanger avec chatgpt")
    @app_commands.describe(
        prompt="Message à envoyer à chatgpt",
        systemprompt="system prompt (optionel)",
        model="Model à utiliser (ex: 'gpt-4o')",
        maxtokens="Nombre de tokens maximum (default: 1500)",
        temperature="Température, représente la variation des réponses (ex: 0.7, min:0, max: 2)"
    )
    async def chat(
            self, 
            interaction: discord.Interaction, 
            prompt: str,
            systemprompt: Optional[str] = None,
            model: Optional[str] = 'gpt-4o',
            maxtokens: Optional[int] = 1500,
            temperature: Optional[float] = 0.8,
        ):

        await interaction.response.defer(thinking=True)

        if not systemprompt: 
            systemprompt= "Vous êtes un assistant AI qui répond aux questions de l'utilisateur"

        # Créer un thread basé sur le message de commande
        thread = await interaction.channel.create_thread(
            name=f"Discussion avec {interaction.user.display_name}",
            type=discord.ChannelType.public_thread,
            message=await interaction.original_response(),
        )

        # Ajouter les variables au thread
        await thread.send(f'{{"type":"chat","model":"{model}", "maxtokens":{maxtokens}, "temperature":{temperature} }}')

        # Ajouter le prompt initial au thread
        await thread.send(f"**Prompt initial :** {prompt}")

        # Construire le contexte des messages
        messages = [{"role": "system", "content": systemprompt}]

        async for message in thread.history(limit=None, oldest_first=True):
            if message.author == interaction.user and len(message.content) > 1:
                messages.append({"role" : "user", "content" : message.content})
            if message.author == self.bot.user:
                messages.append({"role" : "assistant", "content" : message.content})

        # Ajouter le message initial en tant que premier message utilisateur
        messages.append({"role": "user", "content": prompt})
        
        answer = await self.generate_chat(
            messages=messages,
            model=model,
            max_tokens=maxtokens,
            temperature=temperature
        )

        # Répondre dans le thread
        for part in Helper().split_message(answer):
            await thread.send(part)

        await interaction.followup.send(f'Discussion avec model: {model}')

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # return if its a bot
        if message.author.bot:
            return

        #the first message is empty (the one that start the thread, so we take the second one)
        async for msg in message.channel.history(limit=2, oldest_first=True):
            first_message = msg

        # return if the thread is initiated by a human
        if first_message.author.bot is False:
            return

        try:
            # the first message should be the parameters in a json format
            params = json.loads(first_message.content)

            print("FROM JSON")
            print(params)
        except:
            params = False

        if first_message.author == self.bot.user and params and params["type"] == "chat":
            thread = message.channel

            # Construire le contexte des messages
            messages = []
            i = 0
            async for msg in thread.history(limit=None, oldest_first=True, after=first_message):
                
                if msg.author == message.author:
                    messages.append({"role": "user", "content": msg.content})
                elif msg.author == self.bot.user:
                    messages.append({"role": "assistant", "content": msg.content})
                i =+ 1

            # Ajouter le dernier message utilisateur
            messages.append({"role": "user", "content": message.content})

            print(messages)

            # Générer la réponse
            answer = await self.generate_chat(
                messages=messages,
                model=params["model"],  # Remplace par un modèle par défaut ou configurable
                max_tokens=params["maxtokens"],
                temperature=params["temperature"]
            )

            # Répondre dans le thread
            for part in Helper().split_message(answer):
                await thread.send(part)

    @commands.Cog.listener()
    async def on_ready(self):
        print("Chat command is ready!")

async def setup(bot, client):
    await bot.add_cog(Chat(bot, client))
    print("Chat cog added to the bot.")
