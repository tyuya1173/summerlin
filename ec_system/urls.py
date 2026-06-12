from django.urls import path
from . import views

app_name = "ec_system"

urlpatterns = [
    path('', views.index, name="index"),
    path('searchResult/', views.SearchResult.as_view(), name="search_result"),
    path('login/', views.Login.as_view(), name="login"),
    path('itemDetail/<int:item_id>/', views.Itemdetail.as_view(), name="item_detail")
]