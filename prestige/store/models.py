from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver

class User(AbstractUser):
    email = models.EmailField(unique=True)
    payment_method = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return self.username

class Product(models.Model):
    product_id = models.PositiveIntegerField(unique=True, editable=False)
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    category = models.CharField(max_length=100)
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='products/', null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.product_id:
            max_id = Product.objects.aggregate(models.Max('product_id'))['product_id__max']
            self.product_id = (max_id or 0) + 1  # Si no hay productos, inicia en 1
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    def update_stock(self, quantity):
        if self.stock >= quantity:
            self.stock -= quantity
            self.save()
            return True
        return False

class Catalog(models.Model):
    name = models.CharField(max_length=100)
    categories = models.JSONField(default=list)
    
    def __str__(self):
        return self.name
    
    def filter_items(self, **kwargs):
        return Product.objects.filter(**kwargs)
    
    def search_items(self, query):
        return Product.objects.filter(
            models.Q(name__icontains=query) | 
            models.Q(description__icontains=query) |
            models.Q(category__icontains=query)
        )

class ShoppingCart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='shopping_cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Carrito de {self.user.username}"
    
    @property
    def total(self):
        return sum(item.subtotal for item in self.items.all())
    
    def clear_cart(self):
        self.items.all().delete()

class CartItem(models.Model):
    cart = models.ForeignKey(ShoppingCart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    class Meta:
        unique_together = ('cart', 'product')
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    
    @property
    def subtotal(self):
        return self.product.price * self.quantity

class OrderStatus(models.TextChoices):
    PENDING = 'PE', 'Pendiente'
    SHIPPED = 'SH', 'Enviado'
    DELIVERED = 'DE', 'Entregado'
    CANCELLED = 'CA', 'Cancelado'

class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.BooleanField(default=False)
    payment_method = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Pago de {self.user.username} - {self.amount}€"
    
    def process_payment(self):
        # Aquí iría la lógica para procesar el pago
        # Por ahora, simplemente marcamos como pagado
        self.payment_status = True
        self.save()
        return True

class Order(models.Model):
    order_id = models.PositiveIntegerField(unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    payment = models.OneToOneField(Payment, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=2, choices=OrderStatus.choices, default=OrderStatus.PENDING)
    shipping_address = models.TextField()
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.order_id:
            max_id = Order.objects.aggregate(models.Max('order_id'))['order_id__max']
            self.order_id = (max_id or 0) + 1  # Si no hay órdenes, inicia en 1
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Orden {self.order_id}"
    
    def get_order_details(self):
        items = OrderItem.objects.filter(order=self)
        return {
            'order_id': self.order_id,
            'date': self.date,
            'status': self.get_status_display(),
            'total': sum(item.subtotal for item in items),
            'items': items
        }
    
    def cancel_order(self):
        if self.status == OrderStatus.PENDING:
            self.status = OrderStatus.CANCELLED
            self.save()
            # Devolver stock
            for item in OrderItem.objects.filter(order=self):
                item.product.stock += item.quantity
                item.product.save()
            return True
        return False

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Guardamos el precio al momento de la compra
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    
    @property
    def subtotal(self):
        return self.price * self.quantity

# Señales para crear automáticamente un carrito cuando se crea un usuario
@receiver(post_save, sender=User)
def create_user_cart(sender, instance, created, **kwargs):
    if created:
        ShoppingCart.objects.create(user=instance)

class Newsletter(models.Model):
    email = models.EmailField(unique=True)
    date_subscribed = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.email

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    name = models.CharField(max_length=100)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.city}, {self.country}"
    
    def save(self, *args, **kwargs):
        # Si esta dirección se marca como predeterminada, desmarca las demás
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).update(is_default=False)
        # Si es la primera dirección del usuario, márcala como predeterminada
        elif not Address.objects.filter(user=self.user).exists():
            self.is_default = True
        super().save(*args, **kwargs)
    
    def full_address(self):
        address = f"{self.address_line1}"
        if self.address_line2:
            address += f", {self.address_line2}"
        address += f", {self.city}, {self.state}, {self.postal_code}, {self.country}"
        return address