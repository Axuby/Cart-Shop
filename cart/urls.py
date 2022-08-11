from django.urls import path
from . import views
urlpatterns = [
    path('', views.CartView.as_view(), name='cart'),
    path('add-cart/<int:product_id>/', views.add_to_cart, name="add-to-cart"),
    path('reduce-cart/<int:product_id>/<int:cart_item_id>/',
         views.remove_from_cart, name="remove-from-cart"),
    path('delete-cart-item/<int:product_id>/<int:cart_item_id>/',
         views.remove_cart_item, name="delete-cart"),

    path('checkout/', views.checkout, name="checkout")
]
