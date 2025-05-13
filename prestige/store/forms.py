from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Address, Newsletter
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
User = get_user_model()

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    #first_name = forms.CharField(required=True, label='Nombre')
    #last_name = forms.CharField(required=True, label='Apellido')
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({'class': 'form-control'})

class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({'class': 'form-control'})

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({'class': 'form-control'})
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        username = self.instance.username
        
        if email and User.objects.filter(email=email).exclude(username=username).exists():
            raise forms.ValidationError('Este email ya está en uso.')
        
        return email

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['name', 'address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country', 'phone', 'is_default']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            if field_name != 'is_default':
                self.fields[field_name].widget.attrs.update({'class': 'form-control'})

class NewsletterForm(forms.ModelForm):
    class Meta:
        model = Newsletter
        fields = ['email']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({
            'class': 'newsletter-input',
            'placeholder': _('Tu dirección de email')
        })