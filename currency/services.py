from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from datetime import date, timedelta, datetime

from config.settings import MAX_WORKERS
from currency.models import ExchangeRate, ExchangeRateProvider


class PrivatRateService:
    API_URL = "https://api.privatbank.ua/p24api/exchange_rates"
    CURRENCIES = ["GBP", "USD", "EUR", "CHF"]
    NAME = 'privat'

    @staticmethod
    def get_dates_from_start_of_year():
        today = date.today()
        start_of_year = date(today.year, 1, 1)
        dates = []
        for i in range((today - start_of_year).days + 1):
            dates.append((start_of_year + timedelta(days=i)).strftime('%d.%m.%Y'))
        return dates

    def get_rates(self):
        dates_list = self.get_dates_from_start_of_year()
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = []

            for date_ in dates_list:
                params = {
                    'date': date_,
                    'json': ''
                }
                futures.append(executor.submit(self.get_rate, **params))
        results = []
        for future in as_completed(futures):
            result = future.result()
            if result != "Failed to process data":
                self.persist_objects(result)
                results.append(result)
        return results

    def get_rate(self, **kwargs):
        response = requests.get(self.API_URL, params=kwargs)
        print(f"Date: {kwargs.get('date')} Status code: {response.status_code}")
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

    def persist_objects(self, objects):
        provider = ExchangeRateProvider.objects.filter(name=self.NAME).first()
        if not provider:
            provider = ExchangeRateProvider(name=self.NAME, api_url=self.API_URL)
            provider.save()

        for rate in objects:
            entry = ExchangeRate.objects.filter(currency=rate.get('currency'),
                                                date=rate.get('date'),
                                                provider__name=self.NAME).first()
            if not entry:
                entry = ExchangeRate(
                    base_currency=rate.get('base_currency'),
                    currency=rate.get('currency'),
                    sale_rate=rate.get('sale_rate'),
                    buy_rate=rate.get('buy_rate'),
                    date=rate.get('date'),
                    provider=provider
                )
                entry.save()
