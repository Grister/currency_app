import datetime

from django.http import JsonResponse
from django.shortcuts import render
from currency.models import ExchangeRate
from currency.services import ProviderService, ExchangeRateService


def privat(request):
    rates = ExchangeRate.objects.filter(provider__name='privat')
    context = {
        'rates_usd': rates.filter(currency='USD').order_by('-date'),
        'rates_eur': rates.filter(currency='EUR').order_by('-date'),
        'rates_chf': rates.filter(currency='CHF').order_by('-date'),
        'rates_gbp': rates.filter(currency='GBP').order_by('-date')
    }
    return render(request, template_name='currency/privat_rates.html', context=context)


def scrape_privat(request):
    provider_data = dict(
        name='privat',
        url="https://api.privatbank.ua/p24api/exchange_rates"
    )
    provider_service = ProviderService(
        name=provider_data.get('name'),
        api_url=provider_data.get('url')
    )
    service = ExchangeRateService(
        provider=provider_service.get_or_create(),
        start_date=datetime.datetime(2023, 5, 1),
        end_date=datetime.datetime.now()
    )
    results = service.get_rates()
    return JsonResponse({'data': results})
