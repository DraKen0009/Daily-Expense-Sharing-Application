from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Expense(models.Model):
    class SplitMethodChoices(models.TextChoices):
        EQUAL = 'EQUAL', "Equal"
        EXACT = 'EXACT', "Exact"
        PERCENTAGE = 'PERCENTAGE', "Percentage"

    description = models.CharField(max_length=255)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[
        MinValueValidator(0),
    ])
    created_by = models.ForeignKey(User, related_name='expenses_created', on_delete=models.CASCADE)
    split_method = models.CharField(max_length=20, choices=SplitMethodChoices.choices, default=SplitMethodChoices.EQUAL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.description} - {self.total_amount} - {self.created_by}"


class ExpenseShare(models.Model):
    expense = models.ForeignKey(Expense, related_name='shares', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='expense_shares', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, validators=[
        MinValueValidator(0),
    ])
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, validators=[
        MinValueValidator(0),
        MaxValueValidator(100)
    ])

    def __str__(self):
        return f"{self.user} owes {self.amount} for {self.expense}"
