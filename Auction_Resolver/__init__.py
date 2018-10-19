import schedule
import time
import threading
from django.utils import timezone
from Auctions.models import *
from Auctions.views import send_email, get_current_winner


def check_auction(auction):
    now = timezone.now()
    if auction.deadline <= now:
        auction.status = Auction.STATUS_DUE
        auction.save()
        winner = get_current_winner(auction)
        if winner is not None:  # Send the winner a special mail and exclude him from the other mail list
            q = Bid.objects.filter(auction=auction).exclude(bidder=winner).values_list(
                'bidder__email', flat=True).distinct()
            send_email("You have won the auction for: " + auction.title + "!",
                       "We would like to let you know that the auction "
                       + auction.title + " has been resolved and that you have won by highest bid!",
                       [winner.email])
        else:  # If no winner (no bids)
            q = Bid.objects.filter(auction=auction).values_list(
                'bidder__email', flat=True).distinct()
        emails = list(q)
        emails.append(auction.seller.email)
        send_email("Auction: " + auction.title + " has been resolved", "We would like to let you know that the auction "
                   + auction.title + " has been resolved and a winner has been picked.",
                   emails)


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

