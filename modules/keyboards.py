from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton


def logout(msgid):
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✖️ Logout", callback_data="logout_yes#{0}".format(msgid)),
        InlineKeyboardButton(text="❌ Annulla", callback_data="logout_no#{0}".format(msgid))
    ]])


def overviewExt(msgid):
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🇪🇺 Europa", callback_data="overview_ext#{0}".format(msgid))
    ]])


def overviewIta(msgid):
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🇮🇹 Italia", callback_data="overview_ita#{0}".format(msgid))
    ]])