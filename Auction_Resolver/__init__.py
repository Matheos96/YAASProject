import schedule
import time
import threading
from django.utils import timezone
from Auctions.models import *
from Auctions.views import send_email


def check_auction(auction):
    now = timezone.now()
    if auction.deadline <= now:
        auction.status = Auction.STATUS_DUE
        auction.save()
        #  NOTIFY USERS AND SELLER!!!!!


def resolve_auctions():  # Checks if auctions have passed their deadlines and changes their statuses to due
    auctions = Auction.objects.filter(status=Auction.STATUS_ACTIVE)
    for auction in auctions:
        check_auction(auction)


schedule.every().minute.do(resolve_auctions)  # Check every minute if a deadline has passed


class ScheduleThread(threading.Thread):  # Scheduler thread
    def __init__(self, *pargs, **kwargs):
        super().__init__(*pargs, daemon=True, name="scheduler", **kwargs)

    def run(self):
        while True:
            schedule.run_pending()
            time.sleep(schedule.idle_seconds())

