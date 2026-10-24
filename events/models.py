from django.db import models
from django.db.models import F, Q

from venues.models import Seat, Venue


# Module level, not nested in Event, so Meta.constraints can reference it.
class EventStatus(models.TextChoices):
    DRAFT = "draft"
    PUBLISHED = "published"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class Event(models.Model):
    # PROTECT: a venue with events can't be deleted; events carry sales history.
    venue = models.ForeignKey(Venue, on_delete=models.PROTECT, related_name="events")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    status = models.CharField(max_length=20, choices=EventStatus.choices, default=EventStatus.DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(ends_at__gt=F("starts_at")), name="event_ends_after_starts"
            ),
            # choices are only checked by forms/serializers, so enforce them in the DB too.
            models.CheckConstraint(
                condition=Q(status__in=EventStatus.values), name="event_status_valid"
            ),
        ]
        indexes = [
            models.Index(fields=["status", "starts_at"], name="event_status_starts_idx"),
            models.Index(fields=["venue", "starts_at"], name="event_venue_starts_idx"),
        ]

    def __str__(self):
        return self.title


class TicketTier(models.Model):
    # No capacity column: for reserved seating it's the count of EventSeat rows on this tier.
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="tiers")
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        constraints = [
            models.CheckConstraint(condition=Q(price__gte=0), name="tier_price_non_negative"),
            models.UniqueConstraint(fields=["event", "name"], name="tier_unique_name_per_event"),
        ]

    def __str__(self):
        return f"{self.event} / {self.name}"


class EventSeatStatus(models.TextChoices):
    AVAILABLE = "available"
    HELD = "held"
    SOLD = "sold"


class EventSeat(models.Model):
    """One inventory row per (event, seat). Phase 2 claims seats with a conditional UPDATE."""

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="inventory")
    # RESTRICT, not PROTECT: blocks deleting a seat or tier that has inventory, but still
    # lets event.delete() cascade, since these rows are deleted through Event as well.
    seat = models.ForeignKey(Seat, on_delete=models.RESTRICT, related_name="event_seats")
    tier = models.ForeignKey(TicketTier, on_delete=models.RESTRICT, related_name="event_seats")
    status = models.CharField(
        max_length=20, choices=EventSeatStatus.choices, default=EventSeatStatus.AVAILABLE
    )
    hold_expires_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["event", "seat"], name="event_seat_unique"),
            models.CheckConstraint(
                condition=Q(status__in=EventSeatStatus.values), name="event_seat_status_valid"
            ),
            # A hold must expire, and only holds have an expiry.
            models.CheckConstraint(
                condition=(
                    Q(status=EventSeatStatus.HELD, hold_expires_at__isnull=False)
                    | (~Q(status=EventSeatStatus.HELD) & Q(hold_expires_at__isnull=True))
                ),
                name="event_seat_hold_expiry_iff_held",
            ),
        ]
        indexes = [
            models.Index(fields=["event", "status"], name="event_seat_event_status_idx"),
            # Small partial index for the Phase 2 job that expires holds.
            models.Index(
                fields=["hold_expires_at"],
                condition=Q(status=EventSeatStatus.HELD),
                name="event_seat_held_expiry_idx",
            ),
        ]

    def __str__(self):
        return f"{self.event} / {self.seat} ({self.status})"
