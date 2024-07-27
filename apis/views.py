from django.contrib.auth import get_user_model
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Expense, ExpenseShare
from .serializers import ExpenseSerializer, ExpenseCreateSerializer

User = get_user_model()


class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return ExpenseCreateSerializer
        return ExpenseSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        users = data.get('shares')
        total_amount = data.get('total_amount')
        split_method = data.get('split_method')
        description = data.get('description')
        created_by = request.user

        expense = Expense.objects.create(
            description=description,
            total_amount=total_amount,
            created_by=created_by,
            split_method=split_method
        )

        if split_method == Expense.SplitMethodChoices.EQUAL:
            amount_per_user = total_amount / len(users)
            for user_id in users:
                user = User.objects.get(id=user_id['user_id'])
                ExpenseShare.objects.create(
                    expense=expense,
                    user=user,
                    amount=amount_per_user
                )

        elif split_method == Expense.SplitMethodChoices.EXACT:
            amount = sum([share['amount'] for share in users])
            if amount != total_amount:
                return Response({'error': f'Total amount must equal {total_amount}'},
                                status=status.HTTP_400_BAD_REQUEST)
            for share in users:
                user = User.objects.get(id=share['user_id'])
                amount = share['amount']
                ExpenseShare.objects.create(
                    expense=expense,
                    user=user,
                    amount=amount
                )

        elif split_method == Expense.SplitMethodChoices.PERCENTAGE:
            total_percentage = sum([share['percentage'] for share in users])
            if total_percentage != 100:
                return Response({'error': 'Total percentage must equal 100%'}, status=status.HTTP_400_BAD_REQUEST)
            for share in users:
                user = User.objects.get(id=share['user_id'])
                percentage = share['percentage']
                amount = (total_amount * percentage) / 100
                ExpenseShare.objects.create(
                    expense=expense,
                    user=user,
                    amount=amount,
                    percentage=percentage
                )

        return Response({'message': 'Expense created successfully'}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def my_expenses(self, request):
        user = request.user
        print(user)
        print("hello")
        expenses = Expense.objects.filter(shares__user=user)
        serializer = ExpenseSerializer(expenses, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def download_balance_sheet(self, request):
        # Generate the balance sheet (for simplicity, we'll return a JSON response)
        balance_sheet = []
        for expense in Expense.objects.all():
            expense_data = ExpenseSerializer(expense).data
            balance_sheet.append(expense_data)
        return Response(balance_sheet, status=status.HTTP_200_OK)
