from pyrogram import Client
import config
from DAXXMUSIC.logging import LOGGER

class ProtectionClient(Client):
    def __init__(self):
        super().__init__(
            name="Protection",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.PROTECTION_STRING),
        )

    async def start(self):
        LOGGER(__name__).info(f"Starting Protection Client...")
        if config.PROTECTION_STRING:
            await super().start()
            try:
                await self.send_message(config.LOGGER_ID, "Protection Client Started")
            except:
                LOGGER(__name__).error(
                    "Protection Account has failed to access the log Group. Make sure that you have added your protection assistant to your log group and promoted as admin!"
                )
            
            self.id = self.me.id
            self.name = self.me.mention
            self.username = self.me.username
            LOGGER(__name__).info(f"Protection Client Started as {self.name}")

    async def stop(self):
        LOGGER(__name__).info(f"Stopping Protection Client...")
        try:
            if config.PROTECTION_STRING:
                await super().stop()
        except:
            pass
