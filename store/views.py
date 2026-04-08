from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Product, Cart, CartItem, Order, OrderItem
from .forms import ProductForm, CartItemForm


# ─── Autenticación ────────────────────────────────────────────────────────────

def login_view(request):
    if request.user.is_authenticated:
        return redirect('catalog')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        if not username or not password:
            messages.error(request, "Completa todos los campos.")
            return render(request, 'store/login.html')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('catalog')
        else:
            messages.error(request, "Usuario o contraseña incorrectos.")
    return render(request, 'store/login.html')


def logout_view(request):
    logout(request)
    messages.success(request, "Sesión cerrada correctamente.")
    return redirect('login')


# ─── Catálogo ─────────────────────────────────────────────────────────────────

@login_required
def catalog(request):
    category = request.GET.get('category', '')
    products = Product.objects.filter(active=True)
    if category in ['fruta', 'verdura']:
        products = products.filter(category=category)
    cart_count = 0
    if hasattr(request.user, 'cart'):
        cart_count = request.user.cart.get_item_count()
    return render(request, 'store/catalog.html', {
        'products': products,
        'selected_category': category,
        'cart_count': cart_count,
    })


@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk, active=True)
    form = CartItemForm()
    cart_count = 0
    if hasattr(request.user, 'cart'):
        cart_count = request.user.cart.get_item_count()
    return render(request, 'store/product_detail.html', {
        'product': product,
        'form': form,
        'cart_count': cart_count,
    })


# ─── Carrito ──────────────────────────────────────────────────────────────────

def _get_or_create_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart


@login_required
def cart_view(request):
    cart = _get_or_create_cart(request.user)
    return render(request, 'store/cart.html', {'cart': cart})


@login_required
def cart_add(request, pk):
    product = get_object_or_404(Product, pk=pk, active=True)
    if request.method == 'POST':
        form = CartItemForm(request.POST)
        if form.is_valid():
            qty = form.cleaned_data['quantity']
            if qty > product.stock:
                messages.error(request, f"Solo hay {product.stock} unidades disponibles de {product.name}.")
                return redirect('product_detail', pk=pk)
            cart = _get_or_create_cart(request.user)
            item, created = CartItem.objects.get_or_create(cart=cart, product=product)
            if not created:
                new_qty = item.quantity + qty
                if new_qty > product.stock:
                    messages.error(request, f"No puedes agregar más de {product.stock} unidades de {product.name}.")
                    return redirect('cart')
                item.quantity = new_qty
            else:
                item.quantity = qty
            item.save()
            messages.success(request, f"{product.name} agregado al carrito.")
        else:
            messages.error(request, "Cantidad inválida.")
    return redirect('cart')


@login_required
def cart_update(request, item_id):
    item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
    if request.method == 'POST':
        form = CartItemForm(request.POST)
        if form.is_valid():
            qty = form.cleaned_data['quantity']
            if qty > item.product.stock:
                messages.error(request, f"Solo hay {item.product.stock} unidades disponibles.")
            else:
                item.quantity = qty
                item.save()
                messages.success(request, "Cantidad actualizada.")
        else:
            messages.error(request, "Cantidad inválida.")
    return redirect('cart')


@login_required
def cart_remove(request, item_id):
    item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
    product_name = item.product.name
    item.delete()
    messages.success(request, f"{product_name} eliminado del carrito.")
    return redirect('cart')


# ─── Checkout / Orden ─────────────────────────────────────────────────────────

@login_required
def checkout_confirm(request):
    cart = _get_or_create_cart(request.user)
    if not cart.items.exists():
        messages.error(request, "Tu carrito está vacío.")
        return redirect('cart')
    return render(request, 'store/checkout_confirm.html', {'cart': cart})


@login_required
def checkout_complete(request):
    if request.method != 'POST':
        return redirect('cart')
    cart = _get_or_create_cart(request.user)
    if not cart.items.exists():
        messages.error(request, "Tu carrito está vacío.")
        return redirect('cart')

    for item in cart.items.all():
        if item.quantity > item.product.stock:
            messages.error(request, f"Stock insuficiente para {item.product.name}.")
            return redirect('cart')

    total = cart.get_total()
    order = Order.objects.create(user=request.user, total=total)
    for item in cart.items.all():
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price,
        )
        item.product.stock -= item.quantity
        item.product.save()

    cart.items.all().delete()
    messages.success(request, f"¡Orden #{order.id} confirmada con éxito!")
    return redirect('order_success', order_id=order.id)


@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    return render(request, 'store/order_success.html', {'order': order})


# ─── Admin de productos ───────────────────────────────────────────────────────

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_staff:
            messages.error(request, "No tienes permiso para acceder a esta sección.")
            return redirect('catalog')
        return view_func(request, *args, **kwargs)
    return wrapper


@admin_required
def admin_products(request):
    products = Product.objects.all().order_by('category', 'name')
    return render(request, 'store/admin_products.html', {'products': products})


@admin_required
def admin_product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Producto creado exitosamente.")
            return redirect('admin_products')
    else:
        form = ProductForm()
    return render(request, 'store/admin_product_form.html', {'form': form, 'action': 'Crear'})


@admin_required
def admin_product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Producto actualizado.")
            return redirect('admin_products')
    else:
        form = ProductForm(instance=product)
    return render(request, 'store/admin_product_form.html', {'form': form, 'action': 'Editar', 'product': product})


@admin_required
def admin_product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, "Producto eliminado.")
        return redirect('admin_products')
    return render(request, 'store/admin_product_confirm_delete.html', {'product': product})
