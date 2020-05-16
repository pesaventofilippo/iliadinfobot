from pony.orm import Database, Required, Optional, Json

db = Database("sqlite", "../iliadinfobot.db", create_db=True)


class User(db.Entity):
    chatId = Required(int)
    username = Optional(str)
    password = Optional(str)
    status = Required(str, default="normal")


class Data(db.Entity):
    chatId = Required(int)
    credito = Optional(int)
    dataRinnovo = Optional(str)
    nome = Optional(str)
    accountId = Optional(int)
    numero = Optional(str)
    totChiamate = Optional(Json)
    costoChiamate = Optional(float)
    totSms = Optional(int)
    costoSms = Optional(float)
    totGiga = Optional(Json)
    costoGiga = Optional(float)
    pianoGiga = Optional(Json)
    totMms = Optional(int)
    costoMms = Optional(float)


db.generate_mapping(create_tables=True)
