"""Telegram bot integration."""
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from langchain_core.messages import HumanMessage
from langfuse.callback import CallbackHandler
import textwrap

from src.config import Config


def create_bot(graph, cfg: Config) -> Application:
    langfuse_handler = CallbackHandler(
        public_key=cfg.langfuse.public_key,
        secret_key=cfg.langfuse.secret_key,
        host=cfg.langfuse.host,
    )

    app = Application.builder().token(cfg.telegram.bot_token).build()

    async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_input = update.message.text
        chat_id = str(update.effective_chat.id)

        state = {
            "messages": [HumanMessage(content=user_input)],
            "thread_id": chat_id,
        }

        await update.message.chat.send_action("typing")

        try:
            config = {
                "configurable": {"thread_id": chat_id},
                "callbacks": [langfuse_handler],
            }
            result = await graph.ainvoke(state, config)
            last_msg = result["messages"][-1]
            response = last_msg.content

            # Telegram has 4096 char limit
            if len(response) > 4000:
                chunks = textwrap.wrap(response, 4000, break_long_words=False)
                for chunk in chunks:
                    await update.message.reply_text(chunk)
            else:
                await update.message.reply_text(response)

        except Exception as e:
            await update.message.reply_text(f"Error: {e}")

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    return app
