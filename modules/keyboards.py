from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton


def logout(msgid):
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✖️ Logout", callback_data="logout_yes#{0}".format(msgid)),
        InlineKeyboardButton(text="❌ Annulla", callback_data="logout_no#{0}".format(msgid))
    ]])
