import re
from lxml import html
from datetime import datetime
from requests import Session

class AuthenticationFailedError(Exception):
    def __init__(self):
        self.message = "Invalid username or password"


class IliadApi:
    loginUrl = "https://www.iliad.it/account/"
    offertaUrl = "https://www.iliad.it/account/le-condizioni-della-mia-offerta"
    _xpaths = {
        "loginError":    "//div[@class='flash flash-error']",
        "nome":          "//body[contains(@id, 'account-conso')]/descendant::div[@class='current-user__infos']/div[1]/text()[2]",
        "id":            "//body[contains(@id, 'account-conso')]/descendant::div[@class='current-user__infos']/div[2]/span",
        "numero":        "//body[contains(@id, 'account-conso')]/descendant::div[@class='current-user__infos']/div[3]/span",
        "credito":       "//div[@class='toggle-conso']/preceding-sibling::b",
        "rinnovo":       "//div[@class='end_offerta']",
        "totChiamate":   "//div[contains(@class, 'conso-infos')][contains(@class, 'conso-{0}')]/descendant::div[@class='conso__text']/span[1]",
        "costoChiamate": "//div[contains(@class, 'conso-infos')][contains(@class, 'conso-{0}')]/descendant::div[@class='conso__text']/span[2]",
        "totSms":        "//div[contains(@class, 'conso-infos')][contains(@class, 'conso-{0}')]/descendant::div[@class='conso__text']/span[1]",
        "costoSms":      "//div[contains(@class, 'conso-infos')][contains(@class, 'conso-{0}')]/descendant::div[@class='conso__text']/span[2]",
        "totGiga":       "//div[contains(@class, 'conso-infos')][contains(@class, 'conso-{0}')]/descendant::div[@class='conso__text']/span[1]",
        "costoGiga":     "//div[contains(@class, 'conso-infos')][contains(@class, 'conso-{0}')]/descendant::div[@class='conso__text']/span[2]",
        "pianoGiga":     "//div[contains(@class, 'conso-infos')][contains(@class, 'conso-{0}')]/descendant::div[@class='conso__text']/text()[2]",
        "totMms":        "//div[contains(@class, 'conso-infos')][contains(@class, 'conso-{0}')]/descendant::div[@class='conso__text']/span[1]",
        "costoMms":      "//div[contains(@class, 'conso-infos')][contains(@class, 'conso-{0}')]/descendant::div[@class='conso__text']/span[2]",
        "costoRinnovo":  "//*[@id='container']/descendant::div[contains(@class, 'rectangle-content')]/descendant::div[contains(@class,'title')]/span[1]"
    }

    def __init__(self, username: str, password: str):
        self._username = username
        self._password = password
        self._pages = []

    def _getXPath(self, name: str, estero: bool=False, page: int=0, array_pos: int=0) -> str:
        localOrRoaming = "roaming" if estero else "local"
        xpath = self._xpaths[name].format(localOrRoaming)
        if "text()" not in xpath:
            xpath += "/text()"
        return str(self._pages[page].xpath(xpath)[array_pos]).strip(" \n")

    def load(self):
        loginInfo = {
            "login-ident": self._username,
            "login-pwd": self._password
        }

        with Session() as httpSession:
            httpSession.get(self.loginUrl)
            resp = httpSession.post(self.loginUrl, loginInfo)
            infoPage = html.fromstring(resp.content)

            if infoPage.xpath(self._xpaths["loginError"]):
                raise AuthenticationFailedError
            if "ID utente o password non corretto" in infoPage.text_content():
                raise AuthenticationFailedError

            resp = httpSession.get(self.offertaUrl)
            offerPage = html.fromstring(resp.content)

        self._pages = [infoPage, offerPage]

    def nome(self) -> str:
        el = self._getXPath("nome")
        return el

    def id(self) -> int:
        el = self._getXPath("id")
        return int(el)

    def numero(self) -> str:
        el = self._getXPath("numero")
        return el.replace(" ", "")

    def credito(self) -> float:
        el = self._getXPath("credito")
        return float(el.replace("€", ""))

    def dataRinnovo(self) -> datetime:
        el = self._getXPath("rinnovo")
        return datetime.strptime(el[-20:], "%H:%M del %d/%m/%Y")

    def totChiamate(self, estero: bool=False) -> str:
        el = self._getXPath("totChiamate", estero)
        return el.lower()

    def costoChiamate(self, estero: bool=False) -> float:
        el = self._getXPath("costoChiamate", estero)
        return float(el.replace("€", ""))

    def totSms(self, estero: bool=False) -> int:
        el = self._getXPath("totSms", estero, array_pos=1)
        return int(el.replace(" SMS", ""))

    def costoSms(self, estero: bool=False) -> float:
        el = self._getXPath("costoSms", estero, array_pos=1)
        return float(el.replace("€", ""))

    def totGiga(self, estero: bool=False) -> dict:
        el = self._getXPath("totGiga", estero, array_pos=2)
        split = re.split(r'(\d+)', el.upper())[1:]
        return {
            "count": float("".join(split[:-1]).replace(",", ".")),
            "unit":  str(split[-1])
        }

    def costoGiga(self, estero: bool=False) -> float:
        el = self._getXPath("costoGiga", estero, array_pos=2)
        return float(el.replace("€", ""))

    def pianoGiga(self, estero: bool=False) -> dict:
        el = self._getXPath("pianoGiga", estero, array_pos=2)
        split = re.split(r'(\d+)', el.upper())[1:]
        return {
            "count": float("".join(split[:-1]).replace(",", ".")),
            "unit": str(split[-1])
        }

    def totMms(self, estero: bool=False) -> int:
        el = self._getXPath("totMms", estero, array_pos=3)
        return int(el.replace(" MMS", ""))

    def costoMms(self, estero: bool=False) -> float:
        el = self._getXPath("costoMms", estero, array_pos=3)
        return float(el.replace("€", ""))

    def costoRinnovo(self) -> float:
        el = self._getXPath("costoRinnovo", page=1)
        return float(el.split(" ")[-1].replace("€", ""))


if __name__ == '__main__':
    print("## API DEBUG MODE ##")
    user = input("ID Iliad: ")
    passw = input("Password: ")
    api = IliadApi(user, passw)
    api.load()

    toTest_Singolo = [
        api.nome, api.id, api.numero,
        api.credito, api.dataRinnovo, api.costoRinnovo
    ]
    toTest_Roaming = [
        api.totChiamate, api.costoChiamate,
        api.totSms, api.costoSms,
        api.totMms, api.costoMms,
        api.totGiga, api.pianoGiga, api.costoGiga
    ]

    print("############# DATI #############")
    for f in toTest_Singolo:
        print(f"api.{f.__name__}: {repr(f())}")
    print("############ ITALIA ############")
    for f in toTest_Roaming:
        print(f"api.{f.__name__}: {repr(f())}")
    print("############ ESTERO ############")
    for f in toTest_Roaming:
        print(f"api.{f.__name__}: {repr(f(estero=True))}")
