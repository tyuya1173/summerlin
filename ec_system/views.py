from django.shortcuts import render
from django.shortcuts import redirect
from django.views.generic import View
from ec_system.models import Account, Category, Item, Itemincart, Purchase, Purchasedetail, Admin, Payment
from . import forms
from django.db import transaction
from django.db.models import Max, Sum, Q
from django.shortcuts import get_object_or_404
import json
import urllib.request
import urllib.error
from django.conf import settings

def is_login(request):
    user_id = request.session.get("user_id")
    if user_id:
        login_user = Account.objects.filter(user_id=user_id).first()
    else:
        login_user = None

    return login_user

def is_admin(request):
    admin_id = request.session.get("admin_id")
    if admin_id:
        return Admin.objects.filter(admin_id=admin_id).first()
    return None

def cancel_purchase(purchase):
    if purchase.cancel:
        return

    with transaction.atomic():
        details = Purchasedetail.objects.filter(purchase=purchase)
        for detail in details:
            detail.item.stock += detail.amount
            detail.item.save()
        purchase.cancel = True
        purchase.save()

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

        for ci in cart_items:
            if ci.amount > ci.item.stock:
                context = {
                    "cart_items": cart_items,
                    "error": f"「{ci.item.name}」は在庫が不足しています(在庫：{ci.item.stock})",
                }
                return render(request, "ec_system/cart.html", context)

        total = sum(ci.item.price * ci.amount for ci in cart_items)
        pay = request.POST.get("pay", "cod")

        # カード払いのときだけ決済APIを呼ぶ
        result = None
        if pay == "card":
            payload = {
                "amount": total,
                "currency": "JPY",
                "card_number": request.POST.get("card_number", ""),
                "description": f"user:{user_id}",
            }
            if request.POST.get("card_holder"):
                payload["card_holder"] = request.POST["card_holder"]
            if request.POST.get("card_exp_month"):
                payload["card_exp_month"] = request.POST["card_exp_month"]
            if request.POST.get("card_exp_year"):
                payload["card_exp_year"] = request.POST["card_exp_year"]
            if request.POST.get("card_cvc"):
                payload["card_cvc"] = request.POST["card_cvc"]

            error_message = None
            req = urllib.request.Request(
                f"{settings.PAYMENT_API_BASE}/payments/charge",
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "X-API-Key": settings.PAYMENT_API_KEY,
                    "Content-Type": "application/json",
                },
                method="POST",
            )
            try:
                with urllib.request.urlopen(req, timeout=settings.PAYMENT_API_TIMEOUT) as res:
                    body = json.loads(res.read().decode("utf-8"))
                if body.get("status") == "succeeded":
                    result = body
                else:
                    error_message = body.get("error", {}).get("message", "決済に失敗しました")
            except urllib.error.HTTPError as e:
                try:
                    err = json.loads(e.read().decode("utf-8")).get("error", {})
                    error_message = err.get("message", "決済リクエストに失敗しました")
                except Exception:
                    error_message = "決済リクエストに失敗しました"
            except urllib.error.URLError:
                error_message = "決済サーバーに接続できませんでした"

            if error_message:
                context = {
                    "login_user": login_user,
                    "cart_items": cart_items,
                    "total": total,
                    "payment_error": error_message,
                }
                return render(request, "ec_system/purchaseConfirm.html", context)

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
                ci.item.stock -= ci.amount
                ci.item.save()
                next_detail_id += 1

            cart_items.delete()

            if result is not None:
                Payment.objects.create(
                    purchase=purchase,
                    transaction_id=result["transaction_id"],
                    card_last4=result.get("card_last4"),
                    amount=total,
                    currency="JPY",
                    status=result.get("status", "succeeded"),
                )

        context = {
            "login_user": login_user,
            "purchase": purchase,
        }
        return render(request, "ec_system/purchaseCommit.html", context)
    
class PurchaseHistory(View):
    def get(self, request):
        login_user = is_login(request)
        if login_user is None:
            return redirect("ec_system:login")

        purchases = Purchase.objects.filter(user=login_user).order_by("-booked_date")

        context = {
            "login_user": login_user,
            "purchases": purchases,
        }
        return render(request, "ec_system/purchaseHistory.html", context)
        
class AdminLogin(View):
    def get(self, request):
        form = forms.AdminLoginForm()
        context = {
            'form': form,
        }
        return render(request, 'ec_system/adminLogin.html', context)
    
    def post(self, request):
        form = forms.AdminLoginForm(request.POST)
        if form.is_valid():
            request.session["admin_id"] = form.admin.admin_id
            return redirect("ec_system:admin_top")
        context = {
            'form': form,
        }
        return render(request, "ec_system/login.html", context)
    
class AdminTop(View):
    def get(self, request):
        login_administrator = is_admin(request)

        if login_administrator is None:
            return redirect("ec_system:admin_login")
        
        return render(request, "ec_system/adminTop.html")
    
class AdminItemSearch(View):
    def get(self, request):
        queryset = Item.objects.all()

        context = {
            'item': queryset
        }
        return render(request, 'ec_system/adminItemSearch.html', context)
    
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
            'category': category,
            'keyword': keyword,
            'item': queryset
        }
        return render(request, 'ec_system/adminItemSearch.html', context)
    
class AdminItemRegister(View):
    def get(self, request):
        if is_admin(request) is None:
            return redirect("ec_system:admin_login")
        form = forms.ItemForm()
        context = {
            'form': form,
            'mode': 'register'
        }
        return render(request, "ec_system/adminItemForm.html",context)

    def post(self, request):
        if is_admin(request) is None:
            return redirect("ec_system:admin_login")
        form = forms.ItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            last_id = Item.objects.aggregate(m=Max("item_id"))["m"] or 0
            item.item_id = last_id + 1
            item.save()
            return redirect("ec_system:admin_item_search")
        
        context = {
            'form': form,
            'mode': 'register'
        }
        return render(request, "ec_system/adminItemForm.html",context)


class AdminItemEdit(View):
    def get(self, request, item_id):
        if is_admin(request) is None:
            return redirect("ec_system:admin_login")
        item = get_object_or_404(Item, pk=item_id)
        form = forms.ItemForm(instance=item)
        context = {
            'form': form,
            'mode': 'edit',
            'item': item,
        }
        return render(request, "ec_system/adminItemForm.html",context)

    def post(self, request, item_id):
        if is_admin(request) is None:
            return redirect("ec_system:admin_login")
        item = get_object_or_404(Item, pk=item_id)
        form = forms.ItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect("ec_system:admin_item_search")
        context = {
            'form': form,
            'mode': 'edit',
            'item': item
        }
        return render(request, "ec_system/adminItemForm.html", context)


class AdminItemDelete(View):
    def post(self, request, item_id):
        if is_admin(request) is None:
            return redirect("ec_system:admin_login")
        item = get_object_or_404(Item, pk=item_id)
        item.delete()
        return redirect("ec_system:admin_item_search")
    
class Ranking(View):
    def get(self, request):
        items = Item.objects.annotate(total_sold=Sum("purchasedetail__amount", filter=Q(purchasedetail__purchase__cancel=False))).filter(total_sold__isnull=False).order_by('-total_sold')[:3]
        context={
            'items':items
        }
        return render(request, "ec_system/ranking.html", context)
    
class AdminPurchaseSearch(View):
    def get(self, request):
        if is_admin(request) is None:
            return redirect("ec_system:admin_login")
        purchases = Purchase.objects.all().order_by("-booked_date")
        context = {
            "purchases": purchases,
            "status": "all"
        }
        return render(request, "ec_system/adminPurchaseSearch.html", context)

    def post(self, request):
        if is_admin(request) is None:
            return redirect("ec_system:admin_login")

        keyword = request.POST.get("keyword", "").strip()
        status = request.POST.get("status", "all")

        purchases = Purchase.objects.all().order_by("-booked_date")
        if keyword:
            purchases = purchases.filter(
                Q(user__user_id__icontains=keyword) | Q(destination__icontains=keyword)
            )
        if status == "active":
            purchases = purchases.filter(cancel=False)
        elif status == "cancelled":
            purchases = purchases.filter(cancel=True)

        context = {
            "purchases": purchases,
            "keyword": keyword,
            "status": status,
        }
        return render(request, "ec_system/adminPurchaseSearch.html", context)

class AdminPurchaseCancel(View):
    def post(self, request, purchase_id):
        if is_admin(request) is None:
            return redirect("ec_system:admin_login")
        purchase = get_object_or_404(Purchase, pk=purchase_id)
        cancel_purchase(purchase)
        return redirect("ec_system:admin_purchase_search")

class PurchaseCancel(View):
    def post(self, request, purchase_id):
        login_user = is_login(request)
        if login_user is None:
            return redirect("ec_system:login")

        purchase = get_object_or_404(Purchase, pk=purchase_id, user=login_user)
        cancel_purchase(purchase)
        return redirect("ec_system:purchase_history")