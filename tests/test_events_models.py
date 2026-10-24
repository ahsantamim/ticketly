from datetime import timedelta

import pytest
from django.db import IntegrityError
from django.db.models import ProtectedError
from django.utils import timezone

from events.models import Event, EventStatus
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
