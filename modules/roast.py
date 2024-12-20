from discord.ext import commands
from discord import app_commands
from modules.membercvtr import DisplayNameMemberConverter

class Roast(commands.Cog):
    def __init__(self, bot, client):
        self.bot = bot
        self.client = client
        print("Roast cog initialized")

    async def generate_roast(self, user_name, messages):
        formatted_messages = [
            {"role": "system", "content": "Vous êtes un robot humoriste plein d'esprit qui critique les gens en fonction de leurs messages précédents. Vos critiques sont intelligentes, drôles et évitent tout langage offensant."},
            {"role": "user", "content": f"Voici quelques messages de {user_name}. Créez un rôti basé sur les sujets de ces messages. N'incluez pas de vrais noms:\n\n{messages}"}
        ]

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=formatted_messages,
            max_tokens=150,
            temperature=0.7
        )
        joke = response.choices[0].message.content.strip()
        return joke

    @app_commands.command(name="roast", description="Rôtissez un membre en fonction de ses messages récents.")
    @app_commands.describe(user_name="Nom ou mention de l'utilisateur à rôtir")
    async def roast(self, ctx, *, user_name: str):
        try:
            # await ctx.send([member.display_name for member in ctx.guild.members])
            user = await DisplayNameMemberConverter().convert(ctx, user_name)
            print(user)

        except commands.MemberNotFound:
            await ctx.send(f"User {user} not found.")
            return

        messages = []
        async for message in ctx.channel.history(limit=1000):
            if message.author == user:
                messages.append(message.content)

        if not messages:
            await ctx.send(f"I couldn't find any messages from {user.mention}.")
            return

        # Combine last 40 messages or less
        messages = "\n".join(messages[:40])

        print(user_name)

        joke = await self.generate_roast(user, messages)
        await ctx.send(joke)

    @commands.Cog.listener()
    async def on_ready(self):
        print("Roast command is ready!")

async def setup(bot, client):
    await bot.add_cog(Roast(bot, client))
