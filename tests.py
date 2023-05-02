import json
import unittest
from datetime import date
from unittest.mock import patch
import xml.etree.ElementTree as ET
import requests
import xmltodict
import api
import models

def get_privat_response(*args, **kwds):
    print("get_privat_response")

    class Response:
        def __init__(self, response):
            self.text = json.dumps(response)

        def json(self):
            return json.loads(self.text)

    return Response({'exchangeRate': [{"currency": "USD", "baseCurrencyLit": "UAH", "saleRate": "30.0"}]})

class Test(unittest.TestCase):
    #Также создает таблицы в базе данных golden-eye.sqlite
    def setUp(self):
        models.init_db(self._testMethodName)

    # @unittest.skip("skip")      #пропускаем тест
    def test_privat_usd(self):
        xrate = models.XRate.get(from_currency=840, to_currency=980, module='privat_api')
        updated_before = xrate.updated
        self.assertEqual(xrate.rate, 1.0)
        data = {'from_currency': 840, 'to_currency': 980, 'source': 'privat_api'}
        api.update_rate(data)
        xrate = models.XRate.get(from_currency=840, to_currency=980, module='privat_api')
        updated_after = xrate.updated
        self.assertGreater(xrate.rate, 30)
        self.assertGreater(updated_after, updated_before)
        api_log = models.ApiLog.select().order_by(models.ApiLog.created.desc()).first()
        self.assertIsNotNone(api_log)
        d1 = date.today().strftime("%d.%m.%Y")
        self.assertEqual(api_log.request_url, f"https://api.privatbank.ua/p24api/exchange_rates?json&date={d1}")
        self.assertIsNotNone(api_log.response_text)
        self.assertIn('"baseCurrency":980,"baseCurrencyLit":"UAH"', api_log.response_text)

    # @unittest.skip("skip")      #пропускаем тест
    def test_nbu(self):
        xrate = models.XRate.get(from_currency=840, to_currency=643)
        updated_before = xrate.updated
        self.assertEqual(xrate.rate, 1.0)
        data = {'from_currency': 840, 'to_currency': 643, 'source': 'nbu_api'}
        api.update_rate(data)
        xrate = models.XRate.get(from_currency=840, to_currency=643)
        updated_after = xrate.updated
        self.assertGreater(xrate.rate, 50)
        self.assertGreater(updated_after, updated_before)
        api_log = models.ApiLog.select().order_by(models.ApiLog.created.desc()).first()
        self.assertIsNotNone(api_log)
        self.assertEqual(api_log.request_url, "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange")
        self.assertIsNotNone(api_log.response_text)
        self.assertIn("<r030>840</r030>", api_log.response_text)

    #Тест на корректность отработки вызова, результат запроса подменяется в функции get_privat_response.
    # @unittest.skip("skip")      #пропускаем тест
    @patch('api._Api._send', new=get_privat_response)
    def test_privat_mock(self):
        xrate = models.XRate.get(from_currency=840, to_currency=980, module='privat_api')
        updated_before = xrate.updated
        self.assertEqual(xrate.rate, 1.0)
        data = {'from_currency': 840, 'to_currency': 980, 'source': 'privat_api'}
        api.update_rate(data)
        xrate = models.XRate.get(from_currency=840, to_currency=980, module='privat_api')
        updated_after = xrate.updated
        self.assertEqual(xrate.rate, 30)
        self.assertGreater(updated_after, updated_before)
        api_log = models.ApiLog.select().order_by(models.ApiLog.created.desc()).first()
        self.assertIsNotNone(api_log)
        d1 = date.today().strftime("%d.%m.%Y")
        self.assertEqual(api_log.request_url, f"https://api.privatbank.ua/p24api/exchange_rates?json&date={d1}")
        self.assertIsNotNone(api_log.response_text)
        self.assertEqual('{"exchangeRate": [{"currency": "USD", "baseCurrencyLit": "UAH", "saleRate": "30.0"}]}',
                         api_log.response_text)

    # @unittest.skip("skip")      #пропускаем тест
    def test_api_error(self):
        api.HTTP_TIMEOUT = 0.001
        xrate = models.XRate.get(id=1)
        updated_before = xrate.updated
        self.assertEqual(xrate.rate, 1.0)
        data = {'from_currency': 840, 'to_currency': 980, 'source': 'privat_api'}
        self.assertRaises(requests.exceptions.RequestException, api.update_rate, data)
        xrate = models.XRate.get(id=1)
        updated_after = xrate.updated
        self.assertEqual(xrate.rate, 1.0)
        self.assertEqual(updated_after, updated_before)
        api_log = models.ApiLog.select().order_by(models.ApiLog.created.desc()).first()
        self.assertIsNotNone(api_log)
        d1 = date.today().strftime("%d.%m.%Y")
        self.assertEqual(api_log.request_url, f"https://api.privatbank.ua/p24api/exchange_rates?json&date={d1}")
        self.assertIsNone(api_log.response_text)
        self.assertIsNotNone(api_log.error)
        error_log = models.ErrorLog.select().order_by(models.ErrorLog.created.desc()).first()
        self.assertIsNotNone(error_log)
        self.assertEqual(error_log.request_url, f"https://api.privatbank.ua/p24api/exchange_rates?json&date={d1}")
        self.assertIsNotNone(error_log.traceback)
        self.assertEqual(api_log.error, error_log.error)
        self.assertIn("Connection to api.privatbank.ua timed out", error_log.error)
        api.HTTP_TIMEOUT = 15

    # @unittest.skip("skip")      #пропускаем тест
    def test_blockchain_usd(self):
        from_currency = 1000
        to_currency = 840
        module = 'blockchain_api'
        xrate = models.XRate.get(from_currency=from_currency, to_currency=to_currency, module= module)
        updated_before = xrate.updated
        self.assertEqual(xrate.rate, 1.0)
        data = {'from_currency': from_currency, 'to_currency': to_currency, 'source': module}
        api.update_rate(data)
        xrate = models.XRate.get(from_currency=from_currency, to_currency=to_currency, module= module)
        updated_after = xrate.updated
        self.assertGreater(xrate.rate, 20000)
        self.assertGreater(updated_after, updated_before)
        api_log = models.ApiLog.select().order_by(models.ApiLog.created.desc()).first()
        self.assertIsNotNone(api_log)
        self.assertEqual(api_log.request_url, "https://api.blockchain.com/v3/exchange/tickers/BTC-USD")
        self.assertIsNotNone(api_log.response_text)

    # @unittest.skip("skip")      #пропускаем тест
    def test_xml_api(self):
        r = requests.get("http://localhost:5000/api/xrates/xml")
        self.assertIn("<xrates>", r.text)
        xml_rates = xmltodict.parse(r.text)
        self.assertIn("xrates", xml_rates)
        self.assertIsInstance(xml_rates["xrates"]["xrate"], list)
        self.assertEqual(len(xml_rates["xrates"]["xrate"]), 4)

    # @unittest.skip("skip")      #пропускаем тест
    def test_json_api(self):
        r = requests.get("http://localhost:5000/api/xrates/json")
        json_rates = r.json()
        self.assertIsInstance(json_rates, list)
        self.assertEqual(len(json_rates), 4)
        for rate in json_rates:
            self.assertIn("from", rate)
            self.assertIn("to", rate)
            self.assertIn("rate", rate)
            self.assertIn("source", rate)

    # @unittest.skip("skip")      #пропускаем тест
    def test_json_api_uah(self):
        r = requests.get("http://localhost:5000/api/xrates/json?to_currency=980")
        json_rates = r.json()
        self.assertIsInstance(json_rates, list)
        self.assertEqual(len(json_rates), 2)

    def test_html_xrates(self):
        r = requests.get("http://localhost:5000/xrates")
        self.assertTrue(r.ok)
        self.assertIn('<table border="1">', r.text)
        root = ET.fromstring(r.text)
        body = root.find("body")
        self.assertIsNotNone(body)
        table = body.find("table")
        self.assertIsNotNone(table)
        rows = table.findall("tr")
        self.assertEqual(len(rows), 4)

if __name__ == '__main__':
    models.init_db()
    unittest.main()
