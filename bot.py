import logging
import re
import pathlib

from telegram import Update, MessageEntity
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import timezone

logging.basicConfig(level=logging.INFO)

TOKEN = "7676730172:AAHUtWkkpdFb9H3cDZT81utpjFMJZoinK18"
GROUP_CHAT_ID = 1001890799008

BASE_DIR = pathlib.Path(__file__).parent.resolve()
AD_IMAGE_PATH = BASE_DIR / "ad_banner.jpg"

CUSTOM_EMOJI_IDS = ["5206607081334906820", "5355012477883004708"]
PREMIUM_ADMINS = [123456789]  # Заменить на свои user_id

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


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Բարև! Ես Լոս Անջելես Հայեր խմբի բոտն եմ 😊")


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Հրամաններ:\n"
        "/premiumtest — պրեմիում գովազդի փորձ\n"
        "/getemojiid — ստանալ emoji ID\n"
        "/debugad — ստուգել գովազդի նկարը\n"
        "/testlaw — փորձել կանոնները\n"
        "/del — ջնջել հաղորդագրությունը, որի պատասխանին գրում եք այս հրամանը"
    )


async def premiumtest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    is_premium = user_id in PREMIUM_ADMINS or (getattr(update.effective_user, 'is_premium', False))
    text, entities = build_premium_ad(is_premium=is_premium)
    if AD_IMAGE_PATH.is_file():
        with open(AD_IMAGE_PATH, "rb") as f:
            await update.message.reply_photo(photo=f, caption=text)
    else:
        await update.message.reply_text(text=text)


async def getemojiid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.entities:
        ids = [e.custom_emoji_id for e in update.message.entities if e.type == "custom_emoji"]
        await update.message.reply_text("ID-ներ:\n" + "\n".join(ids) if ids else "Չգտա custom emoji.")
    else:
        await update.message.reply_text("Չգտա custom emoji.")


async def debugad(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if AD_IMAGE_PATH.is_file():
        with open(AD_IMAGE_PATH, "rb") as f:
            await update.message.reply_photo(photo=f, caption="Նկարի ստուգում:")
    else:
        await update.message.reply_text("Նկարը չկա!")


async def testlaw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await publish_first_law(context)
    await update.message.reply_text("✅ Կանոնները ուղարկվեցին")


async def publish_first_law(context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=first_law_text)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "") + " " + (update.message.caption or "")
    if re.search(r"(t\.me/[^\s]+|telegram\.me/[^\s]+)", text, re.IGNORECASE):
        try:
            await update.message.delete()
        except Exception as e:
            logging.warning(f"Не удалось удалить сообщение: {e}")


async def delete_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("Խնդրում եմ պատասխանեք այն հաղորդագրությանը, որը ցանկանում եք ջնջել, և նորից գրեք այս հրամանը։")
        return
    try:
        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.reply_to_message.message_id)
        await update.message.delete()
    except Exception as e:
        await update.message.reply_text(f"Չհաջողվեց ջնջել հաղորդագրությունը: {e}")


async def scheduled_publish_first_law(app):
    await app.bot.send_message(chat_id=GROUP_CHAT_ID, text=first_law_text)


async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("premiumtest", premiumtest))
    app.add_handler(CommandHandler("getemojiid", getemojiid))
    app.add_handler(CommandHandler("debugad", debugad))
    app.add_handler(CommandHandler("testlaw", testlaw))
    app.add_handler(CommandHandler("del", delete_message_handler))

    app.add_handler(MessageHandler(filters.TEXT | filters.Caption, handle_message))

    scheduler = AsyncIOScheduler(timezone=timezone("Asia/Yerevan"))
    scheduler.add_job(lambda: scheduled_publish_first_law(app), "cron", hour=9, minute=0)
    scheduler.start()

    await app.run_polling()


if __name__ == "__main__":
    import asyncio
    import nest_asyncio

    nest_asyncio.apply()

    asyncio.run(main())
