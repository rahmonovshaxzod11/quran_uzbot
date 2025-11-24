import logging
import os

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.utils.markdown import text
import asyncio
import aiohttp
from dotenv import load_dotenv

load_dotenv()

async def quran_uzb(sura, oyat):
    url_uz = f"https://cdn.jsdelivr.net/gh/fawazahmed0/quran-api@1/editions/uzb-muhammadsodikmu.json"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url_uz) as response:
                if response.status == 200:
                    data = await response.json()
                    for quran in data["quran"]:
                        if quran['chapter'] == sura and quran['verse'] == oyat:
                            return str(quran['text'])
                    return "Oyat topilmadi"
                else:
                    return "API ga ulanishda xatolik"
    except Exception as e:
        return f"Xatolik yuz berdi: {str(e)}"

API_TOKEN = os.getenv("API_TOKEN1")


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher()


@dp.message(Command("start", "help"))
async def send_welcome(message: Message):
    welcome_text = text(
        "Salom. Botimizga hush kelibsiz! Bu bot orqali istalgan oyat matnini topishingiz mumkin",
        "Masalan: 2 1 (2-sura 1-oyat) shu tartibda kiriting orasini bitta probel bilan ajratgan holda",
        "",
        "Bot admini: ||rahmonov_shaxzod||",
        sep="\n"
    )
    await message.reply(welcome_text)


@dp.message()
async def echo(message: Message):
    try:
        parts = message.text.split(" ")
        if len(parts) != 2:
            await message.answer("Iltimos, faqat 2 ta raqam kiriting (sura va oyat)!")
            return

        sura = int(parts[0])
        oyat = int(parts[1])

        # Validate sura and oyat numbers
        if sura < 1 or sura > 114:
            await message.answer("Sura raqami 1 dan 114 gacha bo'lishi kerak!")
            return

        natija = await quran_uzb(sura, oyat)

        if natija and natija != "Oyat topilmadi":
            response_text = f"{sura}-sura ({oyat}-oyat):\n\n{natija}"
            await message.answer(response_text)
        else:
            await message.answer("Bu sura va oyat kombinatsiyasida matn topilmadi. Iltimos, qaytadan tekshiring.")

    except ValueError:
        await message.answer("Iltimos, faqat raqamlardan foydalaning!")
    except Exception as e:
        logger.error(f"Xatolik: {e}")
        await message.answer("Iltimos qaytadan to'g'ri kiriting!!!!!")


async def main():
    try:
        # Delete webhook before starting polling
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Webhook successfully deleted")

        # Start polling
        logger.info("Starting bot polling...")
        await dp.start_polling(bot)

    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())