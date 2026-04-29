# from django.db import models
# from django.contrib.auth.models import User

# # The Expense model represents a single spending record.
# class Expense(models.Model):
#     # Link each expense to a user (foreign key relationship)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
    
#     # A short description or title for the expense
#     title = models.CharField(max_length=100)
    
#     # Amount spent (DecimalField is good for money)
#     amount = models.DecimalField(max_digits=10, decimal_places=2)
    
#     # Expense category (like Food, Transport, etc.)
#     category = models.CharField(max_length=50)
    
#     # Automatically store the date when expense was created
#     date = models.DateField(auto_now_add=True)

#     def __str__(self):
#         # This makes the admin panel show readable entries
#         return f"{self.title} - ${self.amount}"



from django.db import models
from django.contrib.auth.models import User

class Expense(models.Model):

    # Dropdown options for Expense Title
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
    ]

    # Dropdown options for Category
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

    # Mapping to auto-assign categories
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
    title = models.CharField(max_length=100, choices=TITLE_CHOICES)  # 👈 dropdown added
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)  # 👈 dropdown added
    amount = models.DecimalField(max_digits=10, decimal_places=2)
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
