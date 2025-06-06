import discord
from discord.ext import commands
import asyncio

class AccessLoggerBot(commands.Bot):
    def __init__(self, *, channel_id, **kwargs):
        super().__init__(**kwargs)
        self.channel_id = channel_id

    async def setup_hook(self):
        self.loop.create_task(self.wait_until_ready_and_notify())

    async def wait_until_ready_and_notify(self):
        await self.wait_until_ready()
        channel = self.get_channel(self.channel_id)
        if channel:
            await channel.send("Botが起動しました。")

    async def send_log(self, message):
        channel = self.get_channel(self.channel_id)
        if channel:
            await channel.send(message)

intents = discord.Intents.default()
intents.message_content = True

bot = AccessLoggerBot(command_prefix="!", channel_id=1366804810464235713, intents=intents)
