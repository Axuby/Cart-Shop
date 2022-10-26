from pyexpat import model
from unicodedata import category
from category.api.serializers import CategorySerializer
from category.models import Category
from rest_framework import serializers
from ..models import Product, Variation


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = "__all__"


class ProductByCategorySerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = Product
        fields = "__all__"
