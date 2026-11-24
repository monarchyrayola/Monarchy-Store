from django.shortcuts import render
from .models import Product, Category
from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib import messages
from django.urls import reverse
from .models import Product, Order, OrderItem
from .models import Order


def product_list(request):
    products = Product.objects.all().order_by('-created_at')
    categories = Category.objects.all()

    query = request.GET.get('q')

    if query:
        products = products.filter(name__icontains=query)

    category_id = request.GET.get('category')

    if category_id:
        products = products.filter(category_id=category_id)

    context = {
        'products': products,
        'categories': categories,
    }

    return render(request, 'products/product_list.html', context)

def product_detail(request, id):
    product = get_object_or_404(Product, id=id)

    colors = product.colors.prefetch_related('images').all()

    return render(
        request,
        'products/product_detail.html',
        {
            'product': product,
            'colors': colors,
        }
    )

def add_to_cart(request, id):
    product = get_object_or_404(Product, id=id)

    if request.method == 'POST':
        cart = request.session.get('cart', {})

        product_id = str(product.id)
        quantity = int(request.POST.get('quantity', 1))

        if quantity < 1 or quantity > product.quantity:
            return redirect('product_detail', id=id)

        current_quantity = cart.get(product_id, 0)

        if current_quantity + quantity <= product.quantity:
            cart[product_id] = current_quantity + quantity

        request.session['cart'] = cart

    return redirect('cart')

def cart_view(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0

    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=int(product_id))
        except (Product.DoesNotExist, ValueError):
            continue

        subtotal = product.price * quantity
        total += subtotal

        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal,
        })

    context = {
        'cart_items': cart_items,
        'total': total,
    }

    return render(request, 'products/cart.html', context)

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('product_list')
    else:
        form = UserCreationForm()

    return render(request, 'products/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect('product_list')

    return render(request, 'products/login.html')

def logout_view(request):
    logout(request)
    return redirect('product_list')

@login_required
def checkout_view(request):

    cart = request.session.get('cart', {})

    if not cart:
        messages.warning(request, "Your cart is empty.")
        return redirect('cart')

    cart_items = []
    total = 0

    for product_id, quantity in cart.items():

        try:
            product = Product.objects.get(id=int(product_id))
            quantity = int(quantity)

            if quantity < 1 or quantity > product.quantity:
                messages.error(
                    request,
                    f"Insufficient stock for {product.name}."
                )
                return redirect('cart')

        except (Product.DoesNotExist, ValueError):
            messages.error(request, "Invalid cart item.")
            return redirect('cart')

        subtotal = product.price * quantity
        total += subtotal

        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal,
        })

    if request.method == 'POST':

        full_name = request.POST.get('full_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()

        if not full_name or not phone or not address:
            messages.error(request, "Please fill all fields.")
        else:

            with transaction.atomic():

                order = Order.objects.create(
                    user=request.user,
                    full_name=full_name,
                    phone=phone,
                    address=address,
                    total_amount=total
                )

                for item in cart_items:

                    product = Product.objects.select_for_update().get(
                        id=item['product'].id
                    )

                    if product.quantity < item['quantity']:
                        messages.error(
                            request,
                            f"Not enough stock for {product.name}."
                        )
                        raise ValueError("Insufficient stock")

                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=item['quantity'],
                        price=product.price
                    )

                    product.quantity -= item['quantity']
                    product.save()

            request.session['cart'] = {}

            return redirect('order_success', id=order.id)

    context = {
        'cart_items': cart_items,
        'total': total,
    }

    return render(request, 'products/checkout.html', context)

@login_required
def order_success(request, id):

    order = get_object_or_404(
        Order,
        id=id,
        user=request.user
    )

    return render(
        request,
        'products/order_success.html',
        {'order': order}
    )

@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'products/my_orders.html', {
        'orders': orders
    })

@login_required
def order_detail(request, id):
    order = get_object_or_404(
        Order,
        id=id,
        user=request.user
    )

    return render(request, 'products/order_detail.html', {
        'order': order
    })
