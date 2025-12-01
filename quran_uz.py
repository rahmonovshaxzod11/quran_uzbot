import logging
import os
import asyncio
import aiohttp
import re
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from aiohttp import web
from dotenv import load_dotenv

load_dotenv()

# 1. Qur'on API funksiyasi
async def quran_uzb(sura, oyat):
    url_uz = "https://cdn.jsdelivr.net/gh/fawazahmed0/quran-api@1/editions/uzb-muhammadsodikmu.json"
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

# 2. Sura lug'ati
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
    "nuh": 71, "jin": 72, "muzzammil": 73, "muddassir": 74, "qiyamat": 75,
    "inson": 76, "mursalot": 77, "naba": 78, "nazi'ot": 79, "abasa": 80,
    "takvir": 81, "infitor": 82, "mutoffifin": 83, "inshiqoq": 84, "buruj": 85,
    "toriq": 86, "a'la": 87, "g'oshiya": 88, "fajr": 89, "balad": 90,
    "shams": 91, "layl": 92, "zuho": 93, "sharh": 94, "tiyn": 95,
    "alaq": 96, "qadr": 97, "bayyina": 98, "zalzala": 99, "odiyat": 100,
    "qori'a": 101, "takasur": 102, "asr": 103, "humaza": 104, "fil": 105,
    "quraysh": 106, "ma'un": 107, "kavsar": 108, "kofirun": 109, "nasr": 110,
    "masad": 111, "ixlos": 112, "falaq": 113, "nos": 114,
    "yusup": 12, "baqarah": 2, "imran": 3, "fatiha": 1, "kavf": 18,
    "ya-sin": 36, "yaseen": 36, "ar-rahman": 55, "al-waqiah": 56,
}

def get_sura_number(sura_input: str):
    sura_input = sura_input.lower().strip()
    
    if sura_input.isdigit():
        sura_num = int(sura_input)
        if 1 <= sura_num <= 114:
            return sura_num
    
    sura_input = re.sub(r'[\s\-_\.]+', '', sura_input)
    sura_input = sura_input.replace("'", "").replace("ʻ", "").replace("ʼ", "").replace("ʾ", "")
    sura_input = sura_input.replace("gh", "g'").replace("ğ", "g'").replace("ʻ", "g'")
    
    if sura_input in SURA_MAP:
        return SURA_MAP[sura_input]
    
    for key, value in SURA_MAP.items():
        if sura_input in key or key in sura_input:
            return value
    
    return None

# 3. Bot konfiguratsiyasi
API_TOKEN = os.getenv("API_TOKEN1")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# 4. Handlerlar
@dp.message(Command("start", "help"))
async def send_welcome(message: Message):
    welcome_text = (
        "Salom. Qur'on botiga hush kelibsiz!\n\n"
        "<b>📖 Qidirish usullari:</b>\n"
        "1. Raqamlar bilan: <code>2 1</code> (2-sura 1-oyat)\n"
        "2. Nom bilan: <code>Yusuf 3</code> (Yusuf surasi 3-oyat)\n"
        "3. Nom bilan: <code>yusuf 3</code> (kichik harflarda)\n\n"
        "<b>📌 Namunalar:</b>\n"
        "• <code>1 1</code> - Fotiha surasi 1-oyat\n"
        "• <code>yasin 1</code> - Yosin surasi 1-oyat\n"
        "• <code>baqara 255</code> - Baqara surasi 255-oyat (Ayatul Kursi)\n"
        "• <code>mulk 1</code> - Mulk surasi 1-oyat\n\n"
        "Bot admini: @rahmonov_shaxzod"
    )
    await message.reply(welcome_text, parse_mode="HTML")

@dp.message()
async def get_verse(message: Message):
    try:
        text_msg = message.text.strip()
        
        if not text_msg:
            await message.answer("Iltimos, sura va oyatni kiriting!")
            return
        
        parts = re.split(r'[\s,\-]+', text_msg, 1)
        
        if len(parts) < 2:
            await message.answer("Iltimos, sura va oyatni kiriting! Masalan: <code>Yusuf 3</code> yoki <code>2 1</code>", 
                               parse_mode="HTML")
            return
        
        sura_input, oyat_input = parts[0].strip(), parts[1].strip()
        
        try:
            oyat = int(oyat_input)
            if oyat < 1:
                await message.answer("Oyat raqami 1 dan katta bo'lishi kerak!")
                return
        except ValueError:
            await message.answer("Oyat raqami noto'g'ri! Iltimos, raqam kiriting.")
            return
        
        sura = get_sura_number(sura_input)
        
        if not sura:
            await message.answer(f"<b>'{sura_input}'</b> nomli sura topilmadi!", parse_mode="HTML")
            return
        
        if sura < 1 or sura > 114:
            await message.answer("Sura raqami 1 dan 114 gacha bo'lishi kerak!")
            return
        
        natija = await quran_uzb(sura, oyat)
        
        if natija and natija != "Oyat topilmadi":
            sura_name_uz = None
            for name, num in SURA_MAP.items():
                if num == sura and len(name) > 3:
                    sura_name_uz = name.capitalize()
            
            if sura_name_uz:
                response_text = f"<b>📖 {sura_name_uz} surasi ({sura}:{oyat})</b>\n\n{natija}"
            else:
                response_text = f"<b>📖 {sura}-sura ({oyat}-oyat)</b>\n\n{natija}"
            
            await message.answer(response_text, parse_mode="HTML")
        else:
            await message.answer(f"<b>{sura}-suraning {oyat}-oyati topilmadi.</b>", parse_mode="HTML")
    
    except Exception as e:
        logger.error(f"Xatolik: {e}")
        await message.answer("Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring!")

# 5. HTTP server port ochish uchun
async def health_check(request):
    return web.Response(text="Qur'on bot ishlamoqda...")

async def start_bot():
    """Botni alohida task sifatida ishga tushirish"""
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Bot polling ishga tushdi...")
    await dp.start_polling(bot)

async def main():
    """Asosiy funksiya - HTTP server va botni birga ishga tushiradi"""
    port = int(os.getenv("PORT", 8080))
    
    # HTTP server yaratish
    app = web.Application()
    app.router.add_get('/', health_check)
    app.router.add_get('/health', health_check)
    
    # Botni background task sifatida ishga tushirish
    bot_task = asyncio.create_task(start_bot())
    
    # HTTP serverni ishga tushirish
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    
    logger.info(f"✅ Server {port}-portda ishga tushdi")
    logger.info(f"✅ Bot polling rejimida ishlamoqda")
    
    # Ikkala task ham tugaguncha kutish
    try:
        await asyncio.gather(bot_task)
    except KeyboardInterrupt:
        logger.info("Dastur to'xtatildi")
    finally:
        await runner.cleanup()

if __name__ == '__main__':
    asyncio.run(main())
