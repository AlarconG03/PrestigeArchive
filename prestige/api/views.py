from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Q
from .serializers import ProductSerializer
from store.models import Product
from django.shortcuts import render

@api_view(['GET'])
def api_root(request):
    """
    API root endpoint providing overview of available endpoints
    """
    return Response({
        'products': '/api/products/',
        'products_in_stock': '/api/products-in-stock/',
        'documentation': '/api/docs/',
    })

@api_view(['GET'])
def products_in_stock(request):
    """
    List all products currently in stock
    """
    
    products = Product.objects.filter(stock__gt=0)
    serializer = ProductSerializer(products, many=True, context={'request': request})
    return Response(serializer.data)

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This viewset automatically provides 'list' and 'retrieve' actions.
    """
    serializer_class = ProductSerializer
    
    def get_queryset(self):
        queryset = Product.objects.all()
        search = self.request.query_params.get('search', None)
        in_stock = self.request.query_params.get('in_stock', None)
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(description__icontains=search)
            )
        if in_stock and in_stock.lower() == 'true':
            queryset = queryset.filter(stock__gt=0)
            
        return queryset

def api_documentation(request):
    return render(request, 'api/docs.html')