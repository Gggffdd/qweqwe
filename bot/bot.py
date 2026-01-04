import asyncio
import os
import logging
from typing import Optional
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Конфигурация
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8317412011:AAGopoDYX69WeeDo7YpqXRkCHKkmjoTR9eg")
ADMIN_ID = int(os.getenv("ADMIN_TELEGRAM_ID", "896706118"))
ORDER_GROUP_ID = int(os.getenv("ORDER_GROUP_ID", "3605074724"))
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Инициализация бота и диспетчера
bot = Bot(token=TELEGRAM_BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Стартовое меню
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user = message.from_user
    
    welcome_text = (
        f"👋 Добро пожаловать в <b>UNIVERSAL SHOP</b>!\n\n"
        f"Здесь вы найдете:\n"
        f"🎮 <b>Игры</b> - донаты, аккаунты, предметы\n"
        f"📱 <b>Приложения</b> - услуги Telegram\n\n"
        f"Для начала покупок откройте мини-приложение:"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Открыть магазин", web_app=types.WebAppInfo(url="https://ваш-домен.vercel.app"))],
        [InlineKeyboardButton(text="💬 Чат поддержки", url="https://t.me/ваш_чат")]
    ])
    
    await message.answer(welcome_text, reply_markup=keyboard)

# Админ команды
@dp.message(Command("admin"))
async def cmd_admin(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ У вас нет доступа к этой команде.")
        return
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton(text="📦 Управление товарами", callback_data="admin_products")],
        [InlineKeyboardButton(text="📋 Заказы", callback_data="admin_orders")],
        [InlineKeyboardButton(text="👥 Пользователи", callback_data="admin_users")],
    ])
    
    await message.answer("<b>Админ панель</b>\nВыберите действие:", reply_markup=keyboard)

# Обработка callback-запросов
@dp.callback_query(F.data.startswith("admin_"))
async def process_admin_callback(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("⛔ Нет доступа")
        return
    
    action = callback.data
    
    if action == "admin_stats":
        # Здесь будет логика получения статистики
        stats_text = (
            "<b>📊 Статистика магазина</b>\n\n"
            "👥 Пользователи: 150\n"
            "📦 Товаров: 45\n"
            "💰 Выручка: $2,340\n"
            "🛒 Заказов: 89\n"
            "✅ Выполнено: 78"
        )
        await callback.message.edit_text(stats_text)
    
    elif action == "admin_products":
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➕ Добавить товар", callback_data="add_product")],
            [InlineKeyboardButton(text="✏️ Редактировать", callback_data="edit_product")],
            [InlineKeyboardButton(text="🗑️ Удалить", callback_data="delete_product")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_back")]
        ])
        await callback.message.edit_text("<b>📦 Управление товарами</b>", reply_markup=keyboard)
    
    elif action == "admin_back":
        await cmd_admin(callback.message)
    
    await callback.answer()

# Обработка сообщений в группе заказов
@dp.message(F.chat.id == ORDER_GROUP_ID)
async def handle_order_group(message: types.Message):
    # Если это пересланное сообщение от бота с заказом
    if message.forward_from and message.forward_from.is_bot:
        # Добавляем кнопки для обработки заказа
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Подтвердить оплату", callback_data=f"confirm_{message.message_id}"),
                InlineKeyboardButton(text="🚚 Выдать товар", callback_data=f"deliver_{message.message_id}")
            ],
            [
                InlineKeyboardButton(text="❌ Отменить", callback_data=f"cancel_{message.message_id}"),
                InlineKeyboardButton(text="💬 Написать покупателю", callback_data=f"contact_{message.message_id}")
            ]
        ])
        
        # Редактируем сообщение, добавляя кнопки
        await message.edit_reply_markup(reply_markup=keyboard)

# Функция для отправки уведомления о новом заказе
async def send_order_notification(order_data: dict):
    """
    Отправляет уведомление о новом заказе в группу
    """
    text = (
        f"🛒 <b>НОВЫЙ ЗАКАЗ #{order_data.get('id', 'N/A')}</b>\n\n"
        f"👤 <b>Покупатель:</b> @{order_data.get('username', 'N/A')}\n"
        f"📦 <b>Товар:</b> {order_data.get('product_name', 'N/A')}\n"
        f"💰 <b>Сумма:</b> ${order_data.get('amount', 0)}\n"
        f"💳 <b>Способ оплаты:</b> {order_data.get('payment_method', 'N/A').upper()}\n"
        f"⏰ <b>Время:</b> {order_data.get('created_at', 'N/A')}\n\n"
        f"<i>Статус: ⏳ Ожидает оплаты</i>"
    )
    
    try:
        # Отправляем сообщение в группу заказов
        await bot.send_message(
            chat_id=ORDER_GROUP_ID,
            text=text,
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        logger.error(f"Error sending order notification: {e}")

# Команда для рассылки
@dp.message(Command("broadcast"))
async def cmd_broadcast(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    # Проверяем, есть ли текст рассылки
    if not message.reply_to_message:
        await message.answer("❌ Ответьте на сообщение для рассылки")
        return
    
    broadcast_text = message.reply_to_message.text or message.reply_to_message.caption
    
    # Здесь должна быть логика получения всех пользователей из БД
    # Для примера используем заглушку
    users = []  # Получаем из БД
    
    await message.answer(f"📢 Начинаю рассылку для {len(users)} пользователей...")
    
    success = 0
    failed = 0
    
    for user_id in users:
        try:
            await bot.send_message(user_id, broadcast_text)
            success += 1
            await asyncio.sleep(0.1)  # Задержка чтобы не превысить лимиты
        except Exception as e:
            failed += 1
            logger.error(f"Failed to send to {user_id}: {e}")
    
    await message.answer(
        f"✅ Рассылка завершена!\n"
        f"✅ Успешно: {success}\n"
        f"❌ Неудачно: {failed}"
    )

# Основная функция
async def main():
    logger.info("Starting bot...")
    
    # Пропускаем накопившиеся апдейты
    await bot.delete_webhook(drop_pending_updates=True)
    
    # Запускаем поллинг
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
