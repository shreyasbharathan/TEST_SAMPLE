from django.urls import path
from .views import *

urlpatterns = [
    
    path('create_invoice/', create_invoice),
    path('invoice_list/', invoice_list),
]