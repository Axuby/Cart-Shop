from django.urls import path
from . import views


urlpatterns = [
    path('', views.ProductsListAV.as_view(), name='store'),
    path('category/<slug:category_slug>/', views.ProductsListAV.as_view(),
         name='products_by_category'),
    path('category/<slug:category_slug>/<slug:product_slug>/', views.ProductDetailAV.as_view(),
         name='product-detail'),
    # path('search/', views.search, name="search"),
]
