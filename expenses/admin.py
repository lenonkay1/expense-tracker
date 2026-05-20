from django.contrib import admin

from .models import Expense, Income, SavingsGoal, UserProfile

admin.site.register(Expense)
admin.site.register(Income)
admin.site.register(UserProfile)
admin.site.register(SavingsGoal)
