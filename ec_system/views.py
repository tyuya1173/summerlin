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
        queryset = Item.objects.get(pk=item_id)
        form = forms.IteminCartForm()
        context = {
            'item': queryset,
            'form': form,
        }
        return render(request, "ec_system/itemDetail.html", context)
    
class AddToCart(View):
    def post(self, request, item_id):
        new_cart = Itemincart()
        amount = int(request.POST["amountForm"])
        item = item_id
        user = "user001"
        new_cart.amount = amount
        new_cart.item_id = item
        new_cart.user_id = user
        new_cart.save()
        return redirect("ec_system:cart")
    
class Cart(View):
    def get(self, request):
        cart_items = Itemincart.objects.filter(user_id = "user001")
        total = 0
        for ci in cart_items:
            total += ci.item.price * ci.amount
        context = {
            'cart_items': cart_items,
            'total': total,
        }
        return render(request, "ec_system/cart.html", context)
