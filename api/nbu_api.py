import xml.etree.ElementTree as ET
from api import _Api


class Api(_Api):
    def __init__(self):
        super().__init__("NBUApi")

    def _update_rate(self, xrate):
        rate = self._get_nbu_rate(xrate)
        return rate

    def _get_nbu_rate(self, xrate):
        response = self._send_request(url="https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange", method="get")
        self.log.debug("response.encoding: %s" % response.encoding)
        response_text = response.text
        self.log.debug("response.text: %s" % response_text)
        rate = self._find_rate(response_text, xrate)
        return rate

    def _find_rate(self, response_text, xrate):
        root = ET.fromstring(response_text)
        valutes = root.findall('currency')
        nbu_valute_map = {840: "USD", 643: "RUB", 980: "UAH"}
        currency_nbu_alias = nbu_valute_map[xrate.from_currency]
        second_currency_nbu_alias = nbu_valute_map[xrate.to_currency]
        if second_currency_nbu_alias != 'UAH':
            for valute in valutes:
                if valute.find('cc').text == second_currency_nbu_alias:
                    second_rate = float(valute.find("rate").text.replace(",", "."))
                elif valute.find('cc').text == currency_nbu_alias:
                    first_rate = float(valute.find("rate").text.replace(",", "."))
            new_rate = first_rate / second_rate
            return round(new_rate, 4)
        else:
            for valute in valutes:
                if valute.find('cc').text == currency_nbu_alias:
                    return float(valute.find("rate").text.replace(",", "."))
        raise ValueError("Invalid NBU response: USD not found" % xrate.from_currency)
