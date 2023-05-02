import logging
from datetime import datetime
from logging.config import dictConfig
from apscheduler.schedulers.blocking import BlockingScheduler
import config
import controllers

sched = BlockingScheduler()
dictConfig(config.LOGGING)
log = logging.getLogger("Tasks")

@sched.scheduled_job('interval', minutes=1)
def updates_rates():
    log.info(f"Job started at {datetime.now()}")
    data = {'from_currency': None, 'to_currency': None, 'source': None}
    try:
        controllers.UpdateRates().call(data)
    except Exception as ex:
        print(ex)
        log.exception(ex)
    log.info("Job finished")

sched.start()
log.info("Scheduler started")
