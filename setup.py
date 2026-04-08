"""
Script de configuración inicial:
- Aplica migraciones
- Crea superusuario (admin)
- Crea usuario cliente
- Carga productos de prueba
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from django.core.management import call_command
from django.contrib.auth.models import User

print("=== Aplicando migraciones ===")
call_command('migrate', verbosity=1)

print("\n=== Creando usuarios ===")

if not User.objects.filter(username='superadmin').exists():
    User.objects.create_superuser('superadmin', 'superadmin@frutas.cl', 'superadmin123')
    print("  [OK] Superadmin creado: superadmin / superadmin123")
else:
    print("  [--] Superadmin ya existe")

if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@frutas.cl', 'admin123')
    print("  [OK] Admin creado: admin / admin123")
else:
    print("  [--] Admin ya existe")

if not User.objects.filter(username='cliente').exists():
    User.objects.create_user('cliente', 'cliente@frutas.cl', 'cliente123')
    print("  [OK] Cliente creado: cliente / cliente123")
else:
    print("  [--] Cliente ya existe")

print("\n=== Cargando productos ===")
call_command('loaddata', 'store/fixtures/productos.json', verbosity=1)

print("\n=== Listo! Ejecuta: python manage.py runserver ===")
print("  Abre: http://127.0.0.1:8000/")
print("  Superadmin: superadmin / superadmin123")
print("  Admin: admin / admin123")
print("  Cliente: cliente / cliente123")
