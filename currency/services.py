from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from datetime import timedelta, datetime

from config.settings import MAX_WORKERS
from currency.models import ExchangeRate, ExchangeRateProvider


class ProviderService(object):
    def __init__(self, name, api_url):
        self.name = name
        self.api_url = api_url

    def get_or_create(self):
        provider, created = ExchangeRateProvider.objects.get_or_create(name=self.name, api_url=self.api_url)
        if created:
            print("ExchangeRateProvider created:", provider)
        else:
            print("Existing ExchangeRateProvider retrieved:", provider)
        return provider


class ExchangeRateService:
    CURRENCIES = ["GBP", "USD", "EUR", "CHF"]

    def __init__(self, provider, start_date, end_date):
        self.provider = provider
        self.start_date = start_date
        self.end_date = end_date

    @property
    def num_days(self):
        delta = self.end_date - self.start_date
        return delta.days

    @property
    def url(self):
        return self.provider.api_url

    def get_rates(self):
        delta = timedelta(days=1)
        current = self.start_date

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = [executor.submit(self.get_rate, date=current + i * delta) for i in range(self.num_days)]
            objects = []
            for future in as_completed(futures):
                currency_rates = future.result()
                if currency_rates != "Failed to process data":
                    for rates in currency_rates:
                        rates["provider_id"] = self.provider.pk
                        rate, _ = ExchangeRate.objects.get_or_create(**rates)
                    objects.append(currency_rates)
        return objects

    def get_rate(self, date):
        params = {
            'date': str(date.strftime('%d.%m.%Y'))
        }
        response = requests.get(self.url, params=params)
        print(f"Date: {str(date.strftime('%d.%m.%Y'))} Status code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            currency_rates = []
            rates = data['exchangeRate']
            base_currency = data['baseCurrencyLit']
            r_date = datetime.strptime(data['date'], '%d.%m.%Y').date()
            for r in rates:
                if r['currency'] not in self.CURRENCIES:
                    continue

                currency_rates.append(
                    {
                        'base_currency': base_currency,
                        'currency': r['currency'],
                        'sale_rate': r['saleRate'],
                        'buy_rate': r['purchaseRate'],
                        'date': r_date.strftime('%Y-%m-%d')
                    }
                )
            return currency_rates
        return "Failed to process data"
