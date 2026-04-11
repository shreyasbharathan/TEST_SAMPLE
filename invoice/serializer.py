from rest_framework import serializers
from .models import Invoice, IndividualCustomer

# 🔹 Individual Serializer
class IndividualCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = IndividualCustomer
        exclude = ("invoice",)


# 🔹 Invoice Serializer (Main)
class InvoiceSerializer(serializers.ModelSerializer):

    individual = IndividualCustomerSerializer(required=False)

    class Meta:
        model = Invoice
        fields = [
            "id",
            "customer_type",
            "producer",
            "main_customer",
            "delivery_channel",
            "pep",
            "remarks",
            "individual"
        ]

    def create(self, validated_data):
        individual_data = validated_data.pop("individual", None)

        # ✅ Create Invoice
        invoice = Invoice.objects.create(**validated_data)

        # ✅ Create Individual (from form left side)
        if individual_data:
            IndividualCustomer.objects.create(
                invoice=invoice,
                **individual_data
            )

        return invoice
    
class InvoiceListSerializer(serializers.ModelSerializer):

    invoice_id = serializers.SerializerMethodField()
    policy_number = serializers.SerializerMethodField()
    customer_name = serializers.SerializerMethodField()
    premium = serializers.SerializerMethodField()
    issue_date = serializers.SerializerMethodField()
    due_date = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    available_actions = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = [
            "invoice_id",
            "policy_number",
            "customer_name",
            "premium",
            "issue_date",
            "due_date",
            "status",
            "available_actions",
        ]

    def get_invoice_id(self, obj):
        return f"INV-{obj.id:03d}"

    def get_policy_number(self, obj):
        tx = obj.transactions.first()
        return tx.policy_number if tx else ""

    def get_customer_name(self, obj):
        try:
            return obj.individual.name
        except:
            try:
                return obj.cooperative.company_name
            except:
                return ""

    def get_premium(self, obj):
        tx = obj.transactions.first()
        if tx:
            return {
                "currency": tx.premium_currency,
                "amount": tx.total_premium
            }
        return {"currency": "", "amount": 0}

    def get_issue_date(self, obj):
        tx = obj.transactions.first()
        return tx.invoice_date if tx else None

    def get_due_date(self, obj):
        tx = obj.transactions.first()
        return tx.due_date if tx else None

    def get_status(self, obj):
        status_obj = obj.status_logs.last()
        return status_obj.status.lower() if status_obj else "pending"

    def get_available_actions(self, obj):
        status = self.get_status(obj)

        if status == "paid":
            return ["download"]
        elif status in ["pending", "overdue"]:
            return ["download", "send_reminder"]

        return []