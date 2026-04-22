from datetime import timedelta, timezone

from deals.models import Lead
from leads.serializers import LeadListSerializer
from rest_framework import serializers
from leads.models import Lead

from .models import Task

class WorkflowStatsSerializer(serializers.Serializer):
    total_tasks = serializers.IntegerField()
    pending_customer = serializers.IntegerField()
    pending_underwriter = serializers.IntegerField()
    completed_tasks = serializers.IntegerField()




class TaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = "__all__"



class LeadListSerializer(serializers.ModelSerializer):
    contact = serializers.SerializerMethodField()
    timestamps = serializers.SerializerMethodField()
    source_info = serializers.SerializerMethodField()
    assignment = serializers.SerializerMethodField()

    class Meta:
        model = Lead
        fields = "__all__"  # include all fields

    def get_contact(self, obj):
        return {
            "first_name": f"{obj.first_name} {obj.last_name or ''}".strip(),
            "phone": obj.mobile_number,
            "email": obj.email,
        }

    def get_source_info(self, obj):
        return {
            "source": obj.delivery_channel,
            "product_type": obj.product_type,
        }

    def get_timestamps(self, obj):
        return {
            "created_at": obj.created_at,
            "updated_at": obj.updated_at,
        }

    def get_assignment(self, obj):
        return {
            "status": obj.status,
            "stage": obj.stage,
            "progress_score": obj.progress_score,
            "responsible": obj.responsible.id if obj.responsible else None,
        }

class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = '__all__'
    




    



