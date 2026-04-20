from django.urls import path

from leads.views import lead_details,lead_list

from .views import create_task, get_pending_tasks, lead_filter,list_task,completed_tasks
from . import views  # Assuming your function is in views.py
# ######  Akshaya  ######

urlpatterns = [
    # Workflow Statistics API
    path('api/v1/workflow/stats', views.get_workflow_stats,name='workflow-stats'),
    path("<int:lead_id>/tasks/",create_task),
    path("export/",list_task),
    path("tasks/completed/",completed_tasks),
    path('<int:lead_id>/', lead_details),
   
    # path('exports/',lead_list),
    path('leads/', lead_filter),
    path('pending-tasks/', views.get_pending_tasks, name='pending-tasks'),
    path('get_pending_tasks/',get_pending_tasks),

]