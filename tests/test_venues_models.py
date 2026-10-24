import pytest
from django.db import IntegrityError

from venues.models import Seat, Venue

pytestmark = pytest.mark.django_db


@pytest.fixture
def venue():
    return Venue.objects.create(
        name="Main Hall", address="1 Road", city="Dhaka", timezone="Asia/Dhaka"
    )


def test_duplicate_seat_in_same_venue_raises_integrity_error(venue):
    Seat.objects.create(venue=venue, section="A", row="1", number=5)

    with pytest.raises(IntegrityError):
        Seat.objects.create(venue=venue, section="A", row="1", number=5)


def test_same_seat_label_allowed_in_another_venue(venue):
    other = Venue.objects.create(
        name="Annex", address="2 Road", city="Dhaka", timezone="Asia/Dhaka"
    )
    Seat.objects.create(venue=venue, section="A", row="1", number=5)

    Seat.objects.create(venue=other, section="A", row="1", number=5)

    assert Seat.objects.count() == 2


def test_deleting_venue_deletes_its_seats(venue):
    Seat.objects.create(venue=venue, section="A", row="1", number=5)

    venue.delete()

    assert Seat.objects.count() == 0
