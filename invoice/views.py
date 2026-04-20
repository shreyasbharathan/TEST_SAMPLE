from datetime import timedelta, timezone
from turtle import pd
from urllib import request

from rest_framework.decorators import api_view
from rest_framework.response import Response

from invoice.models import Invoice, Reconciliation
from invoice.serializer import BillingSummarySerializer, ImportStatementSerializer, InvoiceListSerializer, InvoiceSerializer, TransactionListSerializer
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.timezone import now
import os
from django.conf import settings
from .models import Reconciliation, Transaction
from invoice.serializer import ReconciliationListSerializer


from invoice.serializer import InvoiceSerializer, InvoiceListSerializer, BillingSummarySerializer, ImportStatementSerializer               

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

    status_filter = request.GET.get('status')
    search = request.GET.get('search')
    page = int(request.GET.get('page', 1))

    invoices = Invoice.objects.all().order_by('-id')

  
    if search:
        invoices = invoices.filter(
            Q(individual__name__icontains=search) |
            Q(cooperative__company_name__icontains=search) |
            Q(transactions__policy_number__icontains=search)
        ).distinct()

  
    if status_filter:
        invoices = invoices.filter(
            status_logs__status__iexact=status_filter
        ).distinct()

  
    paginator = Paginator(invoices, 10)
    page_obj = paginator.get_page(page)

    serializer = InvoiceListSerializer(page_obj, many=True)

    #  FILTER ONLY REQUIRED TABLE FIELDS
    table_data = []
    for item in serializer.data:
        table_data.append({
            "invoice_id": item["invoice_id"],
            "policy_number": item["policy_number"],
            "customer_name": item["customer_name"],
            "premium": item["premium"],
            "issue_date": item["issue_date"],
            "due_date": item["due_date"],
            "status": item["status"],
            "available_actions": item["available_actions"],
        })

    return Response({
        "results_found": paginator.count,
        "data": table_data
    })


@api_view(['GET'])
def billing_summary(request):
    period = request.GET.get('period', 'this_year')

    today = now()

    # 🔹 Date filter
    if period == "7days":
        start_date = today - timedelta(days=7)
    elif period == "30days":
        start_date = today - timedelta(days=30)
    elif period == "90days":
        start_date = today - timedelta(days=90)
    else:
        start_date = today.replace(month=1, day=1)

    invoices = Invoice.objects.filter(creation_date__gte=start_date)

    total_revenue = 0
    paid_count = 0
    pending_count = 0
    overdue_count = 0

    for inv in invoices:
        tx = inv.transactions.first()
        status_obj = inv.status_logs.order_by('-date').first()

        if tx:
            total_revenue += float(tx.total_premium)

        status = status_obj.status.lower() if status_obj else "pending"

        if status == "paid":
            paid_count += 1
        elif status == "pending":
            pending_count += 1
        elif status == "overdue":
            overdue_count += 1

    # 🔹 Prepare data
    data = {
        "total_revenue": {
            "currency": "AED",
            "amount": total_revenue
        },
        "paid_count": paid_count,
        "pending_count": pending_count,
        "overdue_count": overdue_count
    }

    serializer = BillingSummarySerializer(data)

    return Response(serializer.data)

# @api_view(['POST'])
# def import_statement(request):
#     serializer = ImportStatementSerializer(data=request.data)

#     if not serializer.is_valid():
#         return Response(serializer.errors, status=400)

#     file = serializer.validated_data['file']

#     try:
#         # 🔹 Read file (CSV or Excel)
#         if file.name.endswith('.csv'):
#             df = pd.read_csv(file)
#         elif file.name.endswith('.xlsx') or file.name.endswith('.xls'):
#             df = pd.read_excel(file)
#         else:
#             return Response({"error": "Unsupported file format"}, status=400)

#         # 🔹 Convert data to list (optional)
#         data = df.to_dict(orient="records")

#         # 🔹 Example: just return count
#         return Response({
#             "message": "File uploaded successfully",
#             "total_records": len(data),
#             "preview": data[:5]   # first 5 rows
#         })

#     except Exception as e:
#         return Response({"error": str(e)}, status=500)




@api_view(['POST'])
def import_statement(request):
    serializer = ImportStatementSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    file = serializer.validated_data['file']
    file_name = file.name.lower()

    try:
        # ✅ PDF
        if file_name.endswith('.pdf'):

            file_path = os.path.join(settings.MEDIA_ROOT, file.name)

            with open(file_path, 'wb+') as f:
                for chunk in file.chunks():
                    f.write(chunk)

            return Response({
                "message": "PDF uploaded successfully",
                "type": "pdf",
                "file_url": request.build_absolute_uri(settings.MEDIA_URL + file.name)
            })

        # ✅ Image
        elif file_name.endswith(('.jpg', '.jpeg', '.png')):

            file_path = os.path.join(settings.MEDIA_ROOT, file.name)

            with open(file_path, 'wb+') as f:
                for chunk in file.chunks():
                    f.write(chunk)

            return Response({
                "message": "Image uploaded successfully",
                "type": "image",
                "file_url": request.build_absolute_uri(settings.MEDIA_URL + file.name)
            })

        else:
            return Response({
                "error": "Only PDF, JPG, PNG allowed"
            }, status=400)

    except Exception as e:
        return Response({"error": str(e)}, status=500)
    

    

@api_view(['PATCH'])
def resolve_reconciliation(request, id):
    try:
        rec = Reconciliation.objects.get(id=id)
    except Reconciliation.DoesNotExist:
        return Response({"error": "Not found"}, status=404)

    rec.status = "resolved"
    rec.save()

    return Response({
        "message": "Reconciliation resolved successfully",
        "rec_id": rec.rec_id,
        "status": rec.status
    })

@api_view(['POST'])
def escalate_reconciliation(request, id):
    try:
        rec = Reconciliation.objects.get(id=id)
    except Reconciliation.DoesNotExist:
        return Response({"error": "Not found"}, status=404)

    rec.status = "escalated"
    rec.save()

    return Response({
        "message": "Reconciliation escalated successfully",
        "rec_id": rec.rec_id,
        "status": rec.status
    })




@api_view(['GET'])
def reconciliation_table(request):

    queryset = Reconciliation.objects.select_related(
        'invoice', 'policy'
    ).all().order_by('-created_at')

    serializer = ReconciliationListSerializer(queryset, many=True)

    return Response({
        "results_found": queryset.count(),
        "data": serializer.data
    })


@api_view(['GET'])
def transaction_dashboard(request):

    total = Transaction.objects.count()

    active = Transaction.objects.filter(
        policy_number__isnull=False
    ).count()

    pending_payment = Transaction.objects.filter(
        net_due__gt=0
    ).count()

    processing = Transaction.objects.filter(
        policy_number__isnull=True
    ).count()

    return Response({
        "total_policies": total,
        "active": active,
        "pending_payment": pending_payment,
        "processing": processing
    })



@api_view(['GET'])
def transaction_list(request):

    queryset = Transaction.objects.all().order_by('-invoice_date')

    # ✅ Optional filter (7, 30, 90 days)
    days = request.GET.get('days')
    if days:
        queryset = queryset.filter(
            invoice_date__gte=now().date() - timedelta(days=int(days))
        )

    serializer = TransactionListSerializer(queryset, many=True)

    return Response({
        "total": queryset.count(),
        "data": serializer.data
    })



@api_view(['GET'])
def invoice_list_filter(request):
    days = request.GET.get('days')  # 7, 30, 90
    page = request.GET.get('page', 1)

    invoices = Invoice.objects.all().order_by('-creation_date')

    # ✅ FILTER LOGIC
    if days:
        try:
            days = int(days)
            from_date = timezone.now().date() - timedelta(days=days)
            invoices = invoices.filter(issue_date__gte=from_date)
        except:
            pass

    # ✅ PAGINATION
    paginator = Paginator(invoices, 10)  # 10 records per page
    page_obj = paginator.get_page(page)

    serializer = InvoiceListSerializer(page_obj, many=True)

    # ✅ TABLE FORMAT
    table_data = []
    for item in serializer.data:
        table_data.append({
            "invoice_id": item["invoice_id"],
            "policy_number": item["policy_number"],
            "customer_name": item["customer_name"],
            "premium": item["premium"],
            "issue_date": item["issue_date"],
            "due_date": item["due_date"],
            "status": item["status"],
            "available_actions": item["available_actions"],
        })

    return Response({
        "results_found": paginator.count,
        "total_pages": paginator.num_pages,
        "current_page": page_obj.number,
        "data": table_data
    })