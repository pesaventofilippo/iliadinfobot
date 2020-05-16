from pony.orm import Database, Required, Optional

db = Database("sqlite", "../iliadinfobot.db", create_db=True)


class User(db.Entity):
    chatId = Required(int)
    username = Optional(str)
    password = Optional(str)
    status = Required(str, default="normal")


db.generate_mapping(create_tables=True)
