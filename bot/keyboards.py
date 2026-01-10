from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def article_kb(article_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👍 Like", callback_data=f"like:{article_id}"),
            InlineKeyboardButton(text="👎 Dislike", callback_data=f"dislike:{article_id}"),
        ],
        [
            InlineKeyboardButton(text="🔁 Recommend", callback_data="recommend:0"),
        ],
    ])
