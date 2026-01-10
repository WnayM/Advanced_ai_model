from __future__ import annotations

import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from bot.config import BOT_TOKEN, API_URL
from bot.api import GatewayClient
from bot.keyboards import article_kb

client = GatewayClient(API_URL)


def user_external_id_from_message(m: Message) -> str:
    # можно сделать по-другому (username/phone), но telegram user_id норм как внешний ключ
    return str(m.from_user.id)


def user_external_id_from_callback(c: CallbackQuery) -> str:
    return str(c.from_user.id)


async def cmd_start(m: Message):
    ext = user_external_id_from_message(m)
    await client.ensure_user(ext)
    await m.answer(
        "Привет! Я бот новостей.\n\nКоманды:\n"
        "/news — последние новости\n"
        "/recommend — рекомендации (нужно хотя бы 1 лайк)\n"
        "/help — помощь"
    )


async def cmd_help(m: Message):
    await m.answer(
        "Как пользоваться:\n"
        "1) /news — получи новости\n"
        "2) ставь 👍/👎\n"
        "3) /recommend — получи рекомендации"
    )


async def cmd_news(m: Message):
    ext = user_external_id_from_message(m)
    await client.ensure_user(ext)

    arts = await client.latest_articles(limit=5, offset=0)
    if not arts:
        await m.answer("Пока нет новостей. Попробуй позже.")
        return

    for a in arts:
        text = f"📰 <b>{a.title}</b>\n{a.url}\n\nИсточник: {a.source}"
        await m.answer(text, reply_markup=article_kb(a.id))


async def cmd_recommend(m: Message):
    ext = user_external_id_from_message(m)
    await client.ensure_user(ext)

    try:
        recs = await client.recommend(ext, top_k=5)
    except Exception as e:
        await m.answer(f"Не могу рекомендовать: {e}")
        return

    if not recs:
        await m.answer("Рекомендаций пока нет.")
        return

    lines = ["🎯 <b>Твои рекомендации:</b>\n"]
    for it in recs:
        lines.append(f"• <b>{it['title']}</b>\n{it['url']}\nscore={it['score']:.3f}\n")
    await m.answer("\n".join(lines))


async def on_article_vote(cb: CallbackQuery):
    ext = user_external_id_from_callback(cb)
    data = cb.data or ""
    action, article_id_s = data.split(":", 1)
    article_id = int(article_id_s)

    await client.event(ext, article_id, action)
    await cb.answer("Сохранено ✅", show_alert=False)


async def on_recommend_button(cb: CallbackQuery):
    ext = user_external_id_from_callback(cb)
    try:
        recs = await client.recommend(ext, top_k=5)
    except Exception as e:
        await cb.message.answer(f"Не могу рекомендовать: {e}")
        await cb.answer()
        return

    if not recs:
        await cb.message.answer("Рекомендаций пока нет.")
        await cb.answer()
        return

    lines = ["🎯 <b>Рекомендации:</b>\n"]
    for it in recs:
        lines.append(f"• <b>{it['title']}</b>\n{it['url']}\nscore={it['score']:.3f}\n")
    await cb.message.answer("\n".join(lines))
    await cb.answer()


async def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is empty")

    bot = Bot(BOT_TOKEN, parse_mode="HTML")
    dp = Dispatcher()

    dp.message.register(cmd_start, Command("start"))
    dp.message.register(cmd_help, Command("help"))
    dp.message.register(cmd_news, Command("news"))
    dp.message.register(cmd_recommend, Command("recommend"))

    dp.callback_query.register(on_article_vote, F.data.startswith("like:"))
    dp.callback_query.register(on_article_vote, F.data.startswith("dislike:"))
    dp.callback_query.register(on_recommend_button, F.data.startswith("recommend:"))

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
