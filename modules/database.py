from pony.orm import Database, Required, Optional, Json, StrArray

db = Database("sqlite", "../iliadinfobot.db", create_db=True)


class User(db.Entity):
    chatId = Required(int)
    username = Optional(str)
    password = Optional(str)
    status = Required(str, default="normal")
    remainingCalls = Required(int, default=3)


class Data(db.Entity):
    chatId = Required(int)
    credito = Optional(float)
    dataRinnovo = Optional(str)
    costoRinnovo = Optional(float)
    nome = Optional(str)
    accountId = Optional(int)
    numero = Optional(str)

    totChiamate = Optional(str)
    costoChiamate = Optional(float)
    totSms = Optional(int)
    costoSms = Optional(float)
    totGiga = Optional(Json)
    costoGiga = Optional(float)
    pianoGiga = Optional(Json)
    totMms = Optional(int)
    costoMms = Optional(float)

    ext_totChiamate = Optional(str)
    ext_costoChiamate = Optional(float)
    ext_totSms = Optional(int)
    ext_costoSms = Optional(float)
    ext_totGiga = Optional(Json)
    ext_costoGiga = Optional(float)
    ext_pianoGiga = Optional(Json)
    ext_totMms = Optional(int)
    ext_costoMms = Optional(float)


class Notifs(db.Entity):
    chatId = Required(int)
    active = Required(StrArray, default=["50%", "80%", "90%", "100%", "credito", "dailyData"])
    lastDataPerc = Required(float, default=0)
    dailyTrigger = Required(bool, default=False)
    lastGigaUsati = Required(float, default=0)


db.generate_mapping(create_tables=True)
