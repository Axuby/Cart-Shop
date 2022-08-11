from itertools import product
from math import prod
from time import process_time
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import ListView, DetailView, CreateView
from django.views.generic.base import TemplateView
from cart.models import Cart, CartItem
from django.contrib.auth.decorators import login_required

from store.models import Product, Variation
# Create your views here.


def _get_cart_id(request):  # cart_id  as used as session id
    cart_id = request.session.session_key
    if not cart_id:
        cart_id = request.session.create()
    return cart_id


# def cart_view(request, quantity=0, total=0, cart_items=None):
#     try:
#         cart = Cart.objects.get(cart=_get_cart_id(request))
#         cart_items = CartItem.objects.filter(cart=cart)
#         for cart_item in cart_items:  # instance of cart_item
#             total += (cart_item.product.price * cart_item.quantity)
#             quantity += cart_item.quantity
#     except:
#         pass
#     return render(request, "cart/cart.html", {
#         "quantity": quantity,
#         "total": total,
#         "cart_items": cart_items
#     })


# class CartView(TemplateView):
#     template_name = "cart/cart.html"


class CartView(TemplateView):
    template_name = "cart/cart.html"

    def get_context_data(self, **kwargs):
        total = 0
        quantity = 0
        context = super().get_context_data(**kwargs)
        try:
            if self.request.user.is_authenticated:
                cart_items = CartItem.objects.filter(
                    user=self.request.user, is_active=True)
            else:
                cart = Cart.objects.get(cart_id=_get_cart_id(self.request))
                cart_items = CartItem.objects.filter(cart=cart, is_active=True)
            for cart_item in cart_items:
                quantity += cart_item.quantity
                total += (cart_item.product.price * cart_item.quantity)
            tax = int(0.02 * total)

            grand_total = total + tax
            context["quantity"] = quantity
            context["total"] = total
            context["cart_items"] = cart_items
            context["tax"] = tax
            context["grand_total"] = grand_total
        except ObjectDoesNotExist:
            pass

        return context


def add_to_cart(request, product_id):
    current_user = request.user
    if current_user.is_authenticated:
        # get product by its  variation
        product = Product.objects.get(id=product_id)
        product_by_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]
                variation = Variation.objects.filter(
                    variation_category__iexact=key, variation_value__iexact=value, product=product)
                product_by_variation.append(variation)
                print(variation)

        # get and put product in cart to be CartItem
            does_cart_item_exists = CartItem.objects.filter(
                product=product, user=current_user).exists()

            if does_cart_item_exists:
                cart_item = CartItem.objects.get(
                    product=product, user=current_user)
                existing_variation_list = []
                id = []
                for item in cart_item:
                    existing_variation = item.variations.all()
                    existing_variation_list.append(list(existing_variation))
                    id.append(item.id)
                for prod in product_by_variation:
                    if prod in existing_variation_list:
                        index = existing_variation_list.index(prod)
                        item_id = id[index]

                        item = CartItem.objects.get(
                            product=product, id=item_id)
                        item.quantity += 1
                        item.save()

            else:
                cart_item = CartItem.objects.create(
                    user=current_user, product=product, quantity=1)
                if len(product_by_variation) > 0:
                    cart_item.variations.clear()
                    # cart_item.variations.add(product_by_variation)
                    for item in product_by_variation:
                        cart_item.variations.set(item)
                cart_item.save()
        else:

            cart_item = CartItem.objects.create(user=current_user,
                                                product=product, quantity=1)
            if len(product_by_variation) > 0:
                print(cart_item.variations.clear())
                cart_item.variations.set(product_by_variation)
                # cart_item.variations.add(*product_by_variation)
            cart_item.save()

        return redirect('cart')
    else:
        product = Product.objects.get(id=product_id)
        product_by_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]

                # get product variation instance
                variation = Variation.objects.filter(
                    variation_category=key, variation_value=value, product=product)

                product_by_variation.append(variation)
        # try get the cart
        try:
            cart = Cart.objects.get(cart_id=_get_cart_id(request))

            # create the new cart if it doesn't exist
        except Cart.DoesNotExist:

            cart = Cart.objects.create(cart_id=_get_cart_id(request))
            cart.save()

        # get and put product in cart to be CartItem
        does_cart_item_exists = CartItem.objects.filter(
            product=product, cart=cart).exists()

        if does_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, cart=cart)
        # existing var from DB,current var from product var,
        # and item id from DB
            existing_variation_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variations.all()
                existing_variation_list.append(existing_variation)
                id.append(item.id)

            if product_by_variation in existing_variation_list:
                index = existing_variation_list.index(product_by_variation)
                item_id = id[index]

                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1
                item.save()

            else:
                cart_item = CartItem.objects.create(
                    cart=cart, product=product, quantity=1)

                if len(product_by_variation) > 0:
                    cart_item.variations.clear()

                    cart_item.variations.add(*product_by_variation)
                cart_item.save()
        else:

            cart_item = CartItem.objects.create(
                cart=cart, product=product, quantity=1)
            if len(product_by_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_by_variation)
            cart_item.save()

        return redirect('cart')


def remove_from_cart(request, product_id, cart_item_id):
    if request.user.is_authenticated:
        product = get_object_or_404(Product, id=product_id)
        print(cart_item_id)
        try:
            cart_item = CartItem.objects.get(
                user=request.user, product=product, id=cart_item_id)
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                cart_item.delete()
        except:
            pass
    else:
        cart = Cart.objects.get(cart_id=_get_cart_id(request))
        product = get_object_or_404(Product, id=product_id)
        print(cart_item_id)
        try:
            cart_item = CartItem.objects.get(
                cart=cart, product=product, id=cart_item_id)
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                cart_item.delete()
        except:
            pass
    return redirect('cart')


def remove_cart_item(request, product_id, cart_item_id):

    if request.user.is_authenticated:
        product = get_object_or_404(Product, id=product_id)
        try:
            cart_item = CartItem.objects.get(
                user=request.user, product=product, id=cart_item_id)
            print(isinstance(cart_item, CartItem))
            cart_item.delete()
        except:
            print("Not zFOund")

    else:
        cart = Cart.objects.get(cart_id=_get_cart_id(request))
        product = get_object_or_404(Product, id=product_id)
        try:
            cart_item = CartItem.objects.get(
                cart=cart, product=product, id=cart_item_id)
            print(isinstance(cart_item, CartItem))
            cart_item.delete()
        except:
            print("Not zFOund")

    return redirect('cart')


# def cart(request, total=0, quantity=0, cart_items=None):
#     try:
#         tax = 0
#         grand_total = 0
#         cart = Cart.objects.get(cart_id=_get_cart_id(request))
#         cart_items = CartItem.objects.filter(cart=cart, is_active=True)
#         for cart_item in cart_items:

@login_required(login_url='login')
def checkout(request, total=0, quantity=0, cart_items=None):

    try:
        total = 0
        tax = 0
        grand_total = 0
        cart = Cart.objects.get(cart_id=_get_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            quantity += cart_item.quantity
            total += (cart_item.product.price * cart_item.quantity)

        tax = int(0.02 * total)
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass

    context = {
        "total": total,
        "quantity": quantity,
        "cart_items": cart_items,
        "tax": tax,
        "grand_total": grand_total
    }

    return render(request, "cart/checkout.html", context)
