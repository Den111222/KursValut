# from flask import request
from functools import wraps

from flask import request, abort#, render_template

from app import app
import controllers
from config import IP_LIST


def check_ip(func):
    @wraps(func)
    def checker(*args, **kwds):
        if request.remote_addr not in IP_LIST:
            return abort(403)

        return func(*args, **kwds)

    return checker

@app.route("/")
def hello():
    return "Hello everybody!"


@app.route("/xrates")
def view_rates():
    return controllers.ViewAllRates().call()

#Format xml and json. /api/xrates/xml and /api/xrates/json
@app.route("/api/xrates/<fmt>")
def api_rates(fmt):
    return controllers.GetApiRates().call(fmt)

@app.route("/update/<int:from_currency>/<int:to_currency>/<string:source>")
@app.route("/update/all")
def update_xrates(from_currency=None, to_currency=None, source=None):
    data = {'from_currency': from_currency, 'to_currency': to_currency, 'source': source}
    return controllers.UpdateRates().call(data)

#Для информации /logs/api and /logs/error проверка в controllers.py стр. 79
@app.route("/logs/<log_type>")
@check_ip
def view_logs(log_type):
    return controllers.ViewLogs().call()

@app.route("/edit/<int:from_currency>/<int:to_currency>", methods=["GET", "POST"])
@check_ip
def edit_xrate(from_currency, to_currency):
    return controllers.EditRate().call(to_currency)

