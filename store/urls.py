from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Catálogo
    path('catalogo/', views.catalog, name='catalog'),
    path('producto/<int:pk>/', views.product_detail, name='product_detail'),

    # Carrito
    path('carrito/', views.cart_view, name='cart'),
    path('carrito/agregar/<int:pk>/', views.cart_add, name='cart_add'),
    path('carrito/actualizar/<int:item_id>/', views.cart_update, name='cart_update'),
    path('carrito/eliminar/<int:item_id>/', views.cart_remove, name='cart_remove'),

    # Checkout
    path('checkout/', views.checkout_confirm, name='checkout_confirm'),
    path('checkout/confirmar/', views.checkout_complete, name='checkout_complete'),
    path('orden/<int:order_id>/exito/', views.order_success, name='order_success'),

    # Admin productos
    path('admin-productos/', views.admin_products, name='admin_products'),
    path('admin-productos/crear/', views.admin_product_create, name='admin_product_create'),
    path('admin-productos/editar/<int:pk>/', views.admin_product_edit, name='admin_product_edit'),
    path('admin-productos/eliminar/<int:pk>/', views.admin_product_delete, name='admin_product_delete'),
]
