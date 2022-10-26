from . import views
from django.urls import path
urlpatterns = [
    path('', views.CategoryAV.as_view(), name='categories')
]
