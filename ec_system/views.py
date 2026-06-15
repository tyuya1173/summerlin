from django.shortcuts import render
from django.shortcuts import redirect
from django.views.generic import View
from ec_system.models import Account, Category, Item, Itemincart, Purchase, Purchasedetail, Admin 
from . import forms
from django.db import transaction
from django.db.models import Max 

def is_login(request):
    user_id = request.session.get("user_id")
    if user_id:
        login_user = Account.objects.filter(user_id=user_id).first()
    else:
        login_user = None

    return login_user

def index(request):
    login_user = is_login(request)
    context = {
        'login_user': login_user
    }
    return render(request, "ec_system/main.html", context)

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
        context = {
            'form': form,
        }
        return render(request, "ec_system/login.html", context)

    def post(self, request):
        form = forms.LoginForm(request.POST)
        if form.is_valid():
            request.session["user_id"] = form.account.user_id
            return redirect("ec_system:index")
        context = {
            'form': form,
        }
        return render(request, "ec_system/login.html", context)

class Itemdetail(View):
    def get(self, request, item_id):
        login_user = is_login(request)

        queryset = Item.objects.get(pk=item_id)
        form = forms.IteminCartForm()
        context = {
            'item': queryset,
            'form': form,
            'login_user': login_user,
        }
        return render(request, "ec_system/itemDetail.html", context)
    
class AddToCart(View):
    def post(self, request, item_id):
        login_user = is_login(request)
        if login_user is None:
            return redirect("ec_system:login")

        user_id = request.session.get("user_id")
        new_cart = Itemincart()
        amount = int(request.POST["amountForm"])
        new_cart.amount = amount
        new_cart.item_id = item_id
        new_cart.user_id = user_id
        new_cart.save()
        return redirect("ec_system:cart")
    
class Cart(View):
    def get(self, request):
        user_id = request.session.get("user_id")
        cart_items = Itemincart.objects.filter(user_id = user_id)
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
        context = {
            'form': form,
        }
        return render(request, "ec_system/registerUser.html", context)

    def post(self, request):
        form = forms.RegisterForm(request.POST)
        if form.is_valid():
            context = {
                'form': form,
            }
            return render(request, "ec_system/registerUserConfirm.html", context)
        context = {
            'form': form
        }
        return render(request, "ec_system/registerUser.html", context)
    
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
        
        context = {
            'form': form
        }
        return render(request, "ec_system/registerUser.html", context)
    
class UserInfo(View):
    def get(self, request):
        login_user = is_login(request)
        if login_user is None:
            return redirect("ec_system:login")
        
        context = {
            'login_user': login_user
        }
        return render(request, "ec_system/userInfo.html", context)
    
class UpdateUser(View):
    def get(self, request):
        login_user = is_login(request)
        if login_user is None:
            return redirect("ec_system:login")
        form = forms.UpdateUserForm(initial={"name": login_user.name, "address": login_user.address})
        context = {
            "form": form,
            "login_user": login_user
        }
        return render(request, "ec_system/updateUser.html", context)

    def post(self, request):
        login_user = is_login(request)
        if login_user is None:
            return redirect("ec_system:login")
        form = forms.UpdateUserForm(request.POST)
        if form.is_valid():
            context = {
                "form": form,
                "login_user": login_user
            }
            return render(request, "ec_system/updateUserConfirm.html", context)
        
        context = {
            'form': form,
            'login_user': login_user
        }
        return render(request, "ec_system/updateUser.html", context)
    
class UpdateUserCommit(View):
    def post(self, request):
        login_user = is_login(request)

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
            context = {
                'login_user': login_user
            }
            return render(request, "ec_system/updateUserCommit.html", context)
        
        context = {
            'form': form,
            'login_user': login_user
        }
        return render(request, "ec_system/updateUser.html", context)
    
class WithDrawConfirm(View):
    def get(self, request):
        login_user = is_login(request)

        if login_user is None:
            return redirect("ec_system:login")
        
        context = {
            "login_user": login_user
        }
        return render(request, "ec_system/withdrawConfirm.html", context)
    
class WithDrawCommit(View):
    def post(self, request):
        login_user = is_login(request)
            
        if login_user is None:
            return redirect("ec_system:login")
        name = login_user.name
        with transaction.atomic():
            login_user.delete()
        request.session.flush()
        context = {
            "name": name
        }
        return render(request, "ec_system/withdrawCommit.html", context)
    
class DeleteFromCart(View):
    def post(self, request, cart_id):
        login_user = is_login(request)
        if login_user is None:
            return redirect("ec_system:login")

        user_id = request.session.get("user_id")
        cart_item = Itemincart.objects.filter(id = cart_id, user_id = user_id)
        cart_item.delete()
        return redirect("ec_system:cart")
    
class UpdateCart(View):
        def post(self, request, cart_id):
            login_user = is_login(request)
            if login_user is None:
                return redirect("ec_system:login")

            user_id = request.session.get("user_id")
            cart_item = Itemincart.objects.filter(id = cart_id, user_id = user_id)

            amount = int(request.POST["amountForm"])
            if amount <= 0:

                cart_item.delete()
            else:
                cart_item.amount = amount
                cart_item.update(amount=amount)
            return redirect("ec_system:cart")
        
class PurchaseConfirm(View):
    def post(self, request):
        login_user = is_login(request)
        if login_user is None:
            return redirect("ec_system:login")

        user_id = request.session.get("user_id")
        cart_items = Itemincart.objects.filter(user_id=user_id)
        
        if not cart_items.exists():
            return redirect("ec_system:cart")

        total = 0
        for ci in cart_items:
            total += ci.item.price * ci.amount

        context = {
            "login_user": login_user,
            "cart_items": cart_items,
            "total": total,
        }
        return render(request, "ec_system/purchaseConfirm.html", context)
    
class PurchaseCommit(View):
    def post(self, request):
        login_user = is_login(request)
        if login_user is None:
            return redirect("ec_system:login")

        user_id = request.session.get("user_id")
        cart_items = Itemincart.objects.filter(user_id=user_id)

        if not cart_items.exists():
            return redirect("ec_system:cart")

        destination = request.POST.get("destination", "").strip()
        if not destination:
            destination = login_user.address

        with transaction.atomic():
            last_purchase_id = Purchase.objects.aggregate(m=Max("purchase_id"))["m"] or 0
            new_purchase_id = last_purchase_id + 1

            purchase = Purchase.objects.create(
                purchase_id=new_purchase_id,
                destination=destination,
                user=login_user,
            )

            last_detail_id = Purchasedetail.objects.aggregate(m=Max("purchase_detail_id"))["m"] or 0
            next_detail_id = last_detail_id + 1

            for ci in cart_items:
                Purchasedetail.objects.create(
                    purchase_detail_id=next_detail_id,
                    amount=ci.amount,
                    item=ci.item,
                    purchase=purchase,
                )
                next_detail_id += 1

            cart_items.delete()

        context = {
            "login_user": login_user,
            "purchase": purchase,
        }
        return render(request, "ec_system/purchaseCommit.html", context)

