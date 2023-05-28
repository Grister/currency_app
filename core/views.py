from django.shortcuts import render
from currency.tasks import add, hello


def index(request):
    add.delay(3, 5)
    hello.delay()
    return render(request, 'core/index.html')
