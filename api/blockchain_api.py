import json

from api import _Api


class Api(_Api):
    def __init__(self):
        super().__init__("BlockchainApi")

    def _update_rate(self, xrate):
        rate = self._get_api_rate(xrate.from_currency, xrate.to_currency)
        return rate

    def _get_api_rate(self, from_currency, to_currency):
        aliases_map = {1000: "BTC", 840: "USD"}
        if from_currency not in aliases_map:
            raise ValueError(f"Invalid from_currency: {from_currency}")
        if to_currency not in aliases_map:
            raise ValueError(f"Invalid to_currency: {to_currency}")
        url_end = f"{aliases_map[from_currency]}-{aliases_map[to_currency]}"
        url = f"https://api.blockchain.com/v3/exchange/tickers/{url_end}"
        response = self._send_request(url=url, method="get")
        response_json = json.loads(response.text)
        self.log.debug("Blockchain response: %s" % response_json)
        rate = self._find_rate(response_json)
        return rate


    def _find_rate(self, response_data):
        if "symbol" not in response_data:
            raise ValueError(f"Invalid cryptonator response: ticker not set")
        if "price_24h" not in response_data:
            raise ValueError(f"Invalid cryptonator response: ticker.price not set")
        return float(response_data["price_24h"])
