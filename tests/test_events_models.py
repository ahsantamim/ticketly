from datetime import timedelta
from decimal import Decimal

import pytest
from django.db import IntegrityError
from django.db.models import ProtectedError
from django.utils import timezone

from events.models import Event, EventStatus, TicketTier
from venues.models import Venue

pytestmark = pytest.mark.django_db


@pytest.fixture
def venue():
    return Venue.objects.create(
        name="Main Hall", address="1 Road", city="Dhaka", timezone="Asia/Dhaka"
    )


@pytest.fixture
def starts_at():
    return timezone.now() + timedelta(days=7)


def make_event(venue, starts_at, **overrides):
    fields = {
        "venue": venue,
        "title": "Concert",
        "starts_at": starts_at,
        "ends_at": starts_at + timedelta(hours=2),
    }
    fields.update(overrides)
    return Event.objects.create(**fields)


def test_valid_event_saves_as_draft(venue, starts_at):
    event = make_event(venue, starts_at)

    assert event.status == EventStatus.DRAFT


@pytest.mark.parametrize("duration", [timedelta(0), timedelta(hours=-1)])
def test_end_not_after_start_raises_integrity_error(venue, starts_at, duration):
    with pytest.raises(IntegrityError):
        make_event(venue, starts_at, ends_at=starts_at + duration)


def test_unknown_status_raises_integrity_error(venue, starts_at):
    with pytest.raises(IntegrityError):
        make_event(venue, starts_at, status="bogus")


def test_deleting_venue_with_events_is_blocked(venue, starts_at):
    make_event(venue, starts_at)

    with pytest.raises(ProtectedError):
        venue.delete()

    assert Venue.objects.count() == 1
    assert Event.objects.count() == 1


@pytest.fixture
def event(venue, starts_at):
    return make_event(venue, starts_at)


def test_tier_price_round_trips_exactly(event):
    tier = TicketTier.objects.create(event=event, name="VIP", price=Decimal("19.99"))

    tier.refresh_from_db()

    assert tier.price == Decimal("19.99")


def test_free_tier_is_allowed(event):
    TicketTier.objects.create(event=event, name="Free", price=Decimal("0"))

    assert TicketTier.objects.count() == 1


def test_negative_price_raises_integrity_error(event):
    with pytest.raises(IntegrityError):
        TicketTier.objects.create(event=event, name="VIP", price=Decimal("-0.01"))


def test_duplicate_tier_name_in_same_event_raises_integrity_error(event):
    TicketTier.objects.create(event=event, name="VIP", price=Decimal("50.00"))

    with pytest.raises(IntegrityError):
        TicketTier.objects.create(event=event, name="VIP", price=Decimal("60.00"))


def test_same_tier_name_allowed_on_another_event(event, venue, starts_at):
    other = make_event(venue, starts_at + timedelta(days=1), title="Encore")
    TicketTier.objects.create(event=event, name="VIP", price=Decimal("50.00"))

    TicketTier.objects.create(event=other, name="VIP", price=Decimal("50.00"))

    assert TicketTier.objects.count() == 2
