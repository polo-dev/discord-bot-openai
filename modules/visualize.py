import io
import json
import discord
import aiohttp
from discord.ext import commands
from discord import app_commands
from openai import OpenAI
from typing import Optional
from modules.helper import Helper

class Visualize(commands.Cog):
    def __init__(self, bot, client: OpenAI):
        self.bot = bot
        self.client = client
        print("Visualize cog initialized")

    async def generate_image(
            self, 
            message: str,
            model: str,
            size: str,
            n: int,
            style: str,
            response_format: str,
            quality: str
        ):

        n = validate_n(n, model)
        model = validate_model(model)
         
        response = self.client.images.generate(
            prompt=message,
            model=model,
            size=size,
            n=n,
            style=style,
            response_format=response_format,
            quality=quality
        )

        print('response from api images create')
        images = response.data
        print(images)
        urls = [item.url for item in images]
        return urls
    
    @app_commands.command(name="generate", description="Générer une image")
    @app_commands.describe(
        message="Prompt décrivant l'image à générer",
        model="Modèle utilisé pour la génération (ex: 'dall-e-3')",
        size="Dimensions de l'image (ex: '1024x1024')",
        n="Nombre d'images à générer (ex: 1, 2, 3...)",
        style="Style de l'image (ex: 'natural', 'artistic')",
        response_format="Format de la réponse ('url' ou 'b64_json')",
        quality="Qualité de l'image, uniquement pour dall-e-3 (ex: 'standard', 'hd')"
    )
    async def generate(
            self,
            interaction: discord.Interaction,
            message: str,
            model: Optional[str] = 'dall-e-3',
            size: Optional[str] = '1024x1024',
            n: Optional[int] = 1,
            style: Optional[str] = 'natural',
            response_format: Optional[str] = 'url',
            quality: Optional[str] = 'standard'
        ):

        print("Début de la commande generate")

        await interaction.response.defer(thinking=True)

        print(f"Received generate command: {message}, model={model}, size={size}, n={n}, style={style}, response_format={response_format}, quality={quality}")

        # Créer un thread basé sur le message de commande
        thread = await interaction.channel.create_thread(
            name=f"Discussion avec {interaction.user.display_name}",
            type=discord.ChannelType.public_thread,
            message=await interaction.original_response(),
        )

        # Ajouter les variables au thread
        await thread.send(f'{{"type":"visualize","model":"{model}", "size":"{size}", "n":{n}, "style":"{style}", "quality":"{quality}" }}')

        await thread.send(f'**Prompt initial :** {message}')

        try:
            urls = await self.generate_image(
                message=message,
                model=model,
                size=size,
                n=n,
                style=style, 
                response_format=response_format,
                quality=quality
            )
            await interaction.followup.send(f'Génération d\'image avec : {model}')
        except Exception as e:
            await interaction.followup.send(f"Erreur: {str(e)}", ephemeral=True)

        try:
            files = await Helper().upload_images(urls)
            await thread.send(files=files)
        except Exception as e:
            await interaction.followup.send(f"Erreur: {str(e)}", ephemeral=True)

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
        except:
            params = False

        if not params or "type" not in params or params["type"] != 'visualize':
            return  

        thread = message.channel

        print("Parameters for vizualize")
        print(params)

        try:
            urls = await self.generate_image(
                message=message.content,
                model=params["model"],
                size=params["size"],
                n=params["n"],
                style=params["style"], 
                response_format="url",
                quality=params["quality"]
            )
            print(urls)
        except Exception as e:
            await thread.send(f"Erreur: {str(e)}")
        
        try:
            files = await Helper().upload_images(urls)
            await thread.send(files=files)
        except Exception as e:
            await thread.send(f"Erreur: {str(e)}")

    @commands.Cog.listener()
    async def on_ready(self):
        print("Visualize command is ready!")

async def setup(bot, client):
    await bot.add_cog(Visualize(bot, client))
    print("Visualize cog added to the bot.")

def validate_n(n: int, model: str):
    if model == 'dall-e-3' and n != 1:
        raise ValueError('for model dall-e-3 n need to be equal to 1')
    if n >= 1 or n <= 10:
        return n
    return ValueError('n shoud be between 1 and 10')

def validate_model(model: str):
    if model not in ['dall-e-3', 'dall-e-2']:
        return ValueError(f"The model should be dall-e-2 or dall-e-3 not {model}")
    return model