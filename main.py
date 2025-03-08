#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Telegram бот, который отслеживает ключевое слово 'Калл' в сообщениях
и отвечает фразой 'Созвать всех'.
"""

import logging
from telegram import Update, Chat
from telegram.ext import Application, MessageHandler, CommandHandler, ContextTypes, filters
from telegram.error import TelegramError

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Используйте ваш API_TOKEN, полученный от @BotFather
API_TOKEN = '7223856263:AAHTo0KHmi-i0NstCJNA5WymvUaFMoLKKsM'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start."""
    await update.message.reply_text('Привет! Я бот, который отслеживает ключевое слово "Калл".')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /help."""
    await update.message.reply_text('Напишите сообщение, содержащее слово "Калл", и я отвечу. Или напишите "ТестКалл", чтобы созвать всех пользователей.')

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

    # Проверка на точное соответствие сообщения "Калл"
    if text == "Калл":
        logger.info("Запрошен список всех пользователей")
        
        # Получаем список пользователей
        members = await get_all_members(context, update.effective_chat.id)
        
        if members:
            # Формируем сообщение с упоминаниями всех пользователей
            mentions = [f"@{member.username}" for member in members if member.username]
            
            # Если есть пользователи без username, добавляем их по имени
            for member in members:
                if not member.username:
                    name = member.first_name
                    if member.last_name:
                        name += f" {member.last_name}"
                    mentions.append(name)
            
            mention_text = ", ".join(mentions)
            await update.message.reply_text(f"Вызываю всех: {mention_text}")
        else:
            await update.message.reply_text("Не удалось получить список пользователей.")
    
    # Проверяем, содержит ли сообщение ключевое слово (регистронезависимо)
    elif "калл" in text.lower():
        logger.info(f"Обнаружено ключевое слово в сообщении: {text}")
        await update.message.reply_text('Созвать всех')
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
    logger.info("Бот запущен")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()