from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, FormView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib import messages
from django.db.models import Count, Sum, Q, F
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models.functions import TruncDay, TruncMonth
from django.utils import timezone
from datetime import timedelta
import json
from django.utils.safestring import mark_safe
from .models import Product, ShoppingCart, CartItem, Order, OrderItem, Payment, OrderStatus, Newsletter, Favorite, Address
from .forms import UserRegisterForm, UserLoginForm, UserUpdateForm, AddressForm, NewsletterForm
from django.contrib.auth import get_user_model
User = get_user_model()

# Vista de inicio
class HomeView(ListView):
    model = Product
    template_name = 'pages/home.html'
    context_object_name = 'products'
    
    def get_queryset(self):
        # Obtener los 5 productos más vendidos
        top_products = Product.objects.annotate(
            total_sold=Sum('orderitem__quantity')
        ).order_by('-total_sold')[:5]
        
        # Si no hay suficientes productos vendidos, completar con productos recientes
        if top_products.count() < 5:
            product_ids = top_products.values_list('id', flat=True)
            additional_products = Product.objects.exclude(
                id__in=product_ids
            ).order_by('-id')[:5-top_products.count()]
            
            # Combinar los queryset
            top_products = list(top_products) + list(additional_products)
        
        return top_products
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['newsletter_form'] = NewsletterForm()
        return context

# Vista de productos
class ProductListView(ListView):
    model = Product
    template_name = 'pages/products.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Product.objects.all()
        
        # Filtrar por categoría
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        # Filtrar por precio
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # Ordenar
        sort = self.request.GET.get('sort', 'name')
        if sort == 'name':
            queryset = queryset.order_by('name')
        elif sort == 'name_desc':
            queryset = queryset.order_by('-name')
        elif sort == 'price_asc':
            queryset = queryset.order_by('price')
        elif sort == 'price_desc':
            queryset = queryset.order_by('-price')
        elif sort == 'newest':
            queryset = queryset.order_by('-id')
        
        # Búsqueda
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(description__icontains=search) |
                Q(category__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener todas las categorías para el filtro
        context['categories'] = Product.objects.values_list('category', flat=True).distinct()
        
        # Parámetros actuales para mantener los filtros
        context['current_category'] = self.request.GET.get('category', '')
        context['current_min_price'] = self.request.GET.get('min_price', '')
        context['current_max_price'] = self.request.GET.get('max_price', '')
        context['current_sort'] = self.request.GET.get('sort', 'name')
        context['current_search'] = self.request.GET.get('search', '')
        
        # Favoritos del usuario
        if self.request.user.is_authenticated:
            context['favorites'] = Favorite.objects.filter(
                user=self.request.user
            ).values_list('product_id', flat=True)
        
        return context

# Vista de detalle de producto
class ProductDetailView(DetailView):
    model = Product
    template_name = 'pages/product_detail.html'
    context_object_name = 'product'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Productos relacionados (misma categoría)
        context['related_products'] = Product.objects.filter(
            category=self.object.category
        ).exclude(id=self.object.id).order_by('?')[:4]
        
        # Verificar si el producto está en favoritos
        if self.request.user.is_authenticated:
            context['is_favorite'] = Favorite.objects.filter(
                user=self.request.user, 
                product=self.object
            ).exists()
        
        return context

# Vistas de autenticación
class CustomLoginView(LoginView):
    template_name = 'auth/login.html'
    form_class = UserLoginForm
    redirect_authenticated_user = True
    
    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse_lazy('home')
    
    def form_valid(self, form):
        messages.success(self.request, 'Has iniciado sesión correctamente.')
        return super().form_valid(form)

class RegisterView(FormView):
    template_name = 'auth/register.html'
    form_class = UserRegisterForm
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        user = form.save()
        messages.success(self.request, 'Cuenta creada correctamente. Ahora puedes iniciar sesión.')
        return super().form_valid(form)
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

# Vistas de perfil de usuario
class ProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'user_profile/profile.html'
    success_url = reverse_lazy('profile')
    
    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, 'Perfil actualizado correctamente.')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_tab'] = 'profile'
        return context

class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'auth/password_change.html'
    success_url = reverse_lazy('profile')
    
    def form_valid(self, form):
        messages.success(self.request, 'Contraseña actualizada correctamente.')
        return super().form_valid(form)

# Vistas de pedidos
class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'orders/my_orders.html'
    context_object_name = 'orders'
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_tab'] = 'orders'
        return context

class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'orders/order_detail.html'
    context_object_name = 'order'
    slug_field = 'order_id'
    slug_url_kwarg = 'order_id'
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order_items'] = OrderItem.objects.filter(order=self.object).select_related('product')
        context['active_tab'] = 'orders'
        return context

# Vistas de favoritos
class FavoriteListView(LoginRequiredMixin, ListView):
    model = Favorite
    template_name = 'user_fav/favorites.html'
    context_object_name = 'favorites'
    
    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user).select_related('product').order_by('-date_added')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_tab'] = 'favorites'
        return context

class FavoriteToggleView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        
        favorite, created = Favorite.objects.get_or_create(
            user=request.user,
            product=product
        )
        
        if not created:
            favorite.delete()
            is_favorite = False
            message = 'Producto eliminado de favoritos'
        else:
            is_favorite = True
            message = 'Producto añadido a favoritos'
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'is_favorite': is_favorite,
                'message': message
            })
        
        messages.success(request, message)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('home')))

# Vistas de direcciones
class AddressListView(LoginRequiredMixin, ListView):
    model = Address
    template_name = 'user_address/addresses.html'
    context_object_name = 'addresses'
    
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user).order_by('-is_default', 'name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_tab'] = 'addresses'
        return context

class AddressCreateView(LoginRequiredMixin, CreateView):
    model = Address
    form_class = AddressForm
    template_name = 'user_address/address_form.html'
    success_url = reverse_lazy('addresses')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Dirección añadida correctamente.')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_tab'] = 'addresses'
        context['title'] = 'Añadir Dirección'
        return context

class AddressUpdateView(LoginRequiredMixin, UpdateView):
    model = Address
    form_class = AddressForm
    template_name = 'user_address/address_form.html'
    success_url = reverse_lazy('addresses')
    
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, 'Dirección actualizada correctamente.')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_tab'] = 'addresses'
        context['title'] = 'Editar Dirección'
        return context

class AddressDeleteView(LoginRequiredMixin, DeleteView):
    model = Address
    template_name = 'user_address/address_confirm_delete.html'
    success_url = reverse_lazy('addresses')
    
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Dirección eliminada correctamente.')
        return super().delete(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_tab'] = 'addresses'
        return context

class AddressSetDefaultView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        address_id = kwargs.get('pk')
        address = get_object_or_404(Address, id=address_id, user=request.user)
        
        # Desmarcar todas las direcciones como predeterminadas
        Address.objects.filter(user=request.user, is_default=True).update(is_default=False)
        
        # Marcar esta dirección como predeterminada
        address.is_default = True
        address.save()
        
        messages.success(request, 'Dirección predeterminada actualizada.')
        return redirect('addresses')

# Vistas de carrito
class CartView(LoginRequiredMixin, TemplateView):
    template_name = 'cart/cart.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener o crear el carrito del usuario
        cart, created = ShoppingCart.objects.get_or_create(user=self.request.user)
        
        # Obtener los items del carrito
        cart_items = CartItem.objects.filter(cart=cart).select_related('product')
        
        # Calcular el total
        total = sum(item.product.price * item.quantity for item in cart_items)
        
        context['cart'] = cart
        context['cart_items'] = cart_items
        context['total'] = total
        
        return context

class CartAddView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))
        
        product = get_object_or_404(Product, id=product_id)
        
        # Verificar stock
        if product.stock < quantity:
            messages.error(request, f'Lo sentimos, solo hay {product.stock} unidades disponibles.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('home')))
        
        # Obtener o crear el carrito
        cart, created = ShoppingCart.objects.get_or_create(user=request.user)
        
        # Añadir producto al carrito
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        # Si el producto ya estaba en el carrito, actualizar cantidad
        if not created:
            new_quantity = cart_item.quantity + quantity
            if product.stock < new_quantity:
                messages.error(request, f'Lo sentimos, solo hay {product.stock} unidades disponibles.')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('home')))
            
            cart_item.quantity = new_quantity
            cart_item.save()
        
        messages.success(request, f'{product.name} añadido al carrito.')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            cart_count = CartItem.objects.filter(cart=cart).aggregate(
                total=Sum('quantity')
            )['total'] or 0
            
            return JsonResponse({
                'success': True,
                'message': f'{product.name} añadido al carrito.',
                'cart_count': cart_count
            })
        
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('home')))

class CartUpdateView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        item_id = request.POST.get('item_id')
        quantity = int(request.POST.get('quantity', 1))
        
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        
        # Verificar stock
        if cart_item.product.stock < quantity:
            messages.error(request, f'Lo sentimos, solo hay {cart_item.product.stock} unidades disponibles.')
            return redirect('cart')
        
        # Actualizar cantidad
        cart_item.quantity = quantity
        cart_item.save()
        
        messages.success(request, 'Carrito actualizado.')
        return redirect('cart')

class CartRemoveView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        item_id = request.POST.get('item_id')
        
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        product_name = cart_item.product.name
        cart_item.delete()
        
        messages.success(request, f'{product_name} eliminado del carrito.')
        return redirect('cart')

# Vistas de checkout
class CheckoutView(LoginRequiredMixin, TemplateView):
    template_name = 'checkout/checkout.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Verificar que el carrito no esté vacío
        cart = ShoppingCart.objects.filter(user=request.user).first()
        if not cart or not CartItem.objects.filter(cart=cart).exists():
            messages.error(request, 'Tu carrito está vacío.')
            return redirect('cart')
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener el carrito
        cart = ShoppingCart.objects.get(user=self.request.user)
        cart_items = CartItem.objects.filter(cart=cart).select_related('product')
        
        # Calcular el total
        total = sum(item.product.price * item.quantity for item in cart_items)
        
        # Obtener direcciones del usuario
        addresses = Address.objects.filter(user=self.request.user).order_by('-is_default')
        
        context['cart'] = cart
        context['cart_items'] = cart_items
        context['total'] = total
        context['addresses'] = addresses
        context['default_address'] = addresses.filter(is_default=True).first()
        
        return context

class OrderCreateView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        # Obtener datos del formulario
        address_id = request.POST.get('address_id')
        payment_method = request.POST.get('payment_method')
        
        # Validar datos
        if not address_id or not payment_method:
            messages.error(request, 'Por favor, completa todos los campos requeridos.')
            return redirect('checkout')
        
        # Obtener dirección
        address = get_object_or_404(Address, id=address_id, user=request.user)
        
        # Obtener carrito
        cart = ShoppingCart.objects.get(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart).select_related('product')
        
        # Verificar stock
        for item in cart_items:
            if item.product.stock < item.quantity:
                messages.error(request, f'Lo sentimos, solo hay {item.product.stock} unidades disponibles de {item.product.name}.')
                return redirect('checkout')
        
        # Calcular total
        total = sum(item.product.price * item.quantity for item in cart_items)
        
        # Crear orden
        order = Order.objects.create(
            user=request.user,
            status=OrderStatus.PENDING,
            shipping_address=address.full_address()
        )
        
        # Crear items de la orden
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price,
                subtotal=item.product.price * item.quantity
            )
            
            # Actualizar stock
            item.product.stock -= item.quantity
            item.product.save()
        
        # Crear pago
        payment = Payment.objects.create(
            order=order,
            amount=total,
            payment_method=payment_method,
            payment_status=True  # Simulamos que el pago fue exitoso
        )
        
        # Vaciar carrito
        cart_items.delete()
        
        messages.success(request, f'Pedido #{order.order_id} creado correctamente.')
        return redirect('order_confirmation', order_id=order.order_id)

class OrderConfirmationView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'orders/order_confirmation.html'
    context_object_name = 'order'
    slug_field = 'order_id'
    slug_url_kwarg = 'order_id'
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order_items'] = OrderItem.objects.filter(order=self.object).select_related('product')
        return context

# Vista de newsletter
class NewsletterSubscribeView(View):
    def post(self, request, *args, **kwargs):
        form = NewsletterForm(request.POST)
        
        if form.is_valid():
            email = form.cleaned_data['email']
            
            # Verificar si el email ya está suscrito
            if Newsletter.objects.filter(email=email).exists():
                messages.info(request, 'Este email ya está suscrito a nuestro newsletter.')
            else:
                Newsletter.objects.create(email=email)
                messages.success(request, '¡Gracias por suscribirte a nuestro newsletter!')
        else:
            messages.error(request, 'Por favor, introduce un email válido.')
        
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('home')))

# Vista de búsqueda
class SearchView(ListView):
    model = Product
    template_name = 'pages/search_results.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        query = self.request.GET.get('q', '')
        
        if query:
            return Product.objects.filter(
                Q(name__icontains=query) | 
                Q(description__icontains=query) |
                Q(category__icontains=query)
            )
        
        return Product.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context

# Vistas de administración
class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff

class AdminDashboardView(LoginRequiredMixin, StaffRequiredMixin, TemplateView):
    template_name = 'admin/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Estadísticas generales
        context['total_users'] = User.objects.count()
        context['total_products'] = Product.objects.count()
        context['total_orders'] = Order.objects.count()
        context['total_revenue'] = Payment.objects.filter(payment_status=True).aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Pedidos recientes
        context['recent_orders'] = Order.objects.all().order_by('-date')[:5]
        
        # Productos más vendidos
        context['top_products'] = OrderItem.objects.values('product__name').annotate(
            total_sold=Sum('quantity')
        ).order_by('-total_sold')[:5]
        
        # Ventas por día (últimos 7 días)
        end_date = timezone.now()
        start_date = end_date - timedelta(days=7)
        
        daily_sales = Order.objects.filter(
            date__range=[start_date, end_date]
        ).annotate(
            day=TruncDay('date')
        ).values('day').annotate(
            count=Count('id'),
            revenue=Sum('payment__amount')
        ).order_by('day')
        
        # Preparar datos para el gráfico de ventas diarias
        daily_sales_json = {
            'labels': [sale['day'].strftime('%d/%m') for sale in daily_sales],
            'values': [float(sale['revenue'] or 0) for sale in daily_sales]
        }
        
        # Ventas por mes (últimos 6 meses)
        start_date_month = end_date - timedelta(days=180)
        
        monthly_sales = Order.objects.filter(
            date__range=[start_date_month, end_date]
        ).annotate(
            month=TruncMonth('date')
        ).values('month').annotate(
            count=Count('id'),
            revenue=Sum('payment__amount')
        ).order_by('month')
        
        # Preparar datos para el gráfico de ventas mensuales
        monthly_sales_json = {
            'labels': [sale['month'].strftime('%b %Y') for sale in monthly_sales],
            'values': [float(sale['revenue'] or 0) for sale in monthly_sales]
        }
        
        context['daily_sales'] = daily_sales
        context['monthly_sales'] = monthly_sales
        context['daily_sales_json'] = mark_safe(json.dumps(daily_sales_json))
        context['monthly_sales_json'] = mark_safe(json.dumps(monthly_sales_json))
        
        return context

class AdminProductListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = Product
    template_name = 'admin/products.html'
    context_object_name = 'products'
    paginate_by = 20
    ordering = ['-id']

class AdminProductCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = Product
    template_name = 'admin/product_form.html'
    fields = ['name', 'price', 'description', 'category', 'stock', 'image']
    success_url = reverse_lazy('admin_products')
    
    def form_valid(self, form):
        messages.success(self.request, 'Producto creado correctamente.')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Crear Producto'
        return context

class AdminProductUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = Product
    template_name = 'admin/product_form.html'
    fields = ['name', 'price', 'description', 'category', 'stock', 'image']
    success_url = reverse_lazy('admin_products')
    
    def form_valid(self, form):
        messages.success(self.request, 'Producto actualizado correctamente.')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Editar Producto'
        return context

class AdminProductDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = Product
    template_name = 'admin/product_confirm_delete.html'
    success_url = reverse_lazy('admin_products')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Producto eliminado correctamente.')
        return super().delete(request, *args, **kwargs)

class AdminOrderListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = Order
    template_name = 'admin/orders.html'
    context_object_name = 'orders'
    paginate_by = 20
    ordering = ['-date']

class AdminOrderDetailView(LoginRequiredMixin, StaffRequiredMixin, DetailView):
    model = Order
    template_name = 'admin/order_detail.html'
    context_object_name = 'order'
    slug_field = 'order_id'
    slug_url_kwarg = 'order_id'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order_items'] = OrderItem.objects.filter(order=self.object).select_related('product')
        context['order_statuses'] = OrderStatus.choices
        return context
    
    def post(self, request, *args, **kwargs):
        order = self.get_object()
        new_status = request.POST.get('status')
        tracking_number = request.POST.get('tracking_number')
        
        if new_status and new_status in dict(OrderStatus.choices):
            order.status = new_status
        
        if tracking_number:
            order.tracking_number = tracking_number
        
        order.save()
        messages.success(request, f'Pedido #{order.order_id} actualizado correctamente.')
        return redirect('admin_order_detail', order_id=order.order_id)

class AdminUserListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = User
    template_name = 'admin/users.html'
    context_object_name = 'users'
    paginate_by = 20
    ordering = ['-date_joined']