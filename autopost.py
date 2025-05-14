import time
import platform
import requests
import discord
import asyncio
import datetime
import aiohttp
import json
import io

from discord.ext import tasks

CONFIG_FILES = ["teks.json"]

def load_configs():
    configs = []
    for file in CONFIG_FILES:
        try:
            with open(file, "r", encoding="utf-8") as f:
                config = json.load(f)
                configs.append(config)
        except json.JSONDecodeError as e:
            print(f"❌ Gagal memuat {file}: Format JSON salah ({e})")
        except FileNotFoundError:
            print(f"❌ Gagal memuat {file}: File tidak ditemukan")
    return configs

configs = load_configs()

if not configs:
    print("\033[31mNO VALID CONFIGURATION. \033[96mMAKE SURE THE JSON FILE IS AVAILABLE AND CORRECT.\033[0m")
    exit()

intents = discord.Intents.default()
client = discord.Client(intents=intents, self_bot=True)
start_time = time.time()
auto_post_counts = {config["webhook_url"]: 0 for config in configs}

THUMBNAIL_IMG = "https://cdn.discordapp.com/attachments/1340674417331802146/1369739907169521744/image.png?ex=681cf532&is=681ba3b2&hm=88e76be8f64196edb287ec04ed34a2e53f134f0ff595770d4f07626d2074bf0d&"
BANNER_IMG = "https://media.discordapp.net/attachments/1340674417331802146/1342956055700967545/Proyek_Baru_43_41B5227.gif?ex=681c6b0a&is=681b198a&hm=8632c22b4390f29fc77097c7317f57c0354e166a960edd8a4fc7972871b6bd30&width=918&height=170&"

def detect_device():
    return {"Windows": "Windows", "Linux": "Linux", "Darwin": "macOS"}.get(platform.system(), "Android")

def generate_channel_link(channel_id):
    return f"<#{channel_id}>"

def parse_delay(delay_str):
    if isinstance(delay_str, (int, float)):
        return float(delay_str)

    time_units = {
        's': 1,
        'm': 60,
        'h': 3600
    }

    try:
        unit = delay_str[-1]
        value = float(delay_str[:-1])
        return value * time_units.get(unit.lower(), 60)  # default ke menit jika tidak dikenal
    except Exception as e:
        print(f"\033[1;31m[ERROR] Invalid delay format: {delay_str}. Defaulting to 60 seconds.\033[0m")
        return 60
        
def format_delay(delay_str):
    if isinstance(delay_str, (int, float)):
        return f"{int(delay_str)} minutes"
    delay_str = str(delay_str).lower()
    if delay_str.endswith("s"):
        return f"{int(delay_str[:-1])} seconds"
    elif delay_str.endswith("m"):
        return f"{int(delay_str[:-1])} minutes"
    elif delay_str.endswith("h"):
        return f"{int(delay_str[:-1])} hours"
    return f"{int(delay_str)} minutes"

@client.event
async def on_ready():
    print(f"\033[1;95m𝗜𝗛𝗔𝗡𝗡𝗦𝗬 𝗦𝗧𝗜𝗟𝗟 𝗪𝗔𝗧𝗖𝗛𝗜𝗡𝗚 𝗬𝗢𝗨!😈\033[0m")
    for config in configs:
        for channel_data in config["channel"]:
            asyncio.create_task(start_auto_post_channel(config, channel_data))

async def send_sticker_raw(channel_id, sticker_id, message, token):
    url = f"https://discord.com/api/v9/channels/{channel_id}/messages"
    headers = {
        "Authorization": token,
        "Content-Type": "application/json"
    }
    payload = {
        "content": message,
        "sticker_ids": [str(sticker_id)]
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as resp:
            if resp.status == 200 or resp.status == 204:
                return True, None
            else:
                text = await resp.text()
                return False, f"Status {resp.status}: {text}"

async def start_auto_post_channel(config, channel_data):
    channel_id = channel_data["id"]
    delay_seconds = parse_delay(channel_data["delay"])
    token = config["token"]
    webhook_url = config["webhook_url"]

    channel = client.get_channel(channel_id)
    if not channel:
        print(f"\033[1;31mCHANNEL {channel_id} NOT FOUND\033[0m.")
        return

    while True:
        try:
            message = channel_data["message"]
            sticker_id = channel_data.get("sticker_id")
            image_url = channel_data.get("image_url")

            if sticker_id:
                success, error = await send_sticker_raw(channel.id, sticker_id, message, token)
                if not success:
                    raise Exception(f"\033[1;33mFAILED TO SEND STICKER: {error}\033[0m")

            elif image_url:
                async with aiohttp.ClientSession() as session:
                    async with session.get(image_url) as resp:
                        if resp.status == 200:
                            data = await resp.read()
                            await channel.send(content=message, file=discord.File(io.BytesIO(data), 'image.png'))
                        else:
                            raise Exception(f"\033[1;31mFAILED TO DOWNLOAD IMAGE: Status {resp.status}\033[0m")

            else:
                await channel.send(message)

            auto_post_counts[webhook_url] += 1
            uptime = time.time() - start_time
            log_message(config, True, "\033[1;35mGET SENDING!", channel, uptime, channel_data)

            await asyncio.sleep(delay_seconds)

        except (aiohttp.ClientConnectorError, aiohttp.ClientOSError, discord.HTTPException) as conn_error:
            uptime = time.time() - start_time
            log_message(config, False, f"\033[1;33mCONNECTION ERROR! RETRYING IN 15s...\033[0m {conn_error}", channel, uptime, channel_data)
            print(f"\033[1;33m[WARN] \033[90m- \033[93mCONNECTION ISSUE DETECTED, RETRYING IN 15s...\033[0m")
            await asyncio.sleep(15)

        except Exception as e:
            uptime = time.time() - start_time
            log_message(config, False, f"\033[1;31mUNEXPECTED ERROR:\033[0m {e}", channel, uptime, channel_data)
            print(f"\033[1;31m[ERROR] \033[90m- \033[93mUNEXPECTED ERROR, RETRYING IN 15s...\033[0m")
            await asyncio.sleep(15 * 60)

def log_message(config, success, description, channel, uptime, channel_data):
    webhook_url = config["webhook_url"]
    status_emoji = "Status <a:statuson:1342594092068110442>" if success else "Error <a:eror:1342594207574921399>"
    status = "Success" if success else "check the delay time of the channel you are accessing, check your account token, check the arrangement of the .json file that you changed"

    channel_link = f"<#{channel.id}>"

    embed = {
        "title": "<a:emojioy:1342604312924393482> **AUTO POST LOG** <a:emojioy:1342604312924393482>",
        "description": "<a:emoji_15:1342599298373914696> Auto Post Premium <a:emoji_15:1342599298373914696>",
        "color": 0x00FF00 if success else 0xFF0000,
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
        "thumbnail": {"url": THUMBNAIL_IMG},
        "image": {"url": BANNER_IMG},
        "fields": [
            {"name": "User <a:emoji_14:1342599216827994112>", "value": client.user.mention, "inline": False},
            {"name": "Channel <a:Chat_Revival_Ping:1160448050087591996>", "value": channel_link, "inline": False},
            {"name": "Delay <a:emoji_17:1342603128507338814>", "value": format_delay(channel_data['delay']), "inline": True},
            {"name": "Device Used <a:emoji_11:1342592665337856021>", "value": detect_device(), "inline": True},
            {"name": f"{status_emoji}", "value": status, "inline": False},
            {"name": "Count of Messages <a:emoji_5:1342493516231610378>", "value": str(auto_post_counts[webhook_url]), "inline": True},
            {"name": "Uptime <a:emoji_16:1342599401473839114>", "value": f"{int(uptime // 86400)}d {int((uptime % 86400) // 3600)}h {int((uptime % 3600) // 60)}m {int(uptime % 60)}s", "inline": False},
        ],
        "footer": {
            "text": f"Auto Poster By iHannsy| Runtime: {int(uptime // 86400)}d {int((uptime % 86400) // 3600)}h {int((uptime % 3600) // 60)}m {int(uptime % 60)}s"
        }
    }

    response = requests.post(webhook_url, json={"embeds": [embed]})
    if response.status_code != 204:
        print(f"\033[1;31mERROR: \033[0m{response.status_code}, {response.text}")

    if success:
        print("\033[1;5;94miHannsy \033[90m- \033[1;92m[SUCCESS]] \033[90m- \033[1;96mLET'S GET THE SYSTEM RUNNING💥☠️\033[0m")
    else:
        print("\033[1;5;94miHannsy \033[90m- \033[1;31m[ERROR] \033[90m- \033[1;97mYOU ARE EITHER STUPID OR HAVE A SKILL ISSUE🖕\033[0m")

client.run(configs[0]["token"], bot=False)
