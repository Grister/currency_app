from django.db import models


class ExchangeRateProvider(models.Model):
    name = models.CharField(max_length=20)
    api_url = models.URLField()


class ExchangeRate(models.Model):
    date = models.DateField()

    base_currency = models.CharField(max_length=10)
    currency = models.CharField(max_length=10)

    sale_rate = models.DecimalField(max_digits=10, decimal_places=4)
    buy_rate = models.DecimalField(max_digits=10, decimal_places=4)

    provider = models.ForeignKey(ExchangeRateProvider, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.base_currency}/{self.currency}"
