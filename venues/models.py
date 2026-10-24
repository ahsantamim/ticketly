from django.db import models


class Venue(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    # IANA name (e.g. "Asia/Dhaka"), for display only. Timestamps are stored in UTC.
    timezone = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Seat(models.Model):
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name="seats")
    section = models.CharField(max_length=50)
    row = models.CharField(max_length=10)
    # Integer so the seat map sorts 2 before 10.
    number = models.PositiveIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["venue", "section", "row", "number"], name="seat_unique_per_venue"
            ),
        ]

    def __str__(self):
        return f"{self.section} {self.row}-{self.number}"
