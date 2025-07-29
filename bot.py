import nest_asyncio
import asyncio
import logging
import re
import pathlib
from telegram import Update, MessageEntity
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import timezone

# === Логирование ===
logging.basicConfig(level=logging.INFO)

# === Конфигурация ===
TOKEN = "7676730172:AAHUtWkkpdFb9H3cDZT81utpjFMJZoinK18"  # ⚠️ Рекомендую вынести в переменную окружения
GROUP_CHAT_ID = -1001890799008

BASE_DIR = pathlib.Path(__file__).parent.resolve()
AD_IMAGE_PATH = BASE_DIR / "ad_banner.jpg"
SECOND_AD_IMAGE_PATH = BASE_DIR / "second_ad_banner.jpg"
THIRD_AD_IMAGE_PATH = BASE_DIR / "third_ad_banner.jpg"
FOURTH_AD_IMAGE_PATH = BASE_DIR / "fourth_ad_banner.jpg"

CUSTOM_EMOJI_IDS = ["5206607081334906820", "5355012477883004708"]
PREMIUM_ADMINS = [123456789]  # твой user_id

# === Տեքստեր ===
first_law_text = (
    "🔔 Ուշադրություն 🔔  \n"
    "‼️ Խմբի կանոնները ‼️ \n\n"
    "1️⃣ Գրեք հայերեն կամ լատինատառ  \n"
    "2️⃣ Չտարածել ուրիշ խմբեր\n"
    "3️⃣ Հարգել խմբի բոլոր անդամներին\n"
    "4️⃣ Քաղաքականություն չքննարկել\n"
    "5️⃣ Կրիմինալ պոստերը արգելվում է\n"
    "6️⃣ Ցանկացած գոծունեության գովազդը, որից եկամուտ եք ակնկալում, բացի Ձեր անձնական իրերի վաճառքից կամ վարձակալության հանձնելուց վճարովի է, գովազդի համար կապնվեք`@losangelosadmin"
)

SECOND_AD_TEXT = """Բարև Ձեզ   
🚘 Եթե ունեցել եք ավտովթար համեցեք իմ Body Shop :
✅  Արտաքին դեֆորմացիա (Body Work)
✅  Ներկում (Paint)
✅ Փոլիշ (Polish)
✅  Ընթացքային մասերի վերանորոգում (Suspension)
✅  Իրավաբանական օգնություն
📞 7475995550, 7473085876
📱 https://www.instagram.com/_carprof_
"""

THIRD_AD_TEXT = """Բարև Ձեզ👋
‼️ԱՄՆ ում բնակվող  բոլոր մարդկանց տրամադրում ենք Շենգենյան վիզաներ 10 օրվա ընթացքում‼️
Հարցերի դեպքում գրել` @VISA_SCHENGE
Հասցե` 500 N Brand Blvd, 20 floor
"""

FOURTH_AD_TEXT = (
    "❇️Մեր  ակադեմիան առաջարկում է Օնլայն  Ամերիկյան Անգլերենի դասեր ձեր ցանկացած վայրից և ցանկացած ժամի❇️\n"
    "✔️Սովորեք նորագույն մեթոդներով և արագ \n"
    "✔️Խոսակցական Ամերիկյան Անգլերեն\n"
    "✔️Հնարավոր և անհնար մեթոդներ արագ արդյունք ունենալու համար\n"
    "Հարցերի դեպքում կապնվեք` @elevate_academy1"
)


def build_premium_ad(is_premium=False):
    text = (
        "📺 First Stream TV\n"
        "✅  16,000+ ալիքներ\n"
        "✅  Ֆիլմեր • Սերիալներ • Սպորտ\n"
        "✅  Հասանելի է բոլոր սարքերում\n"
        "💸 Շատ մատչելի գին\n\n"
        "✅ Netflix\n✅ Match TV\n✅ Fast Sports TV\n✅ Discovery\n✅ National Geographic\n"
        "📲 Կապ՝ @vahekarapetyan10"
    )
    entities = []
    if is_premium:
        idx = 0
        emoji_index = 0
        while True:
            pos = text.find("☑", idx)
            if pos == -1:
                break
            custom_id = CUSTOM_EMOJI_IDS[emoji_index % len(CUSTOM_EMOJI_IDS)]
            entities.append(MessageEntity(type="custom_emoji", offset=pos, length=1, custom_emoji_id=custom_id))
            idx = pos + 1
            emoji_index += 1
    return text, entities

# --- Команды ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Բարև! Ես Լոս Անջելես Հայեր խմբի բոտն եմ 😊")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Հրամաններ:\n"
        "/premiumtest — պրեմիում գովազդի փորձ\n"
        "/getemojiid — ստանալ emoji ID\n"
        "/debugad — ստուգել գովազդի նկարը\n"
        "/testlaw — փորձել կանոնները\n"
        "/sendfirstad — ուղարկել 1-ին գովազդ\n"
        "/sendsecondad — ուղարկել 2-րդ գովազդ\n"
        "/sendthirdad — ուղարկել 3-րդ գովազդ (Շենգեն)\n"
        "/sendfourthad — ուղարկել 4-րդ գովազդ (Անգլերեն դասեր)\n"
        "/del — ջնջել այն հաղորդագրությունը, որի պատասխանին դուք գրում եք այս հրամանը"
    )

async def premiumtest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    is_premium = user_id in PREMIUM_ADMINS or (update.effective_user.is_premium or False)
    text, entities = build_premium_ad(is_premium=is_premium)
    if AD_IMAGE_PATH.is_file():
        with AD_IMAGE_PATH.open("rb") as f:
            await update.message.reply_photo(photo=f, caption=text, caption_entities=entities if is_premium else None)
    else:
        await update.message.reply_text(text=text)

async def getemojiid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ids = [e.custom_emoji_id for e in update.message.entities if e.type == "custom_emoji"] if update.message.entities else []
    await update.message.reply_text("ID-ներ:\n" + "\n".join(ids) if ids else "Չգտա custom emoji.")

async def debugad(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if AD_IMAGE_PATH.is_file():
        with AD_IMAGE_PATH.open("rb") as f:
            await update.message.reply_photo(photo=f, caption="Նկարի ստուգում:")
    else:
        await update.message.reply_text("Նկարը չկա!") 

async def testlaw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await publish_first_law(context.application)
    await update.message.reply_text("✅ Կանոնները ուղարկվեցին")

async def publish_first_ad_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await publish_ad(context.application)
    await update.message.reply_text("✅ Առաջին գովազդը ուղարկվեց")

async def publish_second_ad_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await publish_second_ad(context.application)
    await update.message.reply_text("✅ Երկրորդ գովազդը ուղարկվեց")

async def publish_third_ad_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await publish_third_ad(context.application)
    await update.message.reply_text("✅ Երրորդ գովազդը (Շենգեն) ուղարկվեց")

async def publish_fourth_ad_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await publish_fourth_ad(context.application)
    await update.message.reply_text("✅ Չորրորդ գովազդը (Անգլերեն դասեր) ուղարկվեց")

# === Добавленная команда удаления сообщения по ответу ===
async def delete_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("Խնդրում եմ պատասխանեք այն հաղորդագրությանը, որը ցանկանում եք ջնջել, և նորից գրեք այս հրամանը։")
        return

    msg_to_delete = update.message.reply_to_message
    chat_id = update.effective_chat.id

    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=msg_to_delete.message_id)
        await update.message.delete()
    except Exception as e:
        await update.message.reply_text(f"Չհաջողվեց ջնջել հաղորդագրությունը: {e}")

# === Автопубликация ===
async def publish_first_law(application):
    await application.bot.send_message(chat_id=GROUP_CHAT_ID, text=first_law_text)

async def publish_ad(application):
    text, entities = build_premium_ad(is_premium=True)
    if AD_IMAGE_PATH.is_file():
        with AD_IMAGE_PATH.open("rb") as f:
            await application.bot.send_photo(chat_id=GROUP_CHAT_ID, photo=f, caption=text, caption_entities=entities)
    else:
        await application.bot.send_message(chat_id=GROUP_CHAT_ID, text=text)

async def publish_second_ad(application):
    if SECOND_AD_IMAGE_PATH.is_file():
        with SECOND_AD_IMAGE_PATH.open("rb") as f:
            await application.bot.send_photo(chat_id=GROUP_CHAT_ID, photo=f, caption=SECOND_AD_TEXT)
    else:
        await application.bot.send_message(chat_id=GROUP_CHAT_ID, text=SECOND_AD_TEXT)

async def publish_third_ad(application):
    if THIRD_AD_IMAGE_PATH.is_file():
        with THIRD_AD_IMAGE_PATH.open("rb") as f:
            await application.bot.send_photo(chat_id=GROUP_CHAT_ID, photo=f, caption=THIRD_AD_TEXT)
    else:
        await application.bot.send_message(chat_id=GROUP_CHAT_ID, text=THIRD_AD_TEXT)

async def publish_fourth_ad(application):
    if FOURTH_AD_IMAGE_PATH.is_file():
        with FOURTH_AD_IMAGE_PATH.open("rb") as f:
            await application.bot.send_photo(chat_id=GROUP_CHAT_ID, photo=f, caption=FOURTH_AD_TEXT)
    else:
        await application.bot.send_message(chat_id=GROUP_CHAT_ID, text=FOURTH_AD_TEXT)

async def publish_both_ads(application):
    await publish_ad(application)
    await publish_second_ad(application)

# === Удаление ссылок ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    text = (update.message.text or "") + " " + (update.message.caption or "")
    if re.search(r"(t\.me/[^\s]+|telegram\.me/[^\s]+)", text, re.IGNORECASE):
        await update.message.delete()

async def main():
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_cmd))
    application.add_handler(CommandHandler("premiumtest", premiumtest))
    application.add_handler(CommandHandler("getemojiid", getemojiid))
    application.add_handler(CommandHandler("debugad", debugad))
    application.add_handler(CommandHandler("testlaw", testlaw))
    application.add_handler(CommandHandler("sendfirstad", publish_first_ad_cmd))
    application.add_handler(CommandHandler("sendsecondad", publish_second_ad_cmd))
    application.add_handler(CommandHandler("sendthirdad", publish_third_ad_cmd))
    application.add_handler(CommandHandler("sendfourthad", publish_fourth_ad_cmd))

    # Добавляем обработчик команды /del
    application.add_handler(CommandHandler("del", delete_message_handler))

    application.add_handler(MessageHandler(filters.TEXT | filters.CAPTION, handle_message))

    # ✅ Автопубликация
    arm_timezone = timezone("Asia/Yerevan")
    scheduler = AsyncIOScheduler(timezone=arm_timezone)
    scheduler.add_job(publish_first_law, "cron", hour=9, minute=0, args=[application])
    scheduler.add_job(publish_third_ad, "cron", hour=10, minute=0, args=[application])
    scheduler.add_job(publish_both_ads, "cron", hour=11, minute=0, args=[application])
    scheduler.add_job(publish_fourth_ad, "cron", hour=12, minute=0, args=[application])
    scheduler.add_job(publish_third_ad, "cron", hour=16, minute=0, args=[application])  # 6 ժամ տարբերություն՝ 10:00 և 16:00
    scheduler.start()

    await application.run_polling()

if __name__ == "__main__":
    nest_asyncio.apply()
    asyncio.run(main())

