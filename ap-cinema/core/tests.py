from django.contrib.auth import get_user_model
from django.test import TestCase

from core.models import Cinema, Movie, ShowTime, Reservation
from core.services import reserve_seats
from finance.models import Wallet


class ReservationTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="u1", password="pass12345")

        # make sure user has wallet and money
        wallet, _ = Wallet.objects.get_or_create(user=self.user)
        wallet.balance = 1_000_000
        wallet.save()

        self.cinema = Cinema.objects.create(name="C1", address="A1")
        self.movie = Movie.objects.create(title="M1", duration_minutes=90)

        self.showtime = ShowTime.objects.create(
            cinema=self.cinema,
            movie=self.movie,
            capacity=10,
            reserved_count=0,
            base_price=100_000,
        )

    def test_reserve_success_reduces_capacity(self):
        r = reserve_seats(
            user=self.user,
            showtime_id=self.showtime.id,
            seats=2,
            seat_type=Reservation.SeatType.NORMAL,
        )
        self.showtime.refresh_from_db()
        self.assertEqual(self.showtime.reserved_count, 2)
        self.assertEqual(r.seats, 2)

    def test_reserve_fails_when_not_enough_seats(self):
        reserve_seats(
            user=self.user,
            showtime_id=self.showtime.id,
            seats=10,
            seat_type=Reservation.SeatType.NORMAL,
        )
        with self.assertRaises(Exception):
            reserve_seats(
                user=self.user,
                showtime_id=self.showtime.id,
                seats=1,
                seat_type=Reservation.SeatType.NORMAL,
            )
