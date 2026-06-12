from django.shortcuts import render
from django.shortcuts import redirect
from django.views.generic import View
from ec_system.models import Account, Category, Item, Itemincart, Purchase, Purchasedetail, Admin 
from . import models
from . import forms


def index(request):
    return render(request, "ec_system/main.html")

class SearchResult(View):
    def get(self):
        pass

    def post(self, request):
        keyword = request.POST["keyword"]
        category = request.POST["category"]
        queryset = Item.objects.all()
        if keyword:
            queryset = queryset.filter(name__icontains=keyword)

        if category == '鞄':
            queryset = queryset.filter(category__category_id = 1)
        elif category == '帽子':
            queryset = queryset.filter(category__category_id = 2)

        context = {
            'keyword': keyword,
            'category': category,
            'item': queryset
        }
        return render(request, 'ec_system/searchResult.html', context)
    
class Login(View):
    def get(self, request):
        return render(request, 'ec_system/login.html')

    def post(self, request):
        pass

class Itemdetail(View):
    def get(self, request, item_id):
        qeryset = Item.objects.get(pk=item_id)
        form = forms.IteminCartForm()
        context = {
            'item': qeryset,
            'form': form,
        }
        return render(request, "ec_system/itemDetail.html", context)