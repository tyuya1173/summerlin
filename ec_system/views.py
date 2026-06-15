from django.shortcuts import render
from django.shortcuts import redirect
from django.views.generic import View
from ec_system.models import Account, Category, Item, Itemincart, Purchase, Purchasedetail, Admin 
from . import forms
from django.db import transaction


def index(request):
    form = forms.ItemSearchForm()
    user_id = request.session.get("user_id")
    if user_id:
        login_user = Account.objects.filter(user_id=user_id).first()
    else:
        login_user = None
    return render(request, "ec_system/main.html", {"form": form, "login_user": login_user})

class SearchResult(View):

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
        form = forms.LoginForm()
        return render(request, "ec_system/login.html", {"form": form})

    def post(self, request):
        form = forms.LoginForm(request.POST)
        if form.is_valid():
            request.session["user_id"] = form.account.user_id
            return redirect("ec_system:index")
        return render(request, "ec_system/login.html", {"form": form})

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
    
class Logout(View):
    def get(self, request):
        request.session.flush()
        return redirect("ec_system:login")

class RegisterUser(View):
    def get(self, request):
        form = forms.RegisterForm()
        return render(request, "ec_system/registerUser.html", {"form": form})

    def post(self, request):
        form = forms.RegisterForm(request.POST)
        if form.is_valid():
            return render(request, "ec_system/registerUserConfirm.html", {"form": form})
        return render(request, "ec_system/registerUser.html", {"form": form})
    
class RegisterCommit(View):
    def post(self, request):
        form = forms.RegisterForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                Account.objects.create(
                    user_id=form.cleaned_data["user_id"],
                    password=form.cleaned_data["password"],
                    name=form.cleaned_data["name"],
                    address=form.cleaned_data["address"],
                )
                context = {
                    "name": form.cleaned_data["name"],
                }
            return render(request,"ec_system/registerUserCommit.html", context)
        
        return render(request, "ec_system/registerUser.html", {"form": form})
    
class UserInfo(View):
    def get(self, request):
        user_id = request.session.get("user_id")
        if user_id:
            login_user = Account.objects.filter(user_id=user_id).first()
        else:
            login_user = None
        if login_user is None:
            return redirect("ec_system:login")
        return render(request, "ec_system/userInfo.html", {"login_user": login_user})
    
class UpdateUser(View):
    def get(self, request):
        user_id = request.session.get("user_id")
        if user_id:
            login_user = Account.objects.filter(user_id=user_id).first()
        else:
            login_user = None
        if login_user is None:
            return redirect("ec_system:login")
        form = forms.UpdateUserForm(initial={"name": login_user.name, "address": login_user.address})
        context = {
            "form": form,
            "login_user": login_user
        }
        return render(request, "ec_system/updateUser.html", context)

    def post(self, request):
        user_id = request.session.get("user_id")
        if user_id:
            login_user = Account.objects.filter(user_id=user_id).first()
        else:
            login_user = None
        if login_user is None:
            return redirect("ec_system:login")
        form = forms.UpdateUserForm(request.POST)
        if form.is_valid():
            context = {
                "form": form,
                "login_user": login_user
            }
            return render(request, "ec_system/updateUserConfirm.html", context)
        return render(request, "ec_system/updateUser.html", {"form": form, "login_user": login_user})
    
class UpdateUserCommit(View):
    def post(self, request):
        user_id = request.session.get("user_id")
        if user_id:
            login_user = Account.objects.filter(user_id=user_id).first()
        else:
            login_user = None

        if login_user is None:
            return redirect("ec_system:login")
        form = forms.UpdateUserForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                login_user.name = form.cleaned_data["name"]
                login_user.address = form.cleaned_data["address"]
                if form.cleaned_data["password"]:
                    login_user.password = form.cleaned_data["password"]
                login_user.save()
            return render(request, "ec_system/updateUserCommit.html", {"login_user": login_user})
        return render(request, "ec_system/updateUser.html", {"form": form, "login_user": login_user})
    
class WithDrawConfirm(View):
    def get(self, request):
        user_id = request.session.get("user_id")
        if user_id:
            login_user = Account.objects.filter(user_id=user_id).first()
        else:
            login_user = None

        if login_user is None:
            return redirect("ec_system:login")
        return render(request, "ec_system/withdrawConfirm.html", {"login_user": login_user})
    
class WithDrawCommit(View):
    def post(self, request):
        user_id = request.session.get("user_id")
        if user_id:
            login_user = Account.objects.filter(user_id=user_id).first()
        else:
            login_user = None
            
        if login_user is None:
            return redirect("ec_system:login")
        name = login_user.name
        with transaction.atomic():
            login_user.delete()
        request.session.flush()
        return render(request, "ec_system/withdrawCommit.html", {"name": name})