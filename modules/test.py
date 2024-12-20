import discord
from discord.ext import commands
from discord import app_commands

class TestCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="test", description="Commande de test")
    async def test(self, interaction: discord.Interaction):
        await interaction.response.send_message("Test command works!")

async def setup(bot):
    await bot.add_cog(TestCog(bot))