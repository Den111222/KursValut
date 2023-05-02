from api import _Api
from datetime import date

today = date.today()
d1 = today.strftime("%d.%m.%Y")

class Api(_Api):
    def __init__(self):
        super().__init__("PrivatApi")
    def _update_rate(self, xrate):
        rate = self._get_privat_rate(xrate.from_currency)
        return rate

    def _get_privat_rate(self, from_currency):
        response = self._send_request(url=f"https://api.privatbank.ua/p24api/exchange_rates?json&date={d1}",
                                      method="get")
        response_json = response.json()
        self.log.debug("Privat response: %s" % response_json)
        rate = self._find_rate(response_json, from_currency)
        return rate

    def _find_rate(self, response_data, from_currency):
        for e in response_data['exchangeRate']:
            if e['currency'] == "USD":
                return float(e['saleRate'])
        raise ValueError(f"Invalid Privat response: USD not found")

