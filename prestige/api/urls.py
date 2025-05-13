from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'products', views.ProductViewSet, basename='product')

urlpatterns = [
    path('', views.api_root, name='api-root'),
    path('', include(router.urls)),
    path('products-in-stock/', views.products_in_stock, name='products-in-stock'),
    path('docs/', views.api_documentation, name='api-docs'),
]
