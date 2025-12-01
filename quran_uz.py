import logging
import os
import asyncio
import aiohttp
import re
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.utils.markdown import text
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


# Sura nomlarini raqamga o'girish lug'ati
SURA_MAP = {
    "fotiha": 1, "baqara": 2, "oliyimron": 3, "nison": 4, "moida": 5,
    "an'om": 6, "a'rof": 7, "anfol": 8, "tavba": 9, "yunus": 10,
    "hud": 11, "yusuf": 12, "ra'd": 13, "ibrohim": 14, "hijr": 15,
    "nahl": 16, "isro": 17, "kahf": 18, "maryam": 19, "toha": 20,
    "anbiyo": 21, "haj": 22, "mu'minun": 23, "nur": 24, "furqon": 25,
    "shuaro": 26, "naml": 27, "qasos": 28, "ankabut": 29, "rum": 30,
    "luqmon": 31, "sajda": 32, "ahzob": 33, "saba": 34, "fotir": 35,
    "yosin": 36, "saffat": 37, "sod": 38, "zumur": 39, "g'ofir": 40,
    "fussilat": 41, "shuro": 42, "zukhruf": 43, "duhon": 44, "josiya": 45,
    "ahqof": 46, "muhammad": 47, "fath": 48, "hujurot": 49, "qof": 50,
    "zoriyot": 51, "tur": 52, "najm": 53, "qamar": 54, "rahmon": 55,
    "voqea": 56, "hadid": 57, "mujodala": 58, "hashr": 59, "mumtahona": 60,
    "saff": 61, "jumu'a": 62, "munofiqun": 63, "tag'obun": 64, "taloq": 65,
    "tahrim": 66, "mulk": 67, "qalam": 68, "haqqa": 69, "ma'arij": 70,
    "nuh": 71, "jin": 72, "muzzammil": 73, "muddassir": 74, "qiyomat": 75,
    "inson": 76, "mursalot": 77, "naba": 78, "nazi'ot": 79, "abasa": 80,
    "takvir": 81, "infitor": 82, "mutoffifin": 83, "inshiqoq": 84, "buruj": 85,
    "toriq": 86, "a'la": 87, "g'oshiya": 88, "fajr": 89, "balad": 90,
    "shams": 91, "layl": 92, "zuho": 93, "sharh": 94, "tiyn": 95,
    "alaq": 96, "qadr": 97, "bayyina": 98, "zalzala": 99, "odiyat": 100,
    "qori'a": 101, "takasur": 102, "asr": 103, "humaza": 104, "fil": 105,
    "quraysh": 106, "ma'un": 107, "kavsar": 108, "kofirun": 109, "nasr": 110,
    "masad": 111, "ixlos": 112, "falaq": 113, "nos": 114,

    # Variantlar
    "yusuf": 12, "yusup": 12, "yousuf": 12,
    "omar": 2, "baqarah": 2,
    "imran": 3, "imron": 3,
    "fatiha": 1, "alfatiha": 1,
    "kahf": 18, "kavf": 18,
    "ya-sin": 36, "yaseen": 36,
    "ar-rahman": 55, "rahman": 55,
    "al-waqiah": 56, "waqiah": 56,
    "al-mulk": 67, "mulk": 67,
    "al-kahf": 18,
}


def get_sura_number(sura_input: str) -> int:
    """Sura nomi yoki raqamini qabul qilib, raqamini qaytaradi"""
    # Kichik harflarga o'tkazish va tozalash
    sura_input = sura_input.lower().strip()

    # Agar raqam bo'lsa
    if sura_input.isdigit():
        sura_num = int(sura_input)
        if 1 <= sura_num <= 114:
            return sura_num

    # Arabcha/inglizcha nomlar uchun tozalash
    sura_input = re.sub(r'[\s\-_\.]+', '', sura_input)
    sura_input = sura_input.replace("'", "").replace("ʻ", "").replace("ʼ", "").replace("ʾ", "")
    sura_input = sura_input.replace("gh", "g'").replace("ğ", "g'").replace("ʻ", "g'")

    # To'g'ridan-to'g'ri moslik
    if sura_input in SURA_MAP:
        return SURA_MAP[sura_input]

    # Qisman moslik
    for key, value in SURA_MAP.items():
        if sura_input in key or key in sura_input:
            return value

    return None


API_TOKEN = os.getenv("API_TOKEN2")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher()


@dp.message(Command("start", "help"))
async def send_welcome(message: Message):
    welcome_text = text(

        "Assalamu alaykum. Qur'on oyatlarini izlashga yordamlashadigan botga hush kelibsiz!\nbunda Shayx Muhammad Sodiq Muhammad Yusuf tarjimalariga asoslangan!",
        "",
        "📖 **Qidirish usullari:**",
        "1. Raqamlar bilan: `2 1` (2-sura 1-oyat)",
        "2. Nom bilan: `Yusuf 3` (Yusuf surasi 3-oyat)",
        "3. Nom bilan: `yusuf 3` (kichik harflarda)",
        "",
        "📌 **Namunalar:**",
        "• `1 1` - Fotiha surasi 1-oyat",
        "• `yasin 1` - Yosin surasi 1-oyat",
        "• `baqara 255` - Baqara surasi 255-oyat (Ayatul Kursi)",
        "• `mulk 1` - Mulk surasi 1-oyat",
        "",
        "Bot admini: ||@rahmonov_shaxzod||",
        sep="\n"
    )
    await message.reply(welcome_text)


@dp.message()
async def get_verse(message: Message):
    try:
        text_msg = message.text.strip()

        # Bo'sh xabar tekshirish
        if not text_msg:
            await message.answer("Iltimos, sura va oyatni kiriting!")
            return

        # Raqam va matnni ajratish
        parts = re.split(r'[\s,\-]+', text_msg, 1)

        if len(parts) < 2:
            await message.answer("Iltimos, sura va oyatni kiriting! Masalan: `Yusuf 3` yoki `2 1`")
            return

        sura_input = parts[0].strip()
        oyat_input = parts[1].strip()

        # Oyatni raqamga o'girish
        try:
            oyat = int(oyat_input)
            if oyat < 1:
                await message.answer("Oyat raqami 1 dan katta bo'lishi kerak!")
                return
        except ValueError:
            await message.answer("Oyat raqami noto'g'ri! Iltimos, raqam kiriting.")
            return

        # Sura raqamini topish
        sura = get_sura_number(sura_input)

        if not sura:
            await message.answer(f"'{sura_input}' nomli sura topilmadi! Iltimos, to'g'ri nom yoki raqam kiriting.")
            return

        # Sura raqamini tekshirish
        if sura < 1 or sura > 114:
            await message.answer("Sura raqami 1 dan 114 gacha bo'lishi kerak!")
            return

        # Oyatni olish
        natija = await quran_uzb(sura, oyat)

        # Sura nomini topish (teskari aylantirish)
        sura_name_uz = None
        for name, num in SURA_MAP.items():
            if num == sura and len(name) > 3:  # Eng uzun nomni olish
                sura_name_uz = name.capitalize()

        if natija and natija != "Oyat topilmadi":
            if sura_name_uz:
                response_text = f"📖 **{sura_name_uz} surasi ({sura}:{oyat})**\n\n{natija}"
            else:
                response_text = f"📖 **{sura}-sura ({oyat}-oyat)**\n\n{natija}"

            # Agar matn juda uzun bo'lsa, bo'laklarga ajratish
            if len(response_text) > 4000:
                # Birinchi bo'lak
                first_part = response_text[:4000]
                last_space = first_part.rfind(' ')
                if last_space != -1:
                    first_part = first_part[:last_space]

                await message.answer(first_part + "...")
                await message.answer("...davomi")
            else:
                await message.answer(response_text, parse_mode="Markdown")
        else:
            await message.answer(f"{sura}-suraning {oyat}-oyati topilmadi. Iltimos, oyat raqamini tekshiring.")

    except Exception as e:
        logger.error(f"Xatolik: {e}")
        await message.answer("Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring!")


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
