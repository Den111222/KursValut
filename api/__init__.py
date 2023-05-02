import importlib
import traceback
import requests
from models import XRate, peewee_datetime, ApiLog, ErrorLog
from logging.config import dictConfig
from config import logging, LOGGING, HTTP_TIMEOUT

dictConfig(LOGGING)


def update_rate(data):
    xrate = XRate.select().where(XRate.from_currency == data['from_currency'],
                                 XRate.to_currency == data['to_currency'], XRate.module == data['source']).first()
    module = importlib.import_module(f"api.{xrate.module}")
    module.Api().update_rate(xrate)

class _Api:
    def __init__(self, logger_name):
        self.log = logging.getLogger("Api")
        self.log.name = logger_name
    def update_rate(self, xrate):
        self.log.info("Started update for: %s" % xrate)
        self.log.debug("rate before: %s", xrate)
        xrate.rate = self._update_rate(xrate)
        xrate.updated = peewee_datetime.datetime.now()
        xrate.save()
        self.log.debug("rate after: %s", xrate)
        self.log.info("Finished update for: %s" % xrate)

    def _update_rate(self, xrate):
        raise NotImplementedError("_update_rate")

    def _send_request(self, url, method, data=None, headers=None):
        log = ApiLog(request_url=url, request_data=data, request_method=method,
                     request_headers=headers)
        try:
            response = self._send(method=method, url=url, headers=headers, data=data)
            log.response_text = response.text
            return response
        except Exception as ex:
            self.log.exception("Error during request sending")
            log.error = str(ex)
            ErrorLog.create(request_data=data, request_url=url, request_method=method,
                            error=str(ex), traceback=traceback.format_exc(chain=False))
            raise
        finally:
            log.finished = peewee_datetime.datetime.now()
            log.save()

    def _send(self, url, method, data=None, headers=None):
        return requests.request(method=method, url=url, headers=headers, data=data, timeout=HTTP_TIMEOUT)
