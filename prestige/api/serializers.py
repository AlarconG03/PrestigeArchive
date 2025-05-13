from rest_framework import serializers
from store.models import Product

class ProductSerializer(serializers.ModelSerializer):
    product_page = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = '__all__'  
    
    def get_product_page(self, obj):
        """
        Get the direct link to view the product on the website
        """
        request = self.context.get('request')
        if request is not None:
            return request.build_absolute_uri(f'/products/{obj.id}/')
        return f'/products/{obj.id}/'