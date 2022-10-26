from unicodedata import category
from category.models import Category
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from ..models import Product, Variation
from .serializers import ProductByCategorySerializer, ProductSerializer


class ProductsListAV(ListAPIView):
    queryset = Product.objects.select_related("category")
    serializer_class = ProductSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        slug = self.kwargs.get("category_slug")
        if slug is not None:
            return qs.filter(category__category_name=slug)

        return qs

    # def get(self, request, *args, **kwargs):
    #     products = self.queryset.all()
    #     print(products)
    #     serializers = self.serializer_class(
    #         products, many=True, context={'request': request})
    #     print(request.user)
    #     return Response(serializers.data)


class ProductDetailAV(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get(self, request, *args, **kwargs):
        cat_slug = self.kwargs.get("category_slug")
        prod_slug = self.kwargs.get("product_slug")
        product = Product.objects.get(
            category__category_name=cat_slug, slug=prod_slug)
        serializer = self.serializer_class(product)
        return Response(serializer.data)


class SearchAV(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_queryset(self):
        qs = super().get_queryset()

        q = self.request.GET("q")
        results = Product.objects.none()
        if q is not None:
            user = None
            if self.request.user.is_authenticated:
                user = self.request.user
            results = qs.search(q, user=user)

        return results
