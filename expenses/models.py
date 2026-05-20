from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    CURRENCY_CHOICES = [
        ("$", "USD ($)"),
        ("R", "ZAR (R)"),
        ("€", "EUR (€)"),
        ("£", "GBP (£)"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    monthly_budget = models.DecimalField(max_digits=12, decimal_places=2, default=300)
    currency = models.CharField(max_length=5, choices=CURRENCY_CHOICES, default="$")
    low_balance_threshold = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, blank=True
    )

    def __str__(self):
        return f"Profile({self.user.username})"


class SavingsGoal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="savings_goals")
    name = models.CharField(max_length=100)
    target_amount = models.DecimalField(max_digits=12, decimal_places=2)
    saved_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.name} ({self.saved_amount}/{self.target_amount})"

    @property
    def progress_percent(self):
        if self.target_amount <= 0:
            return 0
        return min(100, int((self.saved_amount / self.target_amount) * 100))


class Expense(models.Model):
    TITLE_CHOICES = [
        ("Groceries", "Groceries"),
        ("Fuel", "Fuel"),
        ("Rent", "Rent"),
        ("Electricity Bill", "Electricity Bill"),
        ("Internet", "Internet"),
        ("Clothing", "Clothing"),
        ("Medical", "Medical"),
        ("Snacks & Drinks", "Snacks & Drinks"),
        ("Transport", "Transport"),
        ("Entertainment", "Entertainment"),
        ("Other", "Other"),
    ]

    CATEGORY_CHOICES = [
        ("Home", "Home"),
        ("Food", "Food"),
        ("Transport", "Transport"),
        ("Bills", "Bills"),
        ("School", "School"),
        ("Health", "Health"),
        ("Entertainment", "Entertainment"),
        ("Personal", "Personal"),
        ("Savings", "Savings"),
        ("Other", "Other"),
    ]

    AUTO_CATEGORY_MAP = {
        "Groceries": "Food",
        "Fuel": "Transport",
        "Rent": "Home",
        "Electricity Bill": "Bills",
        "Internet": "Bills",
        "Clothing": "Personal",
        "Medical": "Health",
        "Snacks & Drinks": "Food",
        "Transport": "Transport",
        "Entertainment": "Entertainment",
    }

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, choices=TITLE_CHOICES)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.amount}"


class Income(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    source = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.source} - {self.amount}"
