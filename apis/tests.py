from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import Expense, ExpenseShare

User = get_user_model()


class ExpenseViewSetTests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(email='user1@example.com', password='pass1234', name="user1",
                                              mobile_number='9999988888')
        self.user2 = User.objects.create_user(email='user2@example.com', password='pass1234', name="user1",
                                              mobile_number='9999988887')
        self.user3 = User.objects.create_user(email='user3@example.com', password='pass1234', name="user1",
                                              mobile_number='9999988889')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user1)

    def test_create_expense_with_invalid_user_id(self):
        invalid_user_id = '00000000-0000-0000-0000-000000000000'
        data = {
            "description": "Dinner at restaurant",
            "total_amount": 3000.00,
            "split_method": "EQUAL",
            "shares": [
                {"user_id": str(self.user1.id)},
                {"user_id": invalid_user_id},
                {"user_id": str(self.user3.id)}
            ]
        }
        response = self.client.post('/api/expenses/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'User with id 00000000-0000-0000-0000-000000000000 does not exist')

    def test_create_expense_equal_split(self):
        data = {
            "description": "Dinner at restaurant",
            "total_amount": 3000.00,
            "split_method": "EQUAL",
            "shares": [
                {"user_id": str(self.user1.id)},
                {"user_id": str(self.user2.id)},
                {"user_id": str(self.user3.id)}
            ]
        }
        response = self.client.post('/api/expenses/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Expense.objects.count(), 1)
        self.assertEqual(ExpenseShare.objects.count(), 3)
        for expense in ExpenseShare.objects.all():
            self.assertEqual(expense.amount, 1000.00)

    def test_create_expense_exact_split(self):
        data = {
            "description": "Hotel Booking",
            "total_amount": 4000.00,
            "split_method": "EXACT",
            "shares": [
                {"user_id": str(self.user1.id), "amount": 1500.00},
                {"user_id": str(self.user2.id), "amount": 2500.00}
            ]
        }
        response = self.client.post('/api/expenses/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Expense.objects.count(), 1)
        self.assertEqual(ExpenseShare.objects.count(), 2)
        self.assertEqual(ExpenseShare.objects.filter(user_id=self.user1.id).first().amount, 1500.00)
        self.assertEqual(ExpenseShare.objects.filter(user_id=self.user2.id).first().amount, 2500.00)

    def test_create_expense_exact_split_with_invalid_amounts(self):
        data = {
            "description": "Hotel Booking",
            "total_amount": 4000.00,
            "split_method": "EXACT",
            "shares": [
                {"user_id": str(self.user1.id), "amount": 1400.00},
                {"user_id": str(self.user2.id), "amount": 2500.00}
            ]
        }
        response = self.client.post('/api/expenses/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Total amount must equal 4000.00')

    def test_create_expense_percentage_split(self):
        data = {
            "description": "Group Gift",
            "total_amount": 5000.00,
            "split_method": "PERCENTAGE",
            "shares": [
                {"user_id": str(self.user1.id), "percentage": 40},
                {"user_id": str(self.user2.id), "percentage": 60}
            ]
        }
        response = self.client.post('/api/expenses/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Expense.objects.count(), 1)
        self.assertEqual(ExpenseShare.objects.count(), 2)
        self.assertEqual(ExpenseShare.objects.filter(user_id=self.user1.id).first().amount, 2000.00)
        self.assertEqual(ExpenseShare.objects.filter(user_id=self.user2.id).first().amount, 3000.00)

    def test_create_expense_percentage_split_with_invalid_percentage(self):
        data = {
            "description": "Group Gift",
            "total_amount": 5000.00,
            "split_method": "PERCENTAGE",
            "shares": [
                {"user_id": str(self.user1.id), "percentage": 30},
                {"user_id": str(self.user2.id), "percentage": 60}
            ]
        }
        response = self.client.post('/api/expenses/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Total percentage must equal 100%')

    def test_my_expenses(self):
        expense1 = Expense.objects.create(description="Expense 1", total_amount=1000.00, created_by=self.user1,
                                          split_method="EQUAL")
        ExpenseShare.objects.create(expense=expense1, user=self.user1, amount=500.00)
        ExpenseShare.objects.create(expense=expense1, user=self.user2, amount=500.00)

        expense2 = Expense.objects.create(description="Expense 2", total_amount=2000.00, created_by=self.user1,
                                          split_method="EXACT")
        ExpenseShare.objects.create(expense=expense2, user=self.user1, amount=800.00)
        ExpenseShare.objects.create(expense=expense2, user=self.user3, amount=1200.00)

        response = self.client.get('/api/expenses/my_expenses/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
