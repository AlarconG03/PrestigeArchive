from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import CartClearView
from . import views

urlpatterns = [
    # Páginas principales (pages)
    path('', views.HomeView.as_view(), name='home'),
    path('products/', views.ProductListView.as_view(), name='products'),
    path('products/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('search/', views.SearchView.as_view(), name='search'),
    
    #API clima
    path('weather/search/', views.WeatherSearchView.as_view(), name='weather_search'),

    # Autenticación (auth)
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    
    # Perfil de usuario (user_profile)
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/password/', views.CustomPasswordChangeView.as_view(), name='password_change'),
    
    # Pedidos(orders)
    path('my-orders/', views.OrderListView.as_view(), name='my_orders'),
    path('my-orders/<int:order_id>/', views.OrderDetailView.as_view(), name='order_detail'),
    
    # Favoritos(user_fav)
    path('favorites/', views.FavoriteListView.as_view(), name='favorites'),
    path('favorites/toggle/', views.FavoriteToggleView.as_view(), name='favorite_toggle'),
    
    # Direcciones(user_address)
    path('addresses/', views.AddressListView.as_view(), name='addresses'),
    path('addresses/add/', views.AddressCreateView.as_view(), name='address_add'),
    path('addresses/<int:pk>/edit/', views.AddressUpdateView.as_view(), name='address_edit'),
    path('addresses/<int:pk>/delete/', views.AddressDeleteView.as_view(), name='address_delete'),
    path('addresses/<int:pk>/default/', views.AddressSetDefaultView.as_view(), name='address_set_default'),
    
    # Carrito(cart)
    path('cart/', views.CartView.as_view(), name='cart'),
    path('cart/add/', views.CartAddView.as_view(), name='cart_add'),
    path('cart/update/', views.CartUpdateView.as_view(), name='cart_update'),
    path('cart/remove/', views.CartRemoveView.as_view(), name='cart_remove'),
    path('cart/clear/', CartClearView.as_view(), name='cart_clear'),
    
    # Checkout(checkout)
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('checkout/create-order/', views.OrderCreateView.as_view(), name='create_order'),
    path('order-confirmation/<int:order_id>/', views.OrderConfirmationView.as_view(), name='order_confirmation'),
    
    # Newsletter
    path('newsletter/subscribe/', views.NewsletterSubscribeView.as_view(), name='newsletter_subscribe'),
    
    # Administración
    path('admin/dashboard/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('admin/products/', views.AdminProductListView.as_view(), name='admin_products'),
    path('admin/products/create/', views.AdminProductCreateView.as_view(), name='admin_product_create'),
    path('admin/products/<int:pk>/edit/', views.AdminProductUpdateView.as_view(), name='admin_product_edit'),
    path('admin/products/<int:pk>/delete/', views.AdminProductDeleteView.as_view(), name='admin_product_delete'),
    path('admin/orders/', views.AdminOrderListView.as_view(), name='admin_orders'),
    path('admin/orders/<int:order_id>/', views.AdminOrderDetailView.as_view(), name='admin_order_detail'),
    path('admin/users/', views.AdminUserListView.as_view(), name='admin_users'),
]