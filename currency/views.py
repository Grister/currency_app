from django.http import JsonResponse
from django.shortcuts import render
from currency.models import ExchangeRate
from currency.services import PrivatRateService


def privat(request):
    rates = ExchangeRate.objects.filter(provider__name='privat')
    context = {
        'rates_usd': rates.filter(currency='USD'),
        'rates_eur': rates.filter(currency='EUR'),
        'rates_chf': rates.filter(currency='CHF'),
        'rates_gbp': rates.filter(currency='GBP')
    }
    return render(request, template_name='currency/privat_rates.html', context=context)


def scrape_privat(request):
    service = PrivatRateService()
    results = service.get_rates()
    return JsonResponse({'data': results})
