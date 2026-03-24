"""
Management command: expire_rides

Marks all PENDING rides whose departure_time is in the past as CANCELLED.
For each expired ride:
  - ACCEPTED bookings → escrow is released to the driver (driver compensation).
  - PENDING bookings  → escrow is fully refunded to the rider.

Usage:
    python manage.py expire_rides

Schedule this to run every 5–15 minutes via a cron job or Render Cron Job.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction as db_transaction
from django.db.models import F


class Command(BaseCommand):
    help = "Expire past PENDING rides and settle escrow funds accordingly."

    @db_transaction.atomic
    def handle(self, *args, **options):
        from rides.models import Ride
        from bookings.models import Booking
        from wallet.models import Wallet, EscrowRecord

        now = timezone.now()
        expired_rides = Ride.objects.select_for_update().filter(
            status=Ride.PENDING,
            departure_time__lt=now,
        )

        total_expired = 0
        total_released = 0
        total_refunded = 0

        for ride in expired_rides:
            ride.status = Ride.CANCELLED
            ride.save(update_fields=["status"])
            total_expired += 1

            bookings = Booking.objects.select_related("rider").filter(
                ride=ride,
                status__in=[Booking.ACCEPTED, Booking.PENDING],
            )

            for booking in bookings:
                try:
                    escrow = EscrowRecord.objects.select_for_update().get(
                        booking=booking,
                        status=EscrowRecord.Status.HELD,
                    )
                except EscrowRecord.DoesNotExist:
                    continue

                if booking.status == Booking.ACCEPTED:
                    # Driver gets paid — ride was accepted but ride time passed without starting
                    driver_wallet, _ = Wallet.objects.get_or_create(user=ride.driver)
                    driver_wallet.balance = F("balance") + escrow.amount
                    driver_wallet.save(update_fields=["balance"])
                    escrow.status = EscrowRecord.Status.RELEASED
                    total_released += 1
                else:
                    # Rider gets refunded — driver never accepted the booking
                    rider_wallet, _ = Wallet.objects.get_or_create(user=booking.rider)
                    rider_wallet.balance = F("balance") + escrow.amount
                    rider_wallet.save(update_fields=["balance"])
                    escrow.status = EscrowRecord.Status.REFUNDED
                    total_refunded += 1

                escrow.save(update_fields=["status"])

                # Update booking status to COMPLETED (ride ended) or CANCELLED
                booking.status = Booking.COMPLETED if booking.status == Booking.ACCEPTED else Booking.CANCELLED
                booking.save(update_fields=["status"])

        self.stdout.write(
            self.style.SUCCESS(
                f"Expired {total_expired} ride(s). "
                f"Released escrow for {total_released} booking(s). "
                f"Refunded {total_refunded} booking(s)."
            )
        )
