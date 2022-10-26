from category.models import Category
from rest_framework.generics import ListAPIView
from .serializers import CategorySerializer


class CategoryAV(ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
