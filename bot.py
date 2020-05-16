from time import sleep
from telepot import Bot, glance
from threading import Thread
from pony.orm import db_session, select, commit
from telepot.exception import TelegramError, BotWasBlockedError

from modules import helpers, keyboards
from modules.api import AuthenticationFailedError, IliadApi
from modules.crypter import crypt_password, decrypt_password
from modules.database import User, Data

try:
    f = open('token.txt', 'r')
    token = f.readline().strip()
    f.close()
except FileNotFoundError:
    token = input(" * Incolla qui il token di BotFather: ")
    f = open('token.txt', 'w')
    f.write(token)
    f.close()

bot = Bot(token)


@db_session
def reply(msg):
    chatId = msg['chat']['id']
    name = msg['from']['first_name']
    if "text" in msg:
        text = msg['text']
    else:
        bot.sendMessage(chatId, "🤨 Formato file non supportato. /help")
        return

    if not User.exists(lambda u: u.chatId == chatId):
        User(chatId=chatId)
    if not Data.exists(lambda d: d.chatId == chatId):
        Data(chatId=chatId)

    user = User.get(chatId=chatId)
    data = Data.get(chatId=chatId)

    if text == "/about":
        bot.sendMessage(chatId, "ℹ️ <b>Informazioni sul bot</b>\n"
                                "IliadInfoBot è un bot creato e sviluppato da Filippo Pesavento, che ti permette "
                                "di visualizzare tutte le info sul tuo account Iliad in mancanza dell'app.\n"
                                "Prova ad usarlo per scoprire quanto è comodo!\n\n"
                                "<b>Sviluppo:</b> Filippo Pesavento\n"
                                "<b>Hosting:</b> Filippo Pesavento\n"
                                "<b>Info sicurezza:</b> /aboutprivacy\n\n"
                                "<i>IliadInfoBot non è in alcun modo affiliato con Iliad Italia S.p.A ed è una creazione "
                                "esclusiva di Filippo Pesavento.</i>", parse_mode="HTML")

    elif text == "/aboutprivacy":
        bot.sendMessage(chatId, "ℹ️ <b>Informazioni sulla privacy</b>\n"
                                "La mia password è al sicuro? 🤔\n\n"
                                "🔐 <b>Sì: la tua password viene criptata.</b>\n"
                                "Il bot conserva la tua password in maniera sicura, salvandola in un formato non leggibile da "
                                "persone estranee. Sei al sicuro: i tuoi dati non verranno visti nè rubati da nessuno!\n\n"
                                "🔐 <b>Spiegazione dettagliata:</b>\n"
                                "Tecnicamente potrei decriptare a mano le password e vederle, ma sostanzialmente è complicato, "
                                "perchè il bot genera una chiave per l'algoritmo (visto che il cripting deve essere reversibile, "
                                "per poter mandare le notifiche automatiche) prendendo come dati una chiave comune (che salvo nella RAM "
                                "e inserisco ad ogni avvio, per evitare che qualcuno che non sia io possa leggere il database e i dati degli utenti) "
                                "e anche l'username dell'utente. Quindi ogni utente ha la propria password criptata con una chiave diversa da tutti "
                                "gli altri, e sarebbe difficile anche per me risalire alla password, dovendo sapere di chi è l'username collegato a "
                                "quella password specifica.\n"
                                "Questo non vuol dire che non possa farlo: con un po' di lavoro ci riuscirei. Quindi alla fine devi decidere tu: "
                                "io ti posso assicurare che non leggerò mai nè proverò mai a decriptare le password, sia per un discorso di etica "
                                "che per scelta personale, ma non sono tuo amico nè tuo conoscente: quindi se decidi di non fidarti di uno sconosciuto "
                                "che ti scrive su Telegram (ti posso capire benissimo) sei libero di non usare il bot 🙂\n\n"
                                "<a href=\"https://t.me/pesaventofilippo\">Contattami</a>\n\n"
                                "<i>Se sei venuto qui prima di digitare la password per il login, scrivila adesso!</i>",
                        parse_mode="HTML", disable_web_page_preview=True)


    elif user.status != "normal":
        if text == "/annulla":
            user.status = "normal"
            bot.sendMessage(chatId, "Comando annullato!")

        elif user.status == "login_0":
            if len(text) != 8 or not text.isdigit():
                bot.sendMessage(chatId, "⚠️ Errore: l'username deve essere un numero 8 cifre. Riprova!")
                return
            user.username = text
            user.status = "login_1"
            bot.sendMessage(chatId, "👍 Ottimo. Adesso inviami la password.\n"
                                    "Ricorda che la password viene salvata solo per te e viene criptata, nessuno potrà leggerla.\n\n"
                                    "Sei preoccupato per la sicurezza della password? /aboutprivacy")

        elif user.status == "login_1":
            user.password = crypt_password(text, chatId)
            user.status = "normal"
            commit()
            api = IliadApi(user.username, decrypt_password(chatId))

            try:
                api.load()
            except AuthenticationFailedError:
                helpers.clearUserData(chatId)
                try:
                    bot.sendMessage(chatId, "😯 Le tue credenziali di accesso sono errate.\n"
                                            "Controlla i dati inseriti e rieffettua il /login.")
                except (TelegramError, BotWasBlockedError):
                    pass
                return

            bot.sendMessage(chatId, "Fatto 😊\n"
                                    "Premi /help per vedere la lista dei comandi disponibili.\n\n"
                                    "<i>Se vuoi, puoi eliminare il messaggio che mi hai mandato contenente la password: "
                                    "non mi serve più!</i>", parse_mode="HTML")

        elif user.status == "calling_support":
            user.status = "normal"
            for a in helpers.isAdmin():
                bot.sendMessage(a, "🆘 <b>Richiesta di aiuto</b>\n"
                                   "Da: <a href=\"tg://user?id={0}\">{1}</a>\n\n"
                                   "<i>Rispondi al messaggio per parlare con l'utente.</i>".format(chatId, name),
                                parse_mode="HTML")
                if "reply_to_message" in msg:
                    bot.forwardMessage(a, chatId, msg["reply_to_message"]["message_id"])
                bot.forwardMessage(a, chatId, msg['message_id'], disable_notification=True)
            bot.sendMessage(chatId, "<i>Richiesta inviata.</i>\n"
                                    "Un admin ti risponderà il prima possibile.", parse_mode="HTML")


    elif text == "/help":
        bot.sendMessage(chatId, "Ciao, sono il bot di <b>Iliad</b>! 👋🏻\n"
                                "Posso aiutarti a <b>controllare</b> il tuo piano dati e posso mandarti <b>notifiche</b> (in futuro).\n\n"
                                "<b>Lista dei comandi</b>:\n"
                                "- /login - Effettua il login\n"
                                "- /logout - Disconnettiti\n"
                                "- /about - Informazioni sul bot\n"
                                "- /aboutprivacy - Più informazioni sulla privacy\n"
                                "- /support - Contatta lo staff (emergenze)\n\n"
                                "<i>IliadInfoBot non è in alcun modo affiliato con Iliad Italia S.p.A ed è una creazione "
                                "esclusiva di Filippo Pesavento.</i>", parse_mode="HTML")

    elif text == "/users" and helpers.isAdmin(chatId):
        totalUsers = len(select(u for u in User)[:])
        loggedUsers = len(select(u for u in User if u.password != "")[:])
        bot.sendMessage(chatId, "👤 Utenti totali: <b>{}</b>\n"
                                "👤 Utenti loggati: <b>{}</b>".format(totalUsers, loggedUsers), parse_mode="HTML")

    elif text.startswith("/broadcast ") and helpers.isAdmin(chatId):
        bdText = text.split(" ", 1)[1]
        pendingUsers = select(u.chatId for u in User)[:]
        userCount = len(pendingUsers)
        for u in pendingUsers:
            try:
                bot.sendMessage(u, bdText, parse_mode="HTML", disable_web_page_preview=True)
            except (TelegramError, BotWasBlockedError):
                userCount -= 1
        bot.sendMessage(chatId, "📢 Messaggio inviato correttamente a {0} utenti!".format(userCount))

    elif text.startswith("/sendmsg ") and helpers.isAdmin(chatId):
        selId = int(text.split(" ", 2)[1])
        selText = str(text.split(" ", 2)[2])
        bot.sendMessage(selId, selText, parse_mode="HTML")
        bot.sendMessage(chatId, selText + "\n\n- Messaggio inviato!", parse_mode="HTML")

    elif "reply_to_message" in msg:
        if helpers.isAdmin(chatId):
            try:
                userId = msg['reply_to_message']['forward_from']['id']
                bot.sendMessage(userId, "💬 <b>Risposta dello staff</b>\n"
                                        "{0}".format(text), parse_mode="HTML")
                bot.sendMessage(chatId, "Risposta inviata!")
            except Exception:
                bot.sendMessage(chatId, "Errore nell'invio.")
        else:
            bot.sendMessage(chatId, "Scrivi /support per parlare con lo staff.")

    elif text == "/annulla":
        bot.sendMessage(chatId, "😴 Nessun comando da annullare!")


    elif helpers.hasStoredCredentials(chatId):
        if text == "/start":
            bot.sendMessage(chatId, "Bentornato, <b>{0}</b>!\n"
                                    "Cosa posso fare per te? 😊".format(name), parse_mode="HTML")

        elif text == "/login":
            bot.sendMessage(chatId, "Sei già loggato.\n"
                                    "Premi /logout per uscire.")

        elif text == "/logout":
            sent = bot.sendMessage(chatId, "Tutti i tuoi dati relativi all'account e le credenziali verranno eliminate dal bot.\n"
                                            "Sei <b>veramente sicuro</b> di voler uscire?", parse_mode="HTML")
            bot.editMessageReplyMarkup((chatId, sent['message_id']), keyboards.logout(sent['message_id']))

        elif text == "/test":
            api = IliadApi(user.username, decrypt_password(chatId))
            api.load()
            bot.sendMessage(chatId, f"Credito: {api.credito()}\n"
                                    f"Nome: {api.nome()}\n"
                                    f"Numero: {api.numero()}\n"
                                    f"ID: {api.id()}\n"
                                    f"Rinnovo: {api.dataRinnovo()}\n")


        elif text == "/support":
            user.status = "calling_support"
            bot.sendMessage(chatId, "🆘 <b>Richiesta di supporto</b>\n"
                                    "Se hai qualche problema che non riesci a risolvere, scrivi qui un messaggio, e un admin "
                                    "ti contatterà il prima possibile.\n\n"
                                    "<i>Per annullare, premi</i> /annulla.", parse_mode="HTML")

        else:
            bot.sendMessage(chatId, "Non ho capito...\n"
                                    "Serve aiuto? Premi /help")

    else:
        if text == "/login":
            user.status = "login_0"
            bot.sendMessage(chatId, "Per favore, inviami il tuo <b>username</b> (il codice da 8 cifre che usi per accedere "
                                    "all'Area Personale).\n"
                                    "Usa /annulla se serve.", parse_mode="HTML")
        else:
            bot.sendMessage(chatId, "Benvenuto, <b>{0}</b>!\n"
                                    "Per favore, premi /login per utilizzarmi.\n\n"
                                    "Premi /help se serve aiuto.".format(name), parse_mode="HTML")


def button_press(msg):
    chatId, query_data = glance(msg, flavor="callback_query")[1:3]
    query_split = query_data.split("#")
    message_id = int(query_split[1])
    button = query_split[0]

    if button == "logout_yes":
        helpers.clearUserData(chatId)
        bot.editMessageText((chatId, message_id), "😯 Fatto, sei stato disconnesso!\n"
                                                  "Premi /login per entrare di nuovo.\n\n"
                                                  "Premi /help se serve aiuto.", reply_markup=None)

    elif button == "logout_no":
        bot.editMessageText((chatId, message_id), "<i>Logout annullato.</i>", parse_mode="HTML", reply_markup=None)


def accept_message(msg):
    Thread(target=reply, args=[msg]).start()

def accept_button(msg):
    Thread(target=button_press, args=[msg]).start()

bot.message_loop({'chat': accept_message, 'callback_query': accept_button})

while True:
    sleep(60)
