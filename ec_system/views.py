from django.shortcuts import render
from django.shortcuts import redirect
from . import models


def index(request):
    return render(request, "ec_system/main.html")
