from rest_framework import serializers
from .models import Expense, ExpenseShare
from users.serializers import UserSerializer


class ExpenseShareSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = ExpenseShare
        fields = ['id', 'user', 'amount', 'percentage']


class ExpenseSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    shares = ExpenseShareSerializer(many=True, read_only=True)

    class Meta:
        model = Expense
        fields = ['id', 'description', 'total_amount', 'created_by', 'split_method', 'created_at', 'updated_at',
                  'shares']


class ExpenseCreateSerializer(serializers.ModelSerializer):
    shares = serializers.ListField(write_only=True)

    class Meta:
        model = Expense
        fields = ['description', 'total_amount', 'split_method', 'shares']
