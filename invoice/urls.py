from django.urls import path
from .views import *

urlpatterns = [
    
    path('create_invoice/', create_invoice),
    path('invoice_list/', invoice_list),
    path('billing_summary/', billing_summary),
    path('import_statement/', import_statement),
    # path('reconciliation/<int:id>/resolve/', resolve_reconciliation),
    # path('reconciliation/<int:id>/escalate/', escalate_reconciliation),
    path('transactions_dashboard/', transaction_dashboard),
    path('transactions/', transaction_list),

    path('reconciliation_table/', reconciliation_table),
    path('invoice_list_filter/', invoice_list_filter),
]