from django.urls import path
from . import views

app_name = "ec_system"

urlpatterns = [
    path('', views.index, name="index"),
    path('searchResult/', views.SearchResult.as_view(), name="search_result"),
    path('login/', views.Login.as_view(), name="login"),
    path('itemDetail/<int:item_id>/', views.Itemdetail.as_view(), name="item_detail"),
    path("cart/add/<int:item_id>/", views.AddToCart.as_view(), name="add_to_cart"),
    path("cart/", views.Cart.as_view(), name="cart"),
    path("logout/", views.Logout.as_view(), name="logout"),
    path("registerUser/", views.RegisterUser.as_view(), name="register_user"),
    path("register/commit/", views.RegisterCommit.as_view(), name="register_commit"),
    path("user/", views.UserInfo.as_view(), name="user_info"),
    path("user/update/", views.UpdateUser.as_view(), name="update_user"),
    path("user/update/commit", views.UpdateUserCommit.as_view(), name="update_user_commit"),
    path("withdrawConfirm/", views.WithDrawConfirm.as_view(), name="withdraw_confirm"),
    path("withdrawCommit/", views.WithDrawCommit.as_view(), name="withdraw_commit"),
    path("cart/delete/<int:cart_id>/", views.DeleteFromCart.as_view(), name="delete_from_cart"),
    path("cart/update/<int:cart_id>/", views.UpdateCart.as_view(), name="update_cart"),
]