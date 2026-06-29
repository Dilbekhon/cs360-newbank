from datetime import datetime

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone

from .models import Booking


def index(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('accounts:login'))

    bookings = Booking.objects.filter(booked_by=request.user)
    return render(request, 'booking/index.html', {'bookings': bookings})


def add(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('accounts:login'))

    if request.method == 'POST':
        reason = request.POST.get('reason', '').strip()
        date_value = request.POST.get('date', '').strip()
        time_value = request.POST.get('time', '').strip()

        context = {
            'reason': reason,
            'date': date_value,
            'time': time_value,
        }

        if not reason or not date_value or not time_value:
            context['error_message'] = 'Reason, date, and time are required.'
            return render(request, 'booking/add.html', context)

        try:
            booking_datetime = datetime.fromisoformat(
                f'{date_value}T{time_value}'
            )
        except ValueError:
            context['error_message'] = 'Please enter a valid date and time.'
            return render(request, 'booking/add.html', context)

        if settings.USE_TZ and timezone.is_naive(booking_datetime):
            booking_datetime = timezone.make_aware(booking_datetime)

        Booking.objects.create(
            reason=reason,
            date=booking_datetime,
            booked_by=request.user
        )

        return HttpResponseRedirect(reverse('booking:index'))

    return render(request, 'booking/add.html')