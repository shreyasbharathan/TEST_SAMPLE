

from leads import serializers


class PolicyDashboardSerializer(serializers.Serializer):
    total_policies = serializers.IntegerField()
    active = serializers.IntegerField()
    pending_payment = serializers.IntegerField()
    processing = serializers.IntegerField()