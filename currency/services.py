from decimal import Decimal


def convert_currency(amount, from_currency, to_currency):
    rates = {
        ("USD", "UZS"): Decimal("12600"),
        ("UZS", "USD"): Decimal("0.0000793650793651"),
    }

    fee = Decimal("0.02")  

    key = (from_currency, to_currency)

    if key not in rates:
        raise ValueError("Unsupported currency pair")

    converted = amount * rates[key]
    converted = converted * (Decimal("1") - fee)

    return converted.quantize(Decimal("0.01"))