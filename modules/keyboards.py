from telepotpro.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton


def logout():
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✖️ Logout", callback_data="logout_yes"),
        InlineKeyboardButton(text="❌ Annulla", callback_data="logout_no")
    ]])


def overviewExt():
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🇪🇺 Europa", callback_data="overview_ext")
    ]])


def overviewIta():
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🇮🇹 Italia", callback_data="overview_ita")
    ]])
