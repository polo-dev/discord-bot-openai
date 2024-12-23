import io
import aiohttp
import discord


class Helper():
    def split_message(self, message: str, limit: int = 2000) -> list:
        """Divise un message en plusieurs parties en respectant la limite de caractères."""
        parts = []
        while len(message) > limit:
            split_index = message.rfind("\n", 0, limit)
            if split_index == -1:
                split_index = limit
            parts.append(message[:split_index])
            message = message[split_index:].lstrip()
        parts.append(message)
        return parts

    async def upload_images(
            self,
            urls: dict
        ) -> list:
        """Upload plusieurs images via urls pour discord"""
        
        files = []

        async with aiohttp.ClientSession() as session:
            i = 0
            for url in urls:
                i = i+1
                async with session.get(url) as resp:
                    if resp.status != 200:
                        Exception('Error when downloading image from url')
                    data = io.BytesIO(await resp.read())
                    files.append(discord.File(data, f'generation_{i}.png'))

        return files
