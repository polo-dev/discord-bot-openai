import discord
from discord.ext import commands
from discord import app_commands
from openai import OpenAI
from typing import Optional

class VisualizeVariation(commands.Cog):
    def __init__(self, bot, client: OpenAI):
        self.bot = bot
        self.client = client
        print("VisualizeVariation cog initialized")

    async def generate_image(
            self,
            model: str,
            image_data: bytes,
            size: str,
            n: int,
            response_format: str,
        ):

        params = {
            "model": model,
            "size": size,
            "image": image_data,
            "n": n,
            "response_format": response_format,
        }
         
        response = self.client.images.create_variation(**params)

        print('response from api images variation')
        images = response.data
        print(images)
        urls = [item.url for item in images]
        return "\n".join(urls)
    
    @app_commands.command(name="generate_variation", description="Créer une variation d'une image")
    @app_commands.describe(
        size="Dimensions de l'image (défaut: '1024x1024'), (option: '256x256', '512x512','1024x1024')",
        n="Nombre d'images à générer (ex: 1, 2, 3... 10), défaut: 1",
        file="Image à modifier, doit être un PNG de moins de 4mb, si aucun masque n'est définit, il faut ajouter"
    )
    async def generateVariation(
            self,
            interaction: discord.Interaction,
            file: discord.Attachment,
            size: Optional[str] = '1024x1024',
            n: Optional[int] = 1
        ):

        print("Début de la commande generate variation")

        await interaction.response.defer(thinking=True)

        print(f"Received generate variation command: size={size}, n={n}")

        # Lire les données de l'image
        try:
            image_data = await file.read()
        except Exception as e:
            await interaction.followup.send(f"Erreur lors de la lecture de l'image : {str(e)}", ephemeral=True)
            return

        try:
            urls = await self.generate_image(
                model='dall-e-2',
                size=size,
                n=n,
                response_format='url',
                image_data=image_data
            )
            print(urls)
            await interaction.followup.send(content=urls)
        except Exception as e:
            await interaction.followup.send(f"Erreur: {str(e)}", ephemeral=True)

    @commands.Cog.listener()
    async def on_ready(self):
        print("VisualizeVariation command is ready!")

async def setup(bot, client):
    await bot.add_cog(VisualizeVariation(bot, client))
    print("VisualizeVariation cog added to the bot.")