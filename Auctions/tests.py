from django.test import Client
import unittest
from .urls import *
from django.utils import timezone
from concurrency.exceptions import *


class TestAuctionCreation(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestAuctionCreation, cls).setUpClass()
        user = User.objects.create(first_name='NAME', last_name='LASTNAME', username='user1',
                                   email='email@hello.com')
        user.set_password('password')  # Required for not hashing pw
        user.save()
        cls.user = user


    def setUp(self):
        self.client = Client()

    def test_auction_created(self):

        Auction.objects.create(title='Title', description='description', deadline=timezone.now(), min_price=500.22,
                               seller=self.user)
        self.assertTrue(Auction.objects.filter(title='Title').exists())

    def test_auction_missing_seller(self):
        try:
            Auction.objects.create(title='NoSeller', description='description', deadline=timezone.now() +
                                                                         datetime.timedelta(hours=80),min_price=500.22)
        except:
            pass

        self.assertFalse(Auction.objects.filter(title='NoSeller').exists())

    def test_auction_post_form_not_logged_in_get(self):
        response = self.client.get(reverse('new_auction'))

        # Since not logged in, get for new auction should return 302 (moved temporarily) because of temporary redirect
        #  to login
        self.assertEqual(response.status_code, 302)

    def test_auction_post_form_logged_in_get(self):
        logged_in = self.client.login(username='user1', password='password')
        response = self.client.get(reverse('new_auction'))
        self.assertEqual(response.status_code, 200)

    def test_post_auction_form_success(self):
        self.client.login(username='user1', password='password')

        deadline = timezone.localtime() + datetime.timedelta(hours=74)
        deadlinecopy = deadline
        deadline = datetime.datetime.strptime(str(deadline), "%Y-%m-%d %H:%M:%S.%f%z")
        new_format = deadline.strftime('%d.%m.%Y %H:%M')
        deadline = datetime.datetime.strptime(new_format, '%d.%m.%Y %H:%M')
        response = self.client.post(reverse('new_auction'), {'title': 'Success', 'description': 'description',
                                                             'min_price': '0.01',
                                                             'deadline': deadline},
                                    follow=True)

        #  If 'Confirm' is in the source, the confirm form is loaded i.e. the form arguments passed requirements
        self.assertTrue('Confirm' in str(response.content))

        #  Client is sent to confirm page, no object should be created
        self.assertFalse(Auction.objects.filter(title='Success').exists())

        #  The formatting of the datetime is somehow changed if using actual browser but not here
        deadline = deadlinecopy.strftime('%Y-%m-%d %H:%M:%S%z')
        response = self.client.post(reverse('confirm_form'), {'title': 'Success', 'description': 'description',
                                                              'min_price': '0.01',
                                                              'deadline': deadline,
                                                              'yes': 'Confirm'})

        #  Sending the data through confirm page with 'yes' and good parameters should create a new object
        self.assertTrue(Auction.objects.filter(title='Success').exists())

    def test_post_auction_form_deadline_fail(self):
        self.client.login(username='user1', password='password')

        deadline = timezone.localtime() + datetime.timedelta(hours=20)  # Not enough time in future
        deadlinecopy = deadline
        deadline = datetime.datetime.strptime(str(deadline), "%Y-%m-%d %H:%M:%S.%f%z")
        new_format = deadline.strftime('%d.%m.%Y %H:%M')
        deadline = datetime.datetime.strptime(new_format, '%d.%m.%Y %H:%M')
        response = self.client.post(reverse('new_auction'), {'title': 'Deadline', 'description': 'description',
                                                             'min_price': '0.01',
                                                             'deadline': deadline},
                                    follow=True)

        #  'Confirm' would be part of the html source code of the confirm page because the deadline is not meeting req
        self.assertTrue('Confirm' not in str(response.content))
        self.assertFalse(Auction.objects.filter(title='Deadline').exists())

        deadline = deadlinecopy.strftime('%Y-%m-%d %H:%M:%S%z')

        # Try running it in confirm form
        response = self.client.post(reverse('confirm_form'), {'title': 'Deadline', 'description': 'description',
                                                              'min_price': '0.01',
                                                              'deadline': deadline,
                                                              'yes': 'Confirm'})

        self.assertFalse(Auction.objects.filter(title='Deadline').exists())

    def test_post_auction_form_min_price_fail(self):
        self.client.login(username='user1', password='password')

        deadline = timezone.localtime() + datetime.timedelta(hours=74)
        deadlinecopy = deadline
        deadline = datetime.datetime.strptime(str(deadline), "%Y-%m-%d %H:%M:%S.%f%z")
        new_format = deadline.strftime('%d.%m.%Y %H:%M')
        deadline = datetime.datetime.strptime(new_format, '%d.%m.%Y %H:%M')
        response = self.client.post(reverse('new_auction'), {'title': 'Min', 'description': 'description',
                                                             'min_price': '-2',
                                                             'deadline': deadline}, follow=True)

        #  'Confirm' would be part of the html source code of the confirm page because the min_price is not meeting req
        self.assertTrue('Confirm' not in str(response.content))
        self.assertFalse(Auction.objects.filter(title='Fail').exists())

        deadline = deadlinecopy.strftime('%Y-%m-%d %H:%M:%S%z')

        # Try running it in confirm form
        response = self.client.post(reverse('confirm_form'), {'title': 'Min', 'description': 'description',
                                                              'min_price': '-2',
                                                              'deadline': deadline,
                                                              'yes': 'Confirm'})

        self.assertFalse(Auction.objects.filter(title='Min').exists())


class BidTest(unittest.TestCase):

    def setUp(self):
        self.client = Client()

    @classmethod
    def setUpClass(cls):
        super(BidTest, cls).setUpClass()
        user3 = User.objects.create(first_name='NAME', last_name='LASTNAME', username='user3',
                                   email='email1@hello.com')
        user3.set_password('password')  # Required for not hashing pw
        user3.save()
        cls.user3 = user3
        cls.auction3 = Auction.objects.create(title='Test Auction', description='description',
                                              deadline=timezone.localtime()+datetime.timedelta(hours=80),
                                                min_price=50.00, seller=user3)
        user2 = User.objects.create(first_name='NAME', last_name='LASTNAME', username='user2',
                                   email='email2@hello.com')
        user2.set_password('password')  # Required for not hashing pw
        user2.save()
        cls.user2 = user2
        cls.auction2 = Auction.objects.create(title='Test Auction 2', description='description',
                          deadline=timezone.localtime()+datetime.timedelta(hours=80), min_price=500.22, seller=user2)


    def test_bid_success(self):
        self.client.login(username='user3', password='password')
        self.client.get(reverse('auction_view', kwargs={'auction_id': self.auction2.id}))  # Set session variable (required for checking if description has changed)

        response = self.client.post(reverse('auction_view', kwargs={'auction_id': self.auction2.id}),
                                    {'bid': '600.00'}, follow=True)

        # Make sure that user3 is the current winner with given amount
        self.assertTrue(Auction.objects.get(id=self.auction2.id, winning_bid__amount='600.00').winning_bid.bidder == self.user3,)

    def test_bid_fail_changed_description(self):
        self.client.login(username='user3', password='password')
        self.client.get(reverse('auction_view', kwargs={'auction_id': self.auction2.id}))  # Set session variable (required for checking if description has changed)

        # Have to get object again because of concurrency protection
        self.auction2 = Auction.objects.get(id=self.auction2.id)
        # Change description
        self.auction2.description = "CHANGED"
        self.auction2.save()

        response = self.client.post(reverse('auction_view', kwargs={'auction_id': self.auction2.id}),
                                    {'bid': '666.00'}, follow=True)

        # Make sure the bid does not exist
        self.assertFalse(Auction.objects.filter(id=self.auction2.id, winning_bid__amount='666.00').exists())

    def test_bid_fail_no_login(self):
        self.client.get(reverse('auction_view', kwargs={'auction_id': self.auction2.id}))  # Set session variable (required for checking if description has changed)
        try:
            response = self.client.post(reverse('auction_view', kwargs={'auction_id': self.auction2.id}),
                                    {'bid': '1000.00'}, follow=True)
        except:
            pass

        self.assertFalse(Bid.objects.filter(auction_id=self.auction2.id, amount='1000.00').exists())

    def test_bid_too_low_min_price(self):
        self.client.login(username='user3', password='password')
        self.client.get(reverse('auction_view', kwargs={'auction_id': self.auction2.id}))  # Set session variable (required for checking if description has changed)

        response = self.client.post(reverse('auction_view', kwargs={'auction_id': self.auction2.id}),
                                    {'bid': '200.00'}, follow=True)

        self.assertFalse(Bid.objects.filter(auction_id=self.auction2.id, amount='200.00').exists())

    def test_bid_too_low_highest_bidder(self):
        self.client.login(username='user3', password='password')
        self.client.get(reverse('auction_view', kwargs={'auction_id': self.auction2.id}))  # Set session variable (required for checking if description has changed)

        response = self.client.post(reverse('auction_view', kwargs={'auction_id': self.auction2.id}),
                                    {'bid': '600.00'}, follow=True)

        self.client.logout()

        user4 = User.objects.create(username='user4')
        user4.set_password('password')
        user4.save()

        self.client.login(username='user4', password='password')
        self.client.get(reverse('auction_view', kwargs={
            'auction_id': self.auction2.id}))  # Set session variable (required for checking if description has changed)

        # Try make bid greater than min price but less than winning bid
        response = self.client.post(reverse('auction_view', kwargs={'auction_id': self.auction2.id}),
                                    {'bid': '550.00'}, follow=True)

        # Assume False for finding the bid from user4
        self.assertFalse(Bid.objects.filter(auction_id=self.auction2.id, bidder=user4).exists())

    def test_bid_on_own(self):
        self.client.login(username='user3', password='password')
        # user3 is seller of auction3
        self.client.get(reverse('auction_view', kwargs={'auction_id': self.auction3.id}))  # Set session variable (required for checking if description has changed)

        # Should be fine because 100>50 but because user==seller NO
        response = self.client.post(reverse('auction_view', kwargs={'auction_id': self.auction3.id}),
                                    {'bid': '100.00'}, follow=True)

        self.assertFalse(Bid.objects.filter(auction_id=self.auction2.id, amount='100.00').exists())

    def test_bid_on_non_active(self):
        self.client.login(username='user3', password='password')
        new_auction = Auction.objects.create(seller=self.user2, title='New auction', description='desc',
                                             deadline=timezone.localtime()+datetime.timedelta(hours=80),
                                             min_price='20.00')
        new_auction.status = Auction.STATUS_BANNED
        new_auction.save()

        # Auction should exist
        self.assertTrue(Auction.objects.filter(id=new_auction.id).exists())

        self.client.get(reverse('auction_view', kwargs={'auction_id': new_auction.id}))  # Set session variable (required for checking if description has changed)

        # Should be fine because 25>20 but because status != ACTIVE nop
        response = self.client.post(reverse('auction_view', kwargs={'auction_id': new_auction.id}),
                                    {'bid': '25.00'}, follow=True)

        # Bid should not exist
        self.assertFalse(Bid.objects.filter(auction_id=new_auction.id, amount='25.00').exists())

    def test_bid_even_though_winner(self):
        self.client.login(username='user3', password='password')
        self.client.get(reverse('auction_view', kwargs={'auction_id': self.auction2.id}))  # Set session variable (required for checking if description has changed)

        response = self.client.post(reverse('auction_view', kwargs={'auction_id': self.auction2.id}),
                                    {'bid': '600.00'}, follow=True)

        self.client.get(reverse('auction_view', kwargs={'auction_id': self.auction2.id}))  # Set session variable (required for checking if description has changed)

        # Try overbid himself
        response = self.client.post(reverse('auction_view', kwargs={'auction_id': self.auction2.id}),
                                    {'bid': '700.00'}, follow=True)

        # If overbidding himself was possible, there should now be 2 bids on this auction
        self.assertFalse(len(Bid.objects.filter(auction_id=self.auction2.id)) == 2)


class ConcurrencyTest(unittest.TestCase):

    def setUp(self):
        self.client = Client()

    @classmethod
    def setUpClass(cls):
        super(ConcurrencyTest, cls).setUpClass()
        user5 = User.objects.create(username='user5')
        user5.set_password('password')  # Required for not hashing pw
        user5.save()
        cls.user5 = user5
        cls.an_auction = Auction.objects.create(title='Concurrency', description='description',
                                              deadline=timezone.localtime()+datetime.timedelta(hours=80),
                                                min_price=50.00, seller=user5)
        user6 = User.objects.create(username='user6')
        user6.set_password('password')  # Required for not hashing pw
        user6.save()
        cls.user6 = user6

        user7 = User.objects.create(username='user7')
        user7.set_password('password')  # Required for not hashing pw
        user7.save()
        cls.user7 = user7

    def test_concurrency(self):
        auction_user6 = Auction.objects.get(id=self.an_auction.id)  # Get auction
        auction_user7 = Auction.objects.get(id=self.an_auction.id)  # Get auction

        user6_bid = Bid.objects.create(bidder=self.user6, amount='55.00', auction=auction_user6)
        auction_user6.winning_bid = user6_bid
        auction_user6.save()

        user7_bid = Bid.objects.create(bidder=self.user7, amount='55.00', auction=auction_user7)
        auction_user7.winning_bid = user7_bid

        try:
            auction_user7.save()
        except RecordModifiedError:
            user7_bid.delete()

        # user7's bid got deleted above as it does in the actual code if concurrency occurs
        self.assertFalse(Bid.objects.filter(bidder=self.user7).exists())

