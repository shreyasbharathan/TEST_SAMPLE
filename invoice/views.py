from rest_framework.decorators import api_view
from rest_framework.response import Response

from invoice.models import Invoice
from invoice.serializer import InvoiceListSerializer, InvoiceSerializer
from django.core.paginator import Paginator
from django.db.models import Q

from invoice.serializer import InvoiceSerializer

@api_view(['POST'])
def create_invoice(request):
    print("DATA:", request.data)
    serializer = InvoiceSerializer(data=request.data)

    if serializer.is_valid():
        invoice = serializer.save()
        return Response({
            "message": "Invoice Created Successfully ",
            "invoice_id": invoice.id
        })
    print("ERROR:", serializer.errors)

    return Response(serializer.errors, status=400)



@api_view(['GET'])
def invoice_list(request):

    # 🔹 Query params
    status_filter = request.GET.get('status')   # paid / pending / overdue
    search = request.GET.get('search')          # search term
    page = int(request.GET.get('page', 1))

    # 🔹 Base queryset
    invoices = Invoice.objects.all().order_by('-id')

    # 🔍 SEARCH (name + policy number)
    if search:
        invoices = invoices.filter(
            Q(individual__name__icontains=search) |
            Q(cooperative__company_name__icontains=search) |
            Q(transactions__policy_number__icontains=search)
        ).distinct()

    # 🔎 STATUS FILTER
    if status_filter:
        filtered_invoices = []

        for inv in invoices:
            status_obj = inv.status_logs.last()

            if status_obj and status_obj.status.lower() == status_filter.lower():
                filtered_invoices.append(inv)

        invoices = filtered_invoices

    # 📄 PAGINATION (10 per page)
    paginator = Paginator(invoices, 10)
    page_obj = paginator.get_page(page)

    serializer = InvoiceListSerializer(page_obj, many=True)

    return Response({
        "results_found": paginator.count,
        "data": serializer.data
    })