#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Telegram бот, который отслеживает ключевое слово 'Калл' в сообщениях
и отвечает фразой 'Созвать всех'.
"""

import logging
import os
import random
from telegram import Update, Chat
from telegram.ext import Application, MessageHandler, CommandHandler, ContextTypes, filters
from telegram.error import TelegramError

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levellevel)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Безопасное хранение токена (замените на свой способ хранения)
API_TOKEN = '7223856263:AAHTo0KHmi-i0NstCJNA5WymvUaFMoLKKsM'

# Шаблоны сообщений для разнообразия
CALL_MESSAGES = [
    "🚨 *ВНИМАНИЕ!* Срочный сбор всех участников! 🚨",
    "📢 🔊 *Созываю всех!* Внимание, срочный сбор! 🔥",
    "⚡️ *Всем собраться!* Важное сообщение! ⚡️",
    "🎯 *Общий сбор!* Все на связь! 📡",
    "🔔 *Тревога!* Все в чат! 🔔"
]

CALL_WITH_TEXT_TEMPLATES = [
    "📣 *ОБЪЯВЛЕНИЕ:* _{additional_text}_ 📣\n\n👥 {mention_text}",
    "🚩 *ВАЖНО:* _{additional_text}_ 🚩\n\n👋 {mention_text}",
    "🎙️ *ПРИЗЫВ:* _{additional_text}_ 🎙️\n\n⭐️ {mention_text}",
    "📌 *СООБЩЕНИЕ:* _{additional_text}_ 📌\n\n👇 {mention_text}",
    "🔥 *СРОЧНО:* _{additional_text}_ 🔥\n\n👀 {mention_text}"
]

CALL_MENTION_TEMPLATES = [
    "🔔 *Созываю всех:* {mention_text} 👋",
    "📢 *Внимание! Все сюда:* {mention_text} ⚡️",
    "🚨 *Общий сбор:* {mention_text} 🔥",
    "📣 *Всем явиться:* {mention_text} 🎯",
    "⭐️ *Вызываются:* {mention_text} 📌"
]

SEPARATOR = "\n➖➖➖➖➖➖➖➖➖➖➖➖\n"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start."""
    await update.message.reply_text('👋 *Привет!* Я бот, который отслеживает ключевое слово "Калл" 🔍', parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /help."""
    help_text = (
        '📋 *Инструкция по использованию:*\n\n'
        '• Напишите "Калл" для созыва всех пользователей 📢\n'
        '• Напишите "Калл [текст]" для созыва с вашим сообщением 📝\n'
        '• Слово "калл" в любом сообщении также активирует бота 🔍'
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

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
            response = f"{SEPARATOR}{random.choice(CALL_MENTION_TEMPLATES).format(mention_text=mention_text)}{SEPARATOR}"
            await update.message.reply_text(response, parse_mode="Markdown")
        else:
            await update.message.reply_text("⚠️ *Не удалось получить список пользователей.* ⚠️", parse_mode="Markdown")
    
    # Проверка на шаблон "Калл [текст]"
    elif text.lower().startswith("калл ") and len(text) > 5:
        additional_text = text[5:]  # Текст после "Калл "
        logger.info(f"Запрошен список с дополнительным текстом: {additional_text}")
        
        mentions, members = await get_mentions()
        
        if members:
            mention_text = ", ".join(mentions)
            template = random.choice(CALL_WITH_TEXT_TEMPLATES)
            response = f"{SEPARATOR}{template.format(additional_text=additional_text, mention_text=mention_text)}{SEPARATOR}"
            await update.message.reply_text(response, parse_mode="Markdown")
        else:
            await update.message.reply_text(f"⚠️ *Не удалось получить список пользователей для призыва:* _{additional_text}_ ⚠️", parse_mode="Markdown")
    
    # Проверяем, содержит ли сообщение ключевое слово (регистронезависимо)
    elif "калл" in text.lower():
        logger.info(f"Обнаружено ключевое слово в сообщении: {text}")
        response = f"{SEPARATOR}{random.choice(CALL_MESSAGES)}{SEPARATOR}"
        await update.message.reply_text(response, parse_mode="Markdown")
    else:
        logger.debug(f"Получено обычное сообщение: {text}")

# Add this command to let users register
async def register(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    # You'll need to create this dictionary in your application
    if 'registered_users' not in context.bot_data:
        context.bot_data['registered_users'] = {}
    
    if chat_id not in context.bot_data['registered_users']:
        context.bot_data['registered_users'][chat_id] = set()
    
    context.bot_data['registered_users'][chat_id].add(user_id)
    await update.message.reply_text("✅ Вы зарегистрированы для упоминаний!")

def main() -> None:
    """Запуск бота."""
    # Создаем экземпляр приложения
    application = Application.builder().token(API_TOKEN).build()

    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("register", register))
    
    # Регистрируем обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запускаем бота до нажатия Ctrl-C
    logger.info("🤖 Бот запущен и готов к работе! 🚀")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
