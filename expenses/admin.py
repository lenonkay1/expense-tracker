from django.contrib import admin
from .models import Expense

class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "amount", "user", "date")
    list_filter = ("category", "title", "date")  # 👈 filters on sidebar
    search_fields = ("title", "category")

admin.site.register(Expense, ExpenseAdmin)
