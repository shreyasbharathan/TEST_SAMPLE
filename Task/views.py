from asyncio import Task

from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

from deals.models import Deal
from leads.models import Lead
from invoice.models import Invoice
from quotes.models import QuoteRequest
from .models import  Notification, Task
# from Policy.models import Policy
from leads.models import Lead
from rest_framework import status,viewsets
from .serializers import LeadListSerializer, LeadSerializer, TaskSerializer, WorkflowStatsSerializer
from invoice.models import Invoice, StatusOverview,Transaction
from django.utils.timezone import now
from django.utils.timesince import timesince
from datetime import timedelta
from django.contrib.contenttypes.models import ContentType
# from invoice.models import Tranctions










@api_view(['GET'])
def lead_list(request):
    leads = Lead.objects.all().order_by('-created_at')

    serializer = LeadListSerializer(leads, many=True)

    return Response({
        "total_count": leads.count(),
        "results": serializer.data
    }, status=status.HTTP_200_OK)




@api_view(['GET'])
def workflow_dashboard(request):

    user = request.user

    # -------------------------------

    # -------------------------------
    if not user or not user.is_authenticated:
        return Response(
            {"error": "Unauthorized"},
            status=status.HTTP_401_UNAUTHORIZED
        )

    # -------------------------------
    # 🔹 TASK SUMMARY
    # -------------------------------
    lead_type = ContentType.objects.get_for_model(Lead)

    tasks = Task.objects.filter(
        assigned_to=user,
        content_type=lead_type
    )

    total_tasks = tasks.count()
    completed_tasks = tasks.filter(status='Done').count()
    pending_customer = tasks.filter(status='Todo').count()
    pending_underwriter = tasks.filter(status='In Progress').count()

    # -------------------------------
    # 🔹 LEAD WORKFLOW (8 STAGES)
    # -------------------------------
    lead_counts = (
        Lead.objects
        .filter(responsible=user)
        .values('stage')
        .annotate(count=Count('id'))
    )

    # Initialize all stages = 0
    lead_stage_map = {key: 0 for key, _ in Lead.STAGE_CHOICES}

    # Fill actual counts
    for item in lead_counts:
        lead_stage_map[item['stage']] = item['count']

    # Convert to UI labels
    lead_workflow = [
        {
            "stage": label,
            "count": lead_stage_map[key]
        }
        for key, label in Lead.STAGE_CHOICES
    ]

    # -------------------------------
    # 🔹 DEAL WORKFLOW (15 STAGES)
    # -------------------------------
    deal_counts = (
        Deal.objects
        .filter(lead__responsible=user)
        .values('stage_id')   # ✅ FIXED
        .annotate(count=Count('id'))
    )

    # Initialize all stages = 0
    deal_stage_map = {key: 0 for key, _ in Deal.STAGE_CHOICES}

    # Fill actual counts
    for item in deal_counts:
        deal_stage_map[item['stage_id']] = item['count']

    # Convert to UI labels
    deal_workflow = [
        {
            "stage": label,
            "count": deal_stage_map[key]
        }
        for key, label in Deal.STAGE_CHOICES
    ]

    # -------------------------------
    # 🔹 FINAL RESPONSE
    # -------------------------------
    return Response({
        "task_summary": [
            {"title": "Total Tasks", "count": total_tasks},
            {"title": "Pending with Customer", "count": pending_customer},
            {"title": "Pending with Underwriter", "count": pending_underwriter},
            {"title": "Completed Tasks", "count": completed_tasks},
        ],
        "lead_workflow": lead_workflow,
        "deal_workflow": deal_workflow
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
def Total_tasks(request):
    total_tasks = Task.objects.count()


    return Response({
        "total_tasks": total_tasks
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
def lead_list(request):
    leads = Lead.objects.all().order_by('-created_at')

    serializer = LeadListSerializer(leads, many=True)

    return Response({
        "total_count": leads.count(),
        "results": serializer.data
    }, status=status.HTTP_200_OK)


# @api_view(['GET'])
# def lead_filter(request):
#     filter_type = request.GET.get('filter')  # 7days / 30days / year

#     leads = Lead.objects.all()

#     today = timezone.now()

#     if filter_type == '7days':
#         date_from = today - timedelta(days=7)
#         leads = leads.filter(created_at__gte=date_from)

#     elif filter_type == '30days':
#         date_from = today - timedelta(days=30)
#         leads = leads.filter(created_at__gte=date_from)
#     elif filter_type == '90days':
#         date_from = today - timedelta(days=90)
#         leads = leads.filter(created_at__gte=date_from)

#     elif filter_type == 'year':
#         leads = leads.filter(created_at__year=today.year)
#     else:
#         return Response({"error": "Invalid filter type"}, status=status.HTTP_400_BAD_REQUEST)

#     serializer = LeadSerializer(leads, many=True)
#     return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_full_filter_data(request):
    # 1. Capture the 'days' parameter from the URL (?days=7, 30, 90, this_year)
    days_param = request.query_params.get('days', '7')
    now = timezone.now()
    
    # 2. Define the start date based on the filter selected
    if days_param == 'this_year':
        start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0)
    else:
        try:
            days_count = int(days_param)
            start_date = now - timedelta(days=days_count)
        except (ValueError, TypeError):
            start_date = now - timedelta(days=7)

    # --- SECTION 1: TOP SUMMARY CARDS ---
    # Fix: Deal model has no 'status', use 'stage_id' instead
    summary = {
        # stage_id 1 = Potential Customer
        "pending_with_customer": Deal.objects.filter(created_at__gte=start_date, stage_id=1).count(),
        # stage_id 9 = Pending with Insurer
        "pending_with_underwriter": Deal.objects.filter(created_at__gte=start_date, stage_id=9).count(),
        # stage_id 13 = Policy Issuance
        "completed_tasks": Deal.objects.filter(created_at__gte=start_date, stage_id=13).count(),
    }

    # --- SECTION 2: MIDDLE ROW CATEGORIES ---
    categories = {
        "leads_count": Lead.objects.filter(created_at__gte=start_date).count(),
        "documents_count": Deal.objects.filter(created_at__gte=start_date, stage_id=2).count(),
        "quotation_count": Deal.objects.filter(created_at__gte=start_date, stage_id=3).count(),
        "acceptance_count": Deal.objects.filter(created_at__gte=start_date, stage_id=4).count(),
    }

    # --- SECTION 3: THE MAIN TABLE DATA ---
    leads_queryset = Lead.objects.filter(created_at__gte=start_date).order_by('-created_at')
    
    table_data = []
    for lead in leads_queryset:
        # Fix: Your model uses related_name='deals', not 'policies'
        deal = lead.deals.first() 
        time_label = f"{timesince(lead.created_at).split(',')[0]} ago"

        table_data.append({
            "id": lead.id,
            "start_date": time_label,
            "modified": time_label,
            "first_name": lead.name,
            "lead_source": lead.get_delivery_channel_display() or "Website Enquiry",
            "responsible": lead.responsible.username if lead.responsible else "Unassigned",
            "phone": lead.phone_number if lead.phone_number else "N/A",
            "stage": {
                "name": deal.get_stage_id_display() if deal else "New Lead",
                "id": deal.stage_id if deal else 1,
                "percentage": round((deal.stage_id / 15) * 100) if deal else 10
            }
        })

    return Response({
        "filter_info": {
            "applied": days_param,
            "start_date": start_date.strftime("%Y-%m-%d")
        },
        "summary": summary,
        "categories": categories,
        "table_data": table_data
    })






@api_view(['GET'])
def get_pending_tasks(request):
    start_date = now() - timedelta(days=30)   # example: last 30 days

    active_leads = Lead.objects.filter(
        created_at__gte=start_date
    ).count()

    active_deals = Deals.objects.filter(
        status="active"
    ).count()
    documents_pending = Deals.objects.filter(
        status="pending"
    ).count()
    pending_customer=Deals.objects.filter(
        status="pending",
        customer=request.user
    ).count()

    pending_quotes = QuoteRequest.objects.filter(
        status="pending"
    ).count()
    underwriter_count = Deals.objects.filter(status='UNDERWRITING').count()
    pending_billing = StatusOverview.objects.filter(
        status="pending"
    ).count()

    pending_tasks = Task.objects.filter(
        status="pending"
    ).count()

    data = {
        "active_leads": active_leads,
        "active_deals": active_deals,
        "pending_quotes": pending_quotes,
        "pending_underwriting": underwriter_count,
        "pending_tasks": pending_tasks,
        "pending_documents": documents_pending,
        "pending_customer": pending_customer,
        "pending_billing": pending_billing
    }

    return Response(data, status=status.HTTP_200_OK)






@api_view(['GET'])
def notification(request):
    # 1. Get today's date
    today = timezone.now().date()


    pending_task_count = Task.objects.filter(status="pending").count()

    
    user_notifications = Notification.objects.filter(
        user=request.user,
        created_at__date=today
    ).order_by('-created_at')
    
    notifications_data = []
    for n in user_notifications:
        notifications_data.append({
            "id": n.id,
            "title": n.title,             
            "description": n.message,     
            "timestamp": n.created_at.strftime("%m/%d/%Y %I:%M %p"), 
            "is_read": n.is_read
        })

    # Return the data structured for your reference image
    return Response({
        "total_to_go_through": pending_task_count, 
        "notifications": notifications_data        
    }, status=status.HTTP_200_OK)



@api_view(['POST'])
def mark_all_notifications_read(request):
    # This finds all unread notifications for the user and updates them at once
    updated_count = Notification.objects.filter(
        user=request.user, 
        is_read=False
    ).update(is_read=True)

    return Response({
        "message": f"Updated {updated_count} notifications to read.",
        "status": "success"
    }, status=status.HTTP_200_OK)


@api_view(['PATCH'])
def mark_single_notification_read(request, pk):
    try:
        notification = Notification.objects.get(pk=pk, user=request.user)
        notification.is_read = True
        notification.save()
        return Response({"message": "Notification marked as read."})
    except Notification.DoesNotExist:
        return Response({"error": "Notification not found."}, status=status.HTTP_404_NOT_FOUND)



 


