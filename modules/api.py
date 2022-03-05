from requests import session as reqSession
from datetime import datetime
from lxml import html
import re


class AuthenticationFailedError(Exception):
    def __init__(self):
        self.message = "Invalid username or password"


class IliadApi:
    loginUrl = "https://www.iliad.it/account/"
    offertaUrl = "https://www.iliad.it/account/gestisci-lofferta"
    _xpaths = {
        "nome":          "//body[contains(@id, 'account-conso')]/descendant::div[@class='current-user__infos']/div[1]/text()[2]",
        "id":            "//body[contains(@id, 'account-conso')]/descendant::div[@class='current-user__infos']/div[2]/span",
        "numero":        "//body[contains(@id, 'account-conso')]/descendant::div[@class='current-user__infos']/div[3]/span",
        "credito":       "//div[@class='toggle-conso']/preceding-sibling::b",
        "rinnovo":       "//div[@class='end_offerta']",
        "totChiamate":   "//div[contains(@class, 'conso-infos')][contains(@class, 'conso-{0}')]/descendant::div[@class='conso__text']/span[1]", # 1° elemento nell'array
        "costoChiamate": "//div[contains(@class, 'conso-infos')][contains(@class, 'conso-{0}')]/descendant::div[@class='conso__text']/span[2]", # 1° elemento nell'array
        "totSms":        "//div[contains(@class, 'conso-infos')][contains(@class, 'conso-{0}')]/descendant::div[@class='conso__text']/span[1]", # 2° elemento nell'array
        "costoSms":      "//div[contains(@class, 'conso-infos')][contains(@class, 'conso-{0}')]/descendant::div[@class='conso__text']/span[2]", # 2° elemento nell'array
        "totGiga":       "//div[contains(@class, 'conso-infos')][contains(@class, 'conso-{0}')]/descendant::div[@class='conso__text']/span[1]", # 3° elemento nell'array
        "costoGiga":     "//div[contains(@class, 'conso-infos')][contains(@class, 'conso-{0}')]/descendant::div[@class='conso__text']/span[2]", # 3° elemento nell'array
        "pianoGiga":     "//div[contains(@class, 'conso-infos')][contains(@class, 'conso-local')]/descendant::div[@class='conso__text']/text()[2]", # 3° elemento nell'array
        "totMms":        "//div[contains(@class, 'conso-infos')][contains(@class, 'conso-{0}')]/descendant::div[@class='conso__text']/span[1]", # 4° elemento nell'array
        "costoMms":      "//div[contains(@class, 'conso-infos')][contains(@class, 'conso-{0}')]/descendant::div[@class='conso__text']/span[2]", # 4° elemento nell'array
        "costoRinnovo":  "//*[@id='container']/div/div/div[2]/div/div/div/div/div[1]/div/div[1]/span[1]" # questo io non ce l'ho proprio nella pagina iliad
    }

    def __init__(self, username: str, password: str):
        self._username = username
        self._password = password
        self._pages = None

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

        with reqSession() as httpSession:
            httpSession.get(self.loginUrl)
            resp = httpSession.post(self.loginUrl, loginInfo)
            infoPage = html.fromstring(resp.content)
            resp = httpSession.get(self.offertaUrl)
            offertaPage = html.fromstring(resp.content)

        # Remove promotional divs
        delDivs = [
            "//div[@class='marketing-consent-banner']",
            "//div[@class='change-offer-banner']",
            "//div[@class='banner-payment-upgrade']"
        ]
        for div in delDivs:
            try:
                div = infoPage.xpath(div)[0]
                div.getparent().remove(div)
            except Exception:
                pass

        self._pages = [infoPage, offertaPage]

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
        #el = self._getXPath("rinnovo")
        #return datetime.strptime(el[-20:], "%H:%M del %d/%m/%Y")
        return datetime(1970,1,1)

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
        split = re.split('(\d+)', el.upper())[1:]
        return {
            "count": float("".join(split[:-1]).replace(",", ".")),
            "unit":  str(split[-1])
        }

    def costoGiga(self, estero: bool=False) -> float:
        el = self._getXPath("costoGiga", estero, array_pos=2)
        return float(el.replace("€", ""))

    def pianoGiga(self, estero: bool=False) -> dict:
        el = self._getXPath("pianoGiga", estero, array_pos=2)
        split = re.split('(\d+)', el.upper())[1:]
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
        raw = re.findall(r'\d+.\d+', el)
        return float(raw[0])
