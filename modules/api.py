from requests import session as reqSession
from lxml import html
import re


class AuthenticationFailedError(Exception):
    def __init__(self):
        self.message = "Invalid username or password"


class IliadApi:
    loginUrl = "https://www.iliad.it/account/"

    def xpaths(self, name: str, estero: bool=False):
        paths = {
            "_base":  "//*[@id='page-container']/div/",
            "notext": ["gigaTot"],

            "special": {
                "loginError": "//div[@class='flash flash-error']"
            },

            "basic": {
                "_base":   "",
                "credito": "div[2]/div[2]/div[9]/div[2]",
                "rinnovo": "div[2]/div[2]/div[4]",
                "nome":    "nav/div/div/div[2]/div[1]",
                "id":      "nav/div/div/div[2]/div[2]",
                "numero":  "nav/div/div/div[2]/div[3]"
            },

            "info": {
                "_base":      "div[2]/div[2]/",
                "_intSuffix": "div[5]/",
                "_extSuffix": "div[6]/",

                "chiamateCount": "div[1]/div[1]/div/div[1]/span[1]",
                "chiamateCosto": "div[1]/div[1]/div/div[1]/span[2]",
                "smsCount":      "div[1]/div[2]/div/div[1]/span[1]",
                "smsCosto":      "div[1]/div[2]/div/div[1]/span[2]",
                "gigaCount":     "div[2]/div[1]/div/div[1]/span[1]",
                "gigaTot":       "div[2]/div[1]/div/div[1]/text()[1]",
                "gigaCosto":     "div[2]/div[1]/div/div[1]/span[2]",
                "mmsCount":      "div[2]/div[2]/div/div[1]/span[1]",
                "mmsCosto":      "div[2]/div[2]/div/div[1]/span[2]"
            }
        }

        if name in paths["special"].keys():
            selected = paths["special"][name]

        else:
            cat = "info" if name in paths["info"].keys() else "basic"
            selected = paths["_base"] + paths[cat]["_base"]
            if cat == "info":
                suffix = "_intSuffix" if not estero else "_extSuffix"
                selected += paths["info"][suffix]
            selected += paths[cat][name]

        if name not in paths["notext"]:
            selected += "/text()"

        return selected


    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.page = None


    def load(self):
        loginInfo = {
            "login-ident": self.username,
            "login-pwd": self.password
        }

        with reqSession() as sess:
            sess.get(self.loginUrl)
            resp = sess.post(self.loginUrl, loginInfo)
        tree = html.fromstring(resp.content)

        error = tree.xpath(self.xpaths("loginError"))
        if error:
            raise AuthenticationFailedError

        self.page = tree


    # float: euros
    def credito(self):
        return float(self.page.xpath(self.xpaths("credito"))[0].replace("€", ""))


    # datetime: contract renewal
    def dataRinnovo(self):
        from datetime import datetime
        raw = self.page.xpath(self.xpaths("rinnovo"))[0]\
            .replace("\n         La tua offerta iliad si rinnoverà alle ", "")\
            .replace("\n      ", "")
        return datetime.strptime(raw, "%H:%M del %d/%m/%Y")


    # string: holder name
    def nome(self):
        return self.page.xpath(self.xpaths("nome"))[0]


    # int: account id
    def id(self):
        return int(self.page.xpath(self.xpaths("id"))[0].replace("ID utente: ", ""))


    # string: phone number (with spaces and no country code)
    def numero(self):
        return self.page.xpath(self.xpaths("numero"))[0].replace("Numero: ", "")


    # string: duration
    def totChiamate(self, estero: bool=False):
        return self.page.xpath(self.xpaths("chiamateCount", estero))[0].lower()


    # float: euros
    def costoChiamate(self, estero: bool=False):
        return float(self.page.xpath(self.xpaths("chiamateCosto", estero))[0].replace("€", ""))


    # int: sms count
    def totSms(self, estero: bool=False):
        return int(self.page.xpath(self.xpaths("smsCount", estero))[0].replace(" SMS", ""))


    # float: euros
    def costoSms(self, estero: bool=False):
        return float(self.page.xpath(self.xpaths("smsCosto", estero))[0].replace("€", ""))


    # dict: count(float) and unit(str)
    def totGiga(self, estero: bool=False):
        raw = self.page.xpath(self.xpaths("gigaCount", estero))[0].upper()
        split = re.split('(\d+)', raw)
        return {
            "count": float("".join(split[:-1]).replace(",", ".")),
            "unit":  str(split[-1])
        }


    # float: euros
    def costoGiga(self, estero: bool=False):
        return float(self.page.xpath(self.xpaths("gigaCosto", estero))[0].replace("€", ""))


    # dict: count(int) and unit(str)
    def pianoGiga(self, estero: bool=False):
        raw = self.page.xpath(self.xpaths("gigaTot", estero))[0].replace(" / ", "").upper()
        split = re.split('(\d+)', raw)
        return {
            "count": float("".join(split[:-1]).replace(",", ".")),
            "unit": str(split[-1])
        }


    # int: count
    def totMms(self, estero: bool=False):
        return int(self.page.xpath(self.xpaths("mmsCount", estero))[0].replace(" MMS", ""))


    # float: euros
    def costoMms(self, estero: bool=False):
        return float(self.page.xpath(self.xpaths("mmsCosto", estero))[0].replace("€", ""))
