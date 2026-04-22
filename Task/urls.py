from django.urls import path

from leads.views import lead_details,lead_list

from .views import get_full_filter_data, get_pending_tasks, get_pending_tasks, notification, lead_list
from . import views  # Assuming your function is in views.py
# ######  Akshaya  ######

urlpatterns = [
   
    path("list/", lead_list),
  
    path('<int:lead_id>/', lead_details),
   
    path('filter/', get_full_filter_data),
    path('get_pending_tasks/',get_pending_tasks),
    path('notification/',notification),
    path('mark_all_read/', views.mark_all_notifications_read),
    path('mark_read/<int:pk>/', views.mark_single_notification_read),
    path('total_tasks/', views.Total_tasks),
    path('workflow_dashboard/', views.workflow_dashboard),

]