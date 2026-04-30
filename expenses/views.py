from django.shortcuts import render, redirect
from .models import Expense
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import Expense
from django.db.models import Sum
from django.utils.dateparse import parse_date
import csv
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from django.db.models.functions import TruncMonth
from .models import Expense, Income
from django.db.models import Sum
from django.db.models import Sum
import json
from django.db.models import Sum
from django.db.models.functions import TruncMonth







@login_required(login_url='login')
def add_expense(request):
    if request.method == 'POST':
        title = request.POST['title']
        amount = request.POST['amount']
        category = request.POST['category']

        # Save with the logged-in user
        Expense.objects.create(title=title, amount=amount, category=category, user=request.user)
        return redirect('dashboard')
    return render(request, 'expenses/add_expense.html')

@login_required(login_url='login')
def export_csv(request):
    expenses = Expense.objects.filter(user=request.user)

    response = HttpResponse(content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename=expenses.csv'

    writer = csv.writer(response)
    writer.writerow(["Title", "Amount", "Category", "Date"])

    for exp in expenses:
        writer.writerow([exp.title, exp.amount, exp.category, exp.date])

    return response

@login_required(login_url='login')
def export_pdf(request):
    expenses = Expense.objects.filter(user=request.user)

    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = 'attachment; filename=expenses.pdf'

    p = canvas.Canvas(response, pagesize=letter)
    y = 750
    p.drawString(200, 800, "Expense Report")

    for exp in expenses:
        p.drawString(50, y, f"{exp.date} - {exp.title} - ${exp.amount} - {exp.category}")
        y -= 25
        if y < 50:
            p.showPage()
            y = 750

    p.showPage()
    p.save()
    return response

@login_required(login_url='login')
def edit_expense(request, expense_id):  # 👈 must match URL param
    expense = Expense.objects.get(id=expense_id)

    if request.method == "POST":
        expense.title = request.POST.get("title")
        expense.category = request.POST.get("category")
        expense.amount = request.POST.get("amount")
        expense.save()
        return redirect("dashboard")

    return render(request, "expenses/edit_expense.html", {"expense": expense})


@login_required(login_url='login')
def delete_expense(request, expense_id):
    # Get the record using the passed ID
    expense = Expense.objects.get(id=expense_id)

    # Delete the record
    expense.delete()

    # Redirect back to dashboard
    return redirect('dashboard')

@login_required(login_url='login')
def add_income(request):
    if request.method == "POST":
        Income.objects.create(
            user=request.user,
            source=request.POST.get("source"),
            amount=request.POST.get("amount")
        )
        return redirect("dashboard")

    return render(request, "expenses/add_income.html")


# ================= AUTH VIEWS ====================

# Register User
def register_page(request):
    # If form submitted
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken")
            return redirect('register')

        # Create user
        user = User.objects.create_user(username=username, password=password)
        messages.success(request, "Account created successfully! Please log in.")
        return redirect('login')

    return render(request, 'expenses/register.html')


# Login User
def login_page(request):
    # If form submitted
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # Authenticate user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user) # Start session
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid Username or Password")
            return redirect('login')

    return render(request, 'expenses/login.html')


# Logout User
def logout_user(request):
    logout(request)
    return redirect('login')

from django.db.models import Sum
from .models import Expense, Income


@login_required(login_url='login')
def dashboard(request):
    expenses = Expense.objects.filter(user=request.user)
    incomes = Income.objects.filter(user=request.user)

    # Total spent (all time)
    total = expenses.aggregate(total=Sum('amount'))['total'] or 0

    # Total income (all time) - includes "opening balance" and salary entries
    total_income = incomes.aggregate(total=Sum('amount'))['total'] or 0

    # Balance: what you have left
    balance = total_income - total

    # Monthly budget
    budget = 300
    remaining_budget = budget - total
    budget_exceeded = remaining_budget < 0

    # 🔹 GROUP EXPENSES BY MONTH
    monthly_expenses = (
        expenses
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(total=Sum('amount'))
        .order_by('-month')
    )

    context = {
        'expenses': expenses,
        'total': total,
        'total_income': total_income,
        'balance': balance,
        'budget': budget,
        'remaining_budget': remaining_budget,
        'budget_exceeded': budget_exceeded,
        'monthly_expenses': monthly_expenses,
    }

    return render(request, 'expenses/dashboard.html', context)