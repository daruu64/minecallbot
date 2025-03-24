#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Telegram бот, который отслеживает ключевое слово 'Калл' в сообщениях
и отвечает фразой 'Созвать всех'.
"""

import logging
import os
import random
import html
from telegram import Update, Chat
from telegram.ext import Application, MessageHandler, CommandHandler, ContextTypes, filters
from telegram.error import TelegramError

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Безопасное хранение токена (замените на свой способ хранения)
API_TOKEN = '7223856263:AAHTo0KHmi-i0NstCJNA5WymvUaFMoLKKsM'

# Шаблоны сообщений для разнообразия
CALL_MESSAGES = [
    "🚨 <b>ВНИМАНИЕ!</b> Срочный сбор всех участников! 🚨",
    "📢 🔊 <b>Созываю всех!</b> Внимание, срочный сбор! 🔥",
    "⚡️ <b>Всем собраться!</b> Важное сообщение! ⚡️",
    "🎯 <b>Общий сбор!</b> Все на связь! 📡",
    "🔔 <b>Тревога!</b> Все в чат! 🔔"
]

CALL_WITH_TEXT_TEMPLATES = [
    "📣 <b>ОБЪЯВЛЕНИЕ:</b> <i>{additional_text}</i> 📣\n\n👥 {mention_text}",
    "🚩 <b>ВАЖНО:</b> <i>{additional_text}</i> 🚩\n\n👋 {mention_text}",
    "🎙️ <b>ПРИЗЫВ:</b> <i>{additional_text}</i> 🎙️\n\n⭐️ {mention_text}",
    "📌 <b>СООБЩЕНИЕ:</b> <i>{additional_text}</i> 📌\n\n👇 {mention_text}",
    "🔥 <b>СРОЧНО:</b> <i>{additional_text}</i> 🔥\n\n👀 {mention_text}"
]

CALL_MENTION_TEMPLATES = [
    "🔔 <b>Созываю всех:</b> {mention_text} 👋",
    "📢 <b>Внимание! Все сюда:</b> {mention_text} ⚡️",
    "🚨 <b>Общий сбор:</b> {mention_text} 🔥",
    "📣 <b>Всем явиться:</b> {mention_text} 🎯",
    "⭐️ <b>Вызываются:</b> {mention_text} 📌"
]

SEPARATOR = "\n➖➖➖➖➖➖➖➖➖➖➖➖\n"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start."""
    await update.message.reply_text('👋 <b>Привет!</b> Я бот, который отслеживает ключевое слово "Калл" 🔍', parse_mode="HTML")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /help."""
    help_text = (
        '📋 <b>Инструкция по использованию:</b>\n\n'
        '• Напишите "Калл" для созыва всех пользователей 📢\n'
        '• Напишите "Калл [текст]" для созыва с вашим сообщением 📝\n'
        '• Слово "калл" в любом сообщении также активирует бота 🔍'
    )
    await update.message.reply_text(help_text, parse_mode="HTML")

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
        members = []
        for member in admins:
            if not member.user.is_bot:
                if member.user.username:
                    members.append(f"@{member.user.username}")
                else:
                    members.append(f"<a href='tg://user?id={member.user.id}'>{html.escape(member.user.first_name)}</a>")
        
        return members
    except TelegramError as e:
        logger.error(f"Ошибка при получении участников чата: {e}")
        return []

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обрабатывает входящие сообщения и проверяет наличие ключевого слова.
    Если ключевое слово найдено, отправляет определённый ответ.
    """
    chat_id = update.effective_chat.id
    text = update.message.text

    # Проверка на точное соответствие сообщения "Калл"
    if text.lower() == "калл":
        logger.info("Запрошен список всех пользователей")
        
        # Получаем всех участников чата
        mentions = await get_all_members(context, chat_id)
        
        if mentions:
            mention_text = ", ".join(mentions)
            response = f"{SEPARATOR}{random.choice(CALL_MENTION_TEMPLATES).format(mention_text=mention_text)}{SEPARATOR}"
            await update.message.reply_text(response, parse_mode="HTML")
        else:
            await update.message.reply_text("⚠️ <b>Не удалось получить список участников чата.</b> ⚠️", parse_mode="HTML")
        
    # Проверка на шаблон "Калл [текст]"
    elif text.lower().startswith("калл ") and len(text) > 5:
        additional_text = text[5:]  # Текст после "Калл "
        logger.info(f"Запрошен список с дополнительным текстом: {additional_text}")
        
        # Получаем всех участников чата
        mentions = await get_all_members(context, chat_id)
        
        if mentions:
            mention_text = ", ".join(mentions)
            template = random.choice(CALL_WITH_TEXT_TEMPLATES)
            response = f"{SEPARATOR}{template.format(additional_text=additional_text, mention_text=mention_text)}{SEPARATOR}"
            await update.message.reply_text(response, parse_mode="HTML")
        else:
            await update.message.reply_text(f"⚠️ <b>Не удалось получить список участников чата:</b> <i>{additional_text}</i> ⚠️", parse_mode="HTML")
    
    elif "калл" in text.lower():
        logger.info(f"Обнаружено ключевое слово в сообщении: {text}")
        response = f"{SEPARATOR}{random.choice(CALL_MESSAGES)}{SEPARATOR}"
        await update.message.reply_text(response, parse_mode="HTML")
    else:
        logger.debug(f"Получено обычное сообщение: {text}")

def main() -> None:
    """Запуск бота."""
    application = Application.builder().token(API_TOKEN).build()
    
    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    
    # Регистрируем обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("🤖 Бот запущен и готов к работе! 🚀")
    # Запускаем бота до нажатия Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
