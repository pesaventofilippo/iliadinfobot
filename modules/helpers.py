from modules.database import User, Data, Notifs

adminIds = [368894926] # Bot Creator


def isAdmin(chatId=None):
    if not chatId:
        return adminIds
    return chatId in adminIds


def hasStoredCredentials(chatId):
    user = User.get(chatId=chatId)
    return (user.username != "") and (user.password != "")


def clearUserData(chatId):
    User.get(chatId=chatId).delete()
    Data.get(chatId=chatId).delete()
    Notifs.get(chatId=chatId).delete()


def fetchAndStore(api, chatId):
    data = Data.get(chatId=chatId)
    data.credito = api.credito()
    data.dataRinnovo = api.dataRinnovo().strftime("%d/%m/%Y %H:%M")
    data.costoRinnovo = api.costoRinnovo()
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


def unitToGB(data, decimals=2):
    multipliers = {
        "B":  1024**3,
        "KB": 1024**2,
        "MB": 1024,
        "GB": 1
    }

    value = data["count"]
    unit = data["unit"]
    return round(value/multipliers[unit], decimals)
