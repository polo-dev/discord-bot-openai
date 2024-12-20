import discord
from discord.ext import commands
from discord import app_commands
from openai import OpenAI
from typing import Optional

class VisualizeEdit(commands.Cog):
    def __init__(self, bot, client: OpenAI):
        self.bot = bot
        self.client = client
        print("VisualizeEdit cog initialized")

    async def generate_image(
            self,
            model: str,
            image_data: bytes,
            message: str,
            size: str,
            n: int,
            response_format: str,
            image_data_mask: bytes|None
        ):

        params = {
            "prompt": message,
            "model": model,
            "size": size,
            "image": image_data,
            "n": n,
            "response_format": response_format,
        }

        if image_data_mask is not None:
            params["mask"] = image_data_mask
         
        response = self.client.images.edit(**params)

        print('response from api images create')
        images = response.data
        print(images)
        urls = [item.url for item in images]
        return "\n".join(urls)
    
    @app_commands.command(name="generate_edit", description="Editer une image via upload")
    @app_commands.describe(
        message="Prompt décrivant l'image à générer",
        size="Dimensions de l'image (défaut: '1024x1024'), (option: '256x256', '512x512','1024x1024')",
        n="Nombre d'images à générer (ex: 1, 2, 3... 10), défaut: 1",
        file="Image à modifier, doit être un PNG de moins de 4mb, si aucun masque n'est définit, il faut ajouter",
        filemask="Image mask"
    )
    async def generateEdit(
            self,
            interaction: discord.Interaction,
            message: str,
            file: discord.Attachment,
            filemask: Optional[discord.Attachment] = None,
            size: Optional[str] = '1024x1024',
            n: Optional[int] = 1
        ):

        print("Début de la commande generate")

        await interaction.response.defer(thinking=True)

        print(f"Received generate command: {message}, size={size}, n={n}")

        # Lire les données de l'image
        try:
            image_data = await file.read()
        except Exception as e:
            await interaction.followup.send(f"Erreur lors de la lecture de l'image : {str(e)}", ephemeral=True)
            return
        
        image_data_mask = None

        if filemask :
            # Lire les données de l'image
            try:
                image_data_mask = await filemask.read()
            except Exception as e:
                await interaction.followup.send(f"Erreur lors de la lecture du masque : {str(e)}", ephemeral=True)
                return
        try:
            urls = await self.generate_image(
                message=message,
                model='dall-e-2',
                size=size,
                n=n,
                response_format='url',
                image_data=image_data,
                image_data_mask=image_data_mask
            )
            print(urls)
            await interaction.followup.send(content=urls)
        except Exception as e:
            await interaction.followup.send(f"Erreur: {str(e)}", ephemeral=True)

    @commands.Cog.listener()
    async def on_ready(self):
        print("VisualizeEdit command is ready!")

async def setup(bot, client):
    await bot.add_cog(VisualizeEdit(bot, client))
    print("VisualizeEdit cog added to the bot.")