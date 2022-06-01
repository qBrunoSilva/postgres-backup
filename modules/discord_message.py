from discord import Webhook, RequestsWebhookAdapter, Embed
from dotenv import load_dotenv
import os

load_dotenv()

URL = os.getenv('WEBHOOK_URL')
TOKEN = os.getenv('DISCORD_TOKEN')

class DiscordBot():
    def __init__(self) -> None:
        self.webhook = Webhook.from_url(
            URL, adapter=RequestsWebhookAdapter())

    def send_success_message(self, message):
        embed = Embed(title="Wise GEC - Daily Backup",
                      description=f":rocket: {message}", color=0x00ff00)
        self.webhook.send(embed=embed)

    def send_warning_message(self, message):
        embed = Embed(title="Wise GEC - Daily Backup",
                      description=f":warning: {message}", color=0xffc222)
        self.webhook.send(embed=embed)

    def send_fail_message(self, message):
        embed = Embed(title="Wise GEC - Daily Backup",
                      description=f":x: {message}", color=0xff0000)
        self.webhook.send(embed=embed)


if __name__ == "__main__":
    bot = DiscordBot()
    bot.send_success_message("Teste Success Message!")
    bot.send_warning_message("Teste Warning Message!")
    bot.send_fail_message("Teste Fail Message!")
