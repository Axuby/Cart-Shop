try:
        if

        # cart_item = CartItem.objects.filter(
        #     variations__variation_category=value)
        # print(cart_item)
        if not cart_item.exists():
            cart_item = CartItem.objects.create(
                cart=cart, product=product, quantity=1)
        else:
            # if cart_item.variations not in product_by_variation:
            # cart_item.variations.add(item)
            # cart_item.quantity += 1

            if len(product_by_variation) > 0:
                cart_item.variations.clear()
                # for item in product_by_variation:
                # cart_item.variations.add(item)
                # cart_item.quantity += 1
            cart_item.save()
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
            cart=cart, product=product, quantity=1)
        if len(product_by_variation) > 0:
            # cart_item.variations.clear()
            for item in product_by_variation:
                cart_item.variations.add(item)
            cart_item.save()

    return redirect('cart')