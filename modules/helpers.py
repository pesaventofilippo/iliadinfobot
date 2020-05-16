from time import sleep
from telepot import Bot
from modules.database import User, Data

bot = None
maxMessageLength = 4096
adminIds = [368894926] # Bot Creator


def setBot(token):
    global bot
    bot = Bot(token)


def isAdmin(chatId=None):
    if not chatId:
        return adminIds
    return chatId in adminIds


def sendLongMessage(chatId, text: str, **kwargs):
    if len(text) <= maxMessageLength:
        return bot.sendMessage(chatId, text, **kwargs)

    parts = []
    while len(text) > 0:
        if len(text) > maxMessageLength:
            part = text[:maxMessageLength]
            first_lnbr = part.rfind('\n')
            if first_lnbr != -1:
                parts.append(part[:first_lnbr])
                text = text[(first_lnbr + 1):]
            else:
                parts.append(part)
                text = text[maxMessageLength:]
        else:
            parts.append(text)
            break

    msg = None
    for part in parts:
        msg = bot.sendMessage(chatId, part, **kwargs)
        sleep(0.5)
    return msg


def hasStoredCredentials(chatId):
    user = User.get(chatId=chatId)
    return (user.username != "") and (user.password != "")


def clearUserData(chatId):
    user = User.get(chatId=chatId)
    user.username = ""
    user.password = ""
    user.status = "normal"
    user.remainingCalls = 3

    data = Data.get(chatId=chatId)
    data.credito = 0
    data.dataRinnovo = ""
    data.nome = ""
    data.accountId = 0
    data.numero = ""

    data.totChiamate = {}
    data.costoChiamate = 0
    data.totSms = 0
    data.costoSms = 0
    data.totGiga = {}
    data.costoGiga = 0
    data.pianoGiga = {}
    data.totMms = 0
    data.costoMms = 0

    data.ext_totChiamate = {}
    data.ext_costoChiamate = 0
    data.ext_totSms = 0
    data.ext_costoSms = 0
    data.ext_totGiga = {}
    data.ext_costoGiga = 0
    data.ext_pianoGiga = {}
    data.ext_totMms = 0
    data.ext_costoMms = 0


def fetchAndStore(api, chatId):
    data = Data.get(chatId=chatId)
    data.credito = api.credito()
    data.dataRinnovo = api.dataRinnovo().strftime("%d/%m alle %H:%M")
    data.nome = api.nome()
    data.accountId = api.id()
    data.numero = api.numero()

    data.totChiamate = api.totChiamate()
    data.costoChiamate = api.costoChiamate()
    data.totSms = api.totSms()
    data.costoSms = api.costoSms()
    data.totGiga = api.totGiga()
    data.costoGiga = api.costoGiga()
    data.pianoGiga = api.pianoGiga()
    data.totMms = api.totMms()
    data.costoMms = api.costoMms()

    data.ext_totChiamate = api.totChiamate(estero=True)
    data.ext_costoChiamate = api.costoChiamate(estero=True)
    data.ext_totSms = api.totSms(estero=True)
    data.ext_costoSms = api.costoSms(estero=True)
    data.ext_totGiga = api.totGiga(estero=True)
    data.ext_costoGiga = api.costoGiga(estero=True)
    data.ext_pianoGiga = api.pianoGiga(estero=True)
    data.ext_totMms = api.totMms(estero=True)
    data.ext_costoMms = api.costoMms(estero=True)
