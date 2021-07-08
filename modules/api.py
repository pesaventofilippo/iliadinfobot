from requests import session as reqSession
from lxml import html


class AuthenticationFailedError(Exception):
    def __init__(self):
        self.message = "Invalid username or password"


class IliadApi:
    loginUrl = "https://www.iliad.it/account/"

    xpaths = {
        "loginError":    "//div[@class='flash flash-error']/text()",
        "credito":       "//*[@id='page-container']/div/div[2]/div[2]/h2/b",
        "rinnovo":       "//*[@id='page-container']/div/div[2]/div[2]/div[3]",
        "nome":          "//*[@id='page-container']/div/nav/div/div/div[2]/div[1]",
        "id":            "//*[@id='page-container']/div/nav/div/div/div[2]/div[2]",
        "numero":        "//*[@id='page-container']/div/nav/div/div/div[2]/div[3])",

        "chiamateCount": "//*[@id='page-container']/div/div[2]/div[2]/div[4]/div[1]/div[1]/div/div[1]/span[1]/text()",
        "chiamateCosto": "//*[@id='page-container']/div/div[2]/div[2]/div[4]/div[1]/div[1]/div/div[1]/span[2]/text()",
        "smsCount":      "//*[@id='page-container']/div/div[2]/div[2]/div[4]/div[1]/div[2]/div/div[1]/span[1]/text()",
        "smsCosto":      "//*[@id='page-container']/div/div[2]/div[2]/div[4]/div[1]/div[2]/div/div[1]/span[2]/text()",
        "gigaCount":     "//*[@id='page-container']/div/div[2]/div[2]/div[4]/div[2]/div[1]/div/div[1]/span[1]/text()",
        "gigaTot":       "//*[@id='page-container']/div/div[2]/div[2]/div[4]/div[2]/div[1]/div/div[1]/text()[2]",
        "gigaCosto":     "//*[@id='page-container']/div/div[2]/div[2]/div[4]/div[2]/div[1]/div/div[1]/span[2]/text()",
        "mmsCount":      "//*[@id='page-container']/div/div[2]/div[2]/div[4]/div[2]/div[2]/div/div[1]/span[1]/text()",
        "mmsCosto":      "//*[@id='page-container']/div/div[2]/div[2]/div[4]/div[2]/div[2]/div/div[1]/span[2]/text()",

        "ext-chiamateCount": "//*[@id='page-container']/div/div[2]/div[2]/div[5]/div[1]/div[1]/div/div[1]/span[1]/text()",
        "ext-chiamateCosto": "//*[@id='page-container']/div/div[2]/div[2]/div[5]/div[1]/div[1]/div/div[1]/span[2]/text()",
        "ext-smsCount":      "//*[@id='page-container']/div/div[2]/div[2]/div[5]/div[1]/div[2]/div/div[1]/span[1]/text()",
        "ext-smsCosto":      "//*[@id='page-container']/div/div[2]/div[2]/div[5]/div[1]/div[2]/div/div[1]/span[2]/text()",
        "ext-gigaCount":     "//*[@id='page-container']/div/div[2]/div[2]/div[5]/div[2]/div[1]/div/div[1]/span[1]/text()",
        "ext-gigaTot":       "//*[@id='page-container']/div/div[2]/div[2]/div[5]/div[2]/div[1]/div/div[1]/text()[2]",
        "ext-gigaCosto":     "//*[@id='page-container']/div/div[2]/div[2]/div[5]/div[2]/div[1]/div/div[1]/span[2]/text()",
        "ext-mmsCount":      "//*[@id='page-container']/div/div[2]/div[2]/div[5]/div[2]/div[2]/div/div[1]/span[1]/text()",
        "ext-mmsCosto":      "//*[@id='page-container']/div/div[2]/div[2]/div[5]/div[2]/div[2]/div/div[1]/span[2]/text()"
    }


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

        error = tree.xpath(self.xpaths['loginError'])
        if error:
            raise AuthenticationFailedError

        self.page = tree


    # float: euros
    def credito(self):
        return float(self.page.xpath(self.xpaths['credito'])[0].replace("€", ""))


    # datetime: contract renewal
    def dataRinnovo(self):
        from datetime import datetime
        raw = self.page.xpath(self.xpaths['rinnovo'])[0]\
            .replace("\n         La tua offerta iliad si rinnoverà alle ", "")\
            .replace("\n      ", "")
        return datetime.strptime(raw, "%H:%M del %d/%m/%Y")


    # string: holder name
    def nome(self):
        return self.page.xpath(self.xpaths['nome'])[0]


    # int: account id
    def id(self):
        return int(self.page.xpath(self.xpaths['id'])[0].replace("ID utente: ", ""))


    # string: phone number (with spaces and no country code)
    def numero(self):
        return self.page.xpath(self.xpaths['numero'])[0].replace("Numero: ", "")


    # string: duration
    def totChiamate(self, estero: bool=False):
        xpath = "chiamateCount" if not estero else "ext-chiamateCount"
        raw = self.page.xpath(self.xpaths[xpath])[0].lower()
        return raw


    # float: euros
    def costoChiamate(self, estero: bool=False):
        xpath = "chiamateCosto" if not estero else "ext-chiamateCosto"
        return float(self.page.xpath(self.xpaths[xpath])[0].replace("€", ""))


    # int: sms count
    def totSms(self, estero: bool=False):
        xpath = "smsCount" if not estero else "ext-smsCount"
        return int(self.page.xpath(self.xpaths[xpath])[0].replace(" SMS", ""))


    # float: euros
    def costoSms(self, estero: bool=False):
        xpath = "smsCosto" if not estero else "ext-smsCosto"
        return float(self.page.xpath(self.xpaths[xpath])[0].replace("€", ""))


    # dict: count(float) and unit(str)
    def totGiga(self, estero: bool=False):
        xpath = "gigaCount" if not estero else "ext-gigaCount"
        raw = self.page.xpath(self.xpaths[xpath])[0].upper()
        if raw == "0B":
            count = 0
            unit = "B"
        else:
            unit = raw[-2:]
            count = float(raw.replace(unit, "").replace(",", "."))
        return {"count": count, "unit": unit}


    # float: euros
    def costoGiga(self, estero: bool=False):
        xpath = "gigaCosto" if not estero else "ext-gigaCosto"
        return float(self.page.xpath(self.xpaths[xpath])[0].replace("€", ""))


    # dict: count(int) and unit(str)
    def pianoGiga(self, estero: bool=False):
        xpath = "gigaTot" if not estero else "ext-gigaTot"
        raw = self.page.xpath(self.xpaths[xpath])[0].replace(" / ", "").upper()
        unit = raw[-2:]
        count = int(raw.replace(unit, ""))
        return {"count": count, "unit": unit}


    # int: count
    def totMms(self, estero: bool=False):
        xpath = "mmsCount" if not estero else "ext-mmsCount"
        return int(self.page.xpath(self.xpaths[xpath])[0].replace(" MMS", ""))


    # float: euros
    def costoMms(self, estero: bool=False):
        xpath = "mmsCosto" if not estero else "ext-mmsCosto"
        return float(self.page.xpath(self.xpaths[xpath])[0].replace("€", ""))
