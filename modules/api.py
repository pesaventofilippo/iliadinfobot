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
        "nome":          "//*[@id='account-conso']/div[1]/div[1]/div/nav/div/div/div[2]/div[1]/text()[2]",
        "id":            "//*[@id='account-conso']/div[1]/div[1]/div/nav/div/div/div[2]/div[2]/span",
        "numero":        "//*[@id='account-conso']/div[1]/div[1]/div/nav/div/div/div[2]/div[3]/span",
        "credito":       "//*[@id='container']/div/div/div[2]/div/div/div/div/h2/b",
        "rinnovo":       "//*[@id='container']/div/div/div[2]/div[3]/div/div/div/div[2]",
        "rinnovo2":      "//*[@id='container']/div/div/div[2]/div[3]/div/div/div/div[1]",
        "totChiamate":   "//*[@id='container']/div/div/div[2]/div/div/div/div/div[{0}]/div[1]/div[1]/div/div[1]/span[1]",
        "costoChiamate": "//*[@id='container']/div/div/div[2]/div/div/div/div/div[{0}]/div[1]/div[1]/div/div[1]/span[2]",
        "totSms":        "//*[@id='container']/div/div/div[2]/div/div/div/div/div[{0}]/div[1]/div[2]/div/div[1]/span[1]",
        "costoSms":      "//*[@id='container']/div/div/div[2]/div/div/div/div/div[{0}]/div[1]/div[2]/div/div[1]/span[2]",
        "totGiga":       "//*[@id='container']/div/div/div[2]/div/div/div/div/div[{0}]/div[2]/div[1]/div/div[1]/span[1]",
        "costoGiga":     "//*[@id='container']/div/div/div[2]/div/div/div/div/div[{0}]/div[2]/div[1]/div/div[1]/span[2]",
        "pianoGiga":     "//*[@id='container']/div/div/div[2]/div/div/div/div/div[{0}]/div[2]/div[1]/div/div[1]/text()[2]",
        "totMms":        "//*[@id='container']/div/div/div[2]/div/div/div/div/div[{0}]/div[2]/div[2]/div/div[1]/span[1]",
        "costoMms":      "//*[@id='container']/div/div/div[2]/div/div/div/div/div[{0}]/div[2]/div[2]/div/div[1]/span[2]",
        "costoRinnovo":  "//*[@id='container']/div/div/div[2]/div/div/div/div/div[1]/div/div[1]/span[1]"
    }

    def __init__(self, username: str, password: str):
        self._username = username
        self._password = password
        self._pages = None

    def _getXPath(self, name: str, estero: bool=False, page: int=0) -> str:
        intIndex = 3 if estero else 2
        xpath = self._xpaths[name].format(intIndex)
        if "text()" not in xpath:
            xpath += "/text()"
        return str(self._pages[page].xpath(xpath)[0]).strip(" \n")

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
        try:
            el = self._getXPath("rinnovo")
            return datetime.strptime(el[-20:], "%H:%M del %d/%m/%Y")
        except Exception:
            el = self._getXPath("rinnovo2")
            return datetime.strptime(el[-20:], "%H:%M del %d/%m/%Y")

    def totChiamate(self, estero: bool=False) -> str:
        el = self._getXPath("totChiamate", estero)
        return el.lower()

    def costoChiamate(self, estero: bool=False) -> float:
        el = self._getXPath("costoChiamate", estero)
        return float(el.replace("€", ""))

    def totSms(self, estero: bool=False) -> int:
        el = self._getXPath("totSms", estero)
        return int(el.replace(" SMS", ""))

    def costoSms(self, estero: bool=False) -> float:
        el = self._getXPath("costoSms", estero)
        return float(el.replace("€", ""))

    def totGiga(self, estero: bool=False) -> dict:
        el = self._getXPath("totGiga", estero)
        split = re.split('(\d+)', el.upper())[1:]
        return {
            "count": float("".join(split[:-1]).replace(",", ".")),
            "unit":  str(split[-1])
        }

    def costoGiga(self, estero: bool=False) -> float:
        el = self._getXPath("costoGiga", estero)
        return float(el.replace("€", ""))

    def pianoGiga(self, estero: bool=False) -> dict:
        el = self._getXPath("pianoGiga", estero)
        split = re.split('(\d+)', el.upper())[1:]
        return {
            "count": float("".join(split[:-1]).replace(",", ".")),
            "unit": str(split[-1])
        }

    def totMms(self, estero: bool=False) -> int:
        el = self._getXPath("totMms", estero)
        return int(el.replace(" MMS", ""))

    def costoMms(self, estero: bool=False) -> float:
        el = self._getXPath("costoMms", estero)
        return float(el.replace("€", ""))

    def costoRinnovo(self) -> float:
        el = self._getXPath("costoRinnovo", page=1)
        raw = re.findall(r'\d+.\d+', el)
        return float(raw[0])
