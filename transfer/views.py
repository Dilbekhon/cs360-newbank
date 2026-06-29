from decimal import Decimal
from decimal import Decimal, InvalidOperation
from django.shortcuts import redirect, render
from .models import Transaction
from django.http import HttpResponseRedirect
from django.urls import reverse
from accounts.models import Account
from django.utils import timezone

# Create your views here.
def history(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('accounts:login'))
    
    # Fetch transfer history for the user
    transfers = Transaction.objects.filter(sender=request.user) | Transaction.objects.filter(recipient=request.user)
    context = {'transfers': transfers}
    return render(request, 'transfer/history.html', context)

def transfer(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('accounts:login'))

    if request.method == 'POST':
        amount = request.POST.get('amount')
        to_user = request.POST.get('to_account')
        
        if float(amount) < 100: #
            error_message = "The minimum transfer amount is 100."
            return render(request, 'transfer/transfer.html', {'error_message': error_message})
        current_user = request.user
        print(f"Transfer request: {current_user.email}  -> {to_user}, Amount: {amount}", balance={current_user.balance}") #
        
        if current_user.balance < float(amount):
            error_message = "Insufficient balance."
            return render(request, 'transfer/transfer.html', {'error_message': error_message})
        try:
            to_user = Account.objects.get(email=to_user)
        except Account.DoesNotExist:
            error_message = "Recipient account does not exist."
            return render(request, 'transfer/transfer.html', {'error_message': error_message})

        transaction = Transaction.objects.create(
            sender=current_user,
            recipient=to_user,
            amount=amount,
            timestamp=timezone.now(),
        )
        transaction.save()

        current_user.balance -= Decimal(amount)
        current_user.save()
        
        to_user.balance += Decimal(amount)
        to_user.save()

        return HttpResponseRedirect(reverse('transfers:history'))
    return render(request, 'transfer/transfer.html')


