#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Telegram бот, который отслеживает ключевое слово 'Калл' в сообщениях
и отвечает фразой 'Созвать всех'.
"""

import logging
import os
import random
from telegram import Update, Chat, ParseMode
from telegram.ext import Application, MessageHandler, CommandHandler, ContextTypes, filters
from telegram.error import TelegramError

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Безопасное хранение токена через переменные окружения
import os
from dotenv import load_dotenv

# Загружаем переменные из .env файла (если есть)
load_dotenv()

# Получаем токен из переменных окружения или используем запасной вариант
API_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", '7223856263:AAHTo0KHmi-i0NstCJNA5WymvUaFMoLKKsM')

# Варианты сообщений для разнообразия
CALL_MESSAGES = [
    "🚨 *Внимание\!* Все сюда\! 🚨",
    "🔊 *Всем собраться\!* 📣",
    "📢 *Срочный сбор\!* ⚡",
    "🔔 *Общий сбор\!* 🆘",
    "🎯 *Созываю всех\!* 🎯"
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start."""
    await update.message.reply_text('👋 *Привет\!* Я бот, который отслеживает ключевое слово "*Калл*" 🤖', 
                                   parse_mode=ParseMode.MARKDOWN_V2)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /help."""
    help_text = (
        '📋 *Инструкция по использованию:*\n\n'
        '• Напишите "*Калл*" для созыва всех пользователей\n'
        '• Напишите "*Калл \[текст\]*" для созыва с вашим сообщением\n'
        '• Слово "*калл*" в любом сообщении также активирует бота'
    )
    await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN_V2)

async def get_all_members(context: ContextTypes.DEFAULT_TYPE, chat_id: int) -> list:
    """Получение списка всех пользователей в чате."""
    try:
        # Получение информации о чате
        chat = await context.bot.get_chat(chat_id)
        
        if chat.type == Chat.PRIVATE:
            # В личных чатах только один пользователь
            return []
        
        # Получаем администраторов чата (это доступная информация)
        admins = await context.bot.get_chat_administrators(chat_id)
        members = [member.user for member in admins if not member.user.is_bot]
        
        return members
    except TelegramError as e:
        logger.error(f"Ошибка при получении участников чата: {e}")
        return []

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обрабатывает входящие сообщения и проверяет наличие ключевого слова.
    Если ключевое слово найдено, отправляет определённый ответ.
    """
    text = update.message.text

    # Получаем список пользователей для упоминания
    async def get_mentions():
        members = await get_all_members(context, update.effective_chat.id)
        mentions = [f"@{member.username}" for member in members if member.username]
        
        # Если есть пользователи без username, добавляем их по имени
        for member in members:
            if not member.username:
                name = member.first_name
                if member.last_name:
                    name += f" {member.last_name}"
                mentions.append(name)
                
        return mentions, members

    # Проверка на точное соответствие сообщения "Калл"
    if text.lower() == "калл":
        logger.info("Запрошен список всех пользователей")
        
        mentions, members = await get_mentions()
        
        if members:
            mention_text = ", ".join(mentions)
            # Выбираем случайное сообщение из списка вариантов
            call_message = random.choice(CALL_MESSAGES)
            response = f"{'➖'*10}\n{call_message}\n\n👥 *Участники:*\n{mention_text}\n{'➖'*10}"
            await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN_V2)
        else:
            await update.message.reply_text("⚠️ *Не удалось получить список пользователей\.* 😔", 
                                          parse_mode=ParseMode.MARKDOWN_V2)
    
    # Проверка на шаблон "Калл [текст]"
    elif text.lower().startswith("калл ") and len(text) > 5:
        additional_text = text[5:]  # Текст после "Калл "
        logger.info(f"Запрошен список с дополнительным текстом: {additional_text}")
        
        mentions, members = await get_mentions()
        
        if members:
            mention_text = ", ".join(mentions)
            # Экранируем спецсимволы Markdown в additional_text
            escaped_text = additional_text.replace(".", "\\.").replace("-", "\\-").replace("!", "\\!").replace("(", "\\(").replace(")", "\\)")
            response = (f"{'➖'*10}\n"
                       f"📢 *Призыв:* _{escaped_text}_\n\n"
                       f"👥 *Участники:*\n{mention_text}\n"
                       f"{'➖'*10}")
            await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN_V2)
        else:
            await update.message.reply_text(f"⚠️ *Не удалось получить список пользователей для призыва\.* 😔\n\n"
                                         f"_Текст призыва:_ {additional_text}", 
                                         parse_mode=ParseMode.MARKDOWN_V2)
    
    # Проверяем, содержит ли сообщение ключевое слово (регистронезависимо)
    elif "калл" in text.lower():
        logger.info(f"Обнаружено ключевое слово в сообщении: {text}")
        await update.message.reply_text('📢 🔊 *Созываю всех\!* Внимание, срочный сбор\! 🚨 🔥', 
                                      parse_mode=ParseMode.MARKDOWN_V2)
    else:
        logger.debug(f"Получено обычное сообщение: {text}")

def main() -> None:
    """Запуск бота."""
    # Создаем экземпляр приложения
    application = Application.builder().token(API_TOKEN).build()

    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    
    # Регистрируем обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запускаем бота до нажатия Ctrl-C
    logger.info("🤖 Бот запущен")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
