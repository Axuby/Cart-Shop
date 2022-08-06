from cart.views import _get_cart_id
from store.models import Product
from unicodedata import category
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.generic.base import TemplateView
from django.views import View
from django.views.generic import DetailView, ListView, UpdateView, CreateView
from cart.models import CartItem
from category.models import Category
from django.db.models import Q


# Create your views here.


class StoreListView(ListView):
    template_name = "store/store.html"
    model = Product
    context_object_name = "products"

    def get_context_data(self, **kwargs):
        context = super(StoreListView, self).get_context_data(**kwargs)
        if self.kwargs.get("category_slug") != None:
            categories = get_object_or_404(
                Category, slug=self.kwargs["category_slug"])
            products = Product.objects.filter(
                category=categories, is_available=True).order_by('id')
            paginator = Paginator(products, 3)
            page = self.request.GET.get('page')
            paged_product = paginator.get_page(page)
            product_count = products.count()
            context["products"] = paged_product
            context["product_count"] = product_count
            # cat_products = Category.objects.get(slug=category_slug).products.all()
        else:

            products = Product.objects.all().order_by('id')
            paginator = Paginator(products, 3)
            # url that comes with page number ?page=
            page = self.request.GET.get('page')
            paged_product = paginator.get_page(page)
            product_count = products.count()
        #  context["products"] = products
        context["products"] = paged_product
        context["product_count"] = product_count

        return context


def store(request, category_slug=None):
    categories = None
    products = None
    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(
            category=categories, is_available=True)
        product_count = products.count()
        context = {
            "products": products,
            "product_count": product_count,
        }

    else:
        products = Product.objects.all()
        product_count = products.count()
        context = {
            "products": products,
            "product_count": product_count,
        }

    return render(request, 'store/store.html', context)


def product_detail(request, category_slug, product_slug):

    try:
        product = Product.objects.get(
            category__slug=category_slug, slug=product_slug)
        is_in_cart = CartItem.objects.filter(
            cart__cart_id=_get_cart_id(request), product=product).exists()
    except Exception as e:
        pass

    context = {
        "product": product,
        "is_in_cart": is_in_cart,
    }

    return render(request, 'store/product_detail.html', context)


class ProductDetailView(DetailView):
    template_name = 'store/product_detail.html'
    model = Product
    context_object_name = "product"

    def get_object(self):
        product = Product.objects.get(
            category__slug=self.kwargs["category_slug"], slug=self.kwargs["product_slug"])
        # print(list(product.variation_set.colors()))
        # print(product.variation_set.colors, 1)
        # for i in product.variation_set.colors():
        #     print(i.variation_value)
        # for i in product.variation_set.size():
        #     print(i.variation_value)
    # is_in_cart = CartItem.objects.get(
    #     cart__cart_id=_get_cart_id(self.request), product=product).exists()

        return product

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # product = Product.objects.get(
        #     category__slug=self.object.get("category_slug"), slug=self.object.get("product_slug"))
        # is_in_cart = CartItem.objects.get(
        #     cart__cart_id=_get_cart_id(self.request), product=product).exists()
        print(context.get(self.context_object_name))
        context["is_in_cart"] = CartItem.objects.filter(
            cart__cart_id=_get_cart_id(self.request), product=context.get(self.context_object_name)).exists()

        return context


def search(request):
    if request.method == "GET" and "keyword" in request.GET:
        keyword = request.GET.get('keyword')  # request.GET['keyword]
        if keyword:
            products = Product.objects.order_by(
                '-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword) | Q(category__category_name=keyword))
            product_count = products.count()
            context = {
                "products": products,
                "product_count": product_count,
            }
    return render(request, 'store/store.html', context)
