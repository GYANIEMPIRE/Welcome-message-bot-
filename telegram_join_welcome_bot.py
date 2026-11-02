import os
import logging
from html import escape

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    ChatJoinRequestHandler,
    ContextTypes,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ["BOT_TOKEN"]
MAIN_CHANNEL_ID = int(os.environ["MAIN_CHANNEL_ID"])
VIP_CHANNEL_LINK = os.environ["VIP_CHANNEL_LINK"]
ADMIN_USERNAME = os.environ["ADMIN_USERNAME"].lstrip("@")

WELCOME_TITLE = os.getenv(
    "WELCOME_TITLE",
    "✨ WELCOME TO OUR VIP CHANNEL ✨",
)
WELCOME_TEXT = os.getenv(
    "WELCOME_TEXT",
    "Thanks for your interest! You can visit our VIP channel using the link below.",
)


async def handle_join_request(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    request = update.chat_join_request
    if request is None:
        return

    # Only respond to requests for the configured main channel.
    if request.chat.id != MAIN_CHANNEL_ID:
        return

    # Telegram allows a bot admin with the required invite-users permission
    # to use user_chat_id to contact the requester for a limited time.
    user_chat_id = request.user_chat_id
    first_name = escape(request.from_user.first_name or "there")
    title = escape(WELCOME_TITLE)
    body = escape(WELCOME_TEXT)
    vip_link = escape(VIP_CHANNEL_LINK, quote=True)

    message = (
        f"👋 Hello {first_name}!\n\n"
        f"{title}\n\n"
        f"{body}\n\n"
        f'🔗 <a href="{vip_link}">Join our VIP Channel</a>'
    )

    keyboard = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton(
                "💬 CONTACT ADMIN",
                url=f"https://t.me/{ADMIN_USERNAME}",
            )
        ]]
    )

    try:
        await context.bot.send_message(
            chat_id=user_chat_id,
            text=message,
            parse_mode="HTML",
            reply_markup=keyboard,
            disable_web_page_preview=True,
        )
        logger.info("Welcome DM sent to requester ID %s", request.from_user.id)
    except Exception:
        logger.exception(
            "Could not send DM to requester ID %s. Check bot permissions "
            "and Telegram's temporary user_chat_id messaging window.",
            request.from_user.id,
        )


def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(ChatJoinRequestHandler(handle_join_request))
    logger.info("Bot started. Listening for join requests on channel %s", MAIN_CHANNEL_ID)
    app.run_polling(allowed_updates=["chat_join_request"])


if __name__ == "__main__":
    main()
