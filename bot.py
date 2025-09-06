import os, yt_dlp, re
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("TOKEN")
DOWNLOADS_DIR = "downloads"
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

URL_RX = re.compile(r"https?://\S+", re.IGNORECASE)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎬 Send me any video link and I’ll fetch it for you!")

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    m = URL_RX.search(text)
    if not m:
        return await update.message.reply_text("❌ Please send a valid link.")
    url = m.group(0)

    await update.message.reply_text("⏳ Downloading…")

    ydl_opts = {
        "outtmpl": os.path.join(DOWNLOADS_DIR, "%(title).50s.%(ext)s"),
        "format": "bestvideo+bestaudio/best",
        "merge_output_format": "mp4"
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        if os.path.getsize(file_path) > 50 * 1024 * 1024:
            await update.message.reply_text("⚠️ Video is too large for Telegram (50 MB limit).")
        else:
            await update.message.reply_video(video=open(file_path, "rb"))

        os.remove(file_path)

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    app.run_polling()

if __name__ == "__main__":
    main()
