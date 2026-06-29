from decimal import Decimal, InvalidOperation

from django.shortcuts import render
from .models import Transaction
from django.http import HttpResponseRedirect
from django.urls import reverse
from accounts.models import Account
from django.utils import timezone


def history(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('accounts:login'))

    transfers = (
        Transaction.objects.filter(sender=request.user)
        | Transaction.objects.filter(recipient=request.user)
    )

    context = {'transfers': transfers}
    return render(request, 'transfer/history.html', context)


def transfer(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('accounts:login'))

    if request.method == 'POST':
        raw_amount = request.POST.get('amount', '').strip()
        to_user_email = request.POST.get('to_account', '').strip()

        try:
            amount = Decimal(raw_amount)
        except (InvalidOperation, ValueError):
            error_message = "Please enter a valid amount."
            return render(request, 'transfer/transfer.html', {
                'error_message': error_message
            })

        if not amount.is_finite():
            error_message = "Please enter a valid amount."
            return render(request, 'transfer/transfer.html', {
                'error_message': error_message
            })

        if amount < Decimal('100'):
            error_message = "The minimum transfer amount is 100."
            return render(request, 'transfer/transfer.html', {
                'error_message': error_message
            })

        if not to_user_email:
            error_message = "Recipient account is required."
            return render(request, 'transfer/transfer.html', {
                'error_message': error_message
            })

        current_user = request.user

        if current_user.email.lower() == to_user_email.lower():
            error_message = "You cannot transfer money to yourself."
            return render(request, 'transfer/transfer.html', {
                'error_message': error_message
            })

        if current_user.balance < amount:
            error_message = "Insufficient balance."
            return render(request, 'transfer/transfer.html', {
                'error_message': error_message
            })

        try:
            to_user = Account.objects.get(email__iexact=to_user_email)
        except Account.DoesNotExist:
            error_message = "Recipient account does not exist."
            return render(request, 'transfer/transfer.html', {
                'error_message': error_message
            })

        transaction = Transaction.objects.create(
            sender=current_user,
            recipient=to_user,
            amount=amount,
            timestamp=timezone.now(),
        )
        transaction.save()

        current_user.balance -= amount
        current_user.save()

        to_user.balance += amount
        to_user.save()

        return HttpResponseRedirect(reverse('transfers:history'))

    return render(request, 'transfer/transfer.html')