import csv
import json

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from .models import Expense, Income, SavingsGoal, UserProfile
from .utils import apply_expense_filters, get_user_profile


def _export_queryset(request):
    qs = Expense.objects.filter(user=request.user).order_by("-date")
    return apply_expense_filters(qs, request)


@login_required(login_url="login")
def dashboard(request):
    profile = get_user_profile(request.user)
    currency = profile.currency

    all_expenses = Expense.objects.filter(user=request.user)
    expenses = apply_expense_filters(all_expenses, request).order_by("-date")
    incomes = Income.objects.filter(user=request.user).order_by("-date")[:10]

    total = expenses.aggregate(total=Sum("amount"))["total"] or 0
    total_income = Income.objects.filter(user=request.user).aggregate(
        total=Sum("amount")
    )["total"] or 0
    balance = total_income - (
        all_expenses.aggregate(total=Sum("amount"))["total"] or 0
    )

    budget = profile.monthly_budget
    remaining_budget = budget - total
    budget_exceeded = remaining_budget < 0
    over_budget_amount = abs(remaining_budget) if budget_exceeded else 0

    low_balance_alert = (
        profile.low_balance_threshold > 0
        and balance <= profile.low_balance_threshold
    )

    monthly_expenses = (
        all_expenses.annotate(month=TruncMonth("date"))
        .values("month")
        .annotate(total=Sum("amount"))
        .order_by("-month")
    )

    category_data = [
        {
            "category": row["category"],
            "total": float(row["total"] or 0),
        }
        for row in expenses.values("category")
        .annotate(total=Sum("amount"))
        .order_by("-total")
    ]

    savings_goals = SavingsGoal.objects.filter(user=request.user)

    context = {
        "expenses": expenses,
        "incomes": incomes,
        "total": total,
        "total_income": total_income,
        "balance": balance,
        "budget": budget,
        "remaining_budget": remaining_budget,
        "budget_exceeded": budget_exceeded,
        "over_budget_amount": over_budget_amount,
        "low_balance_alert": low_balance_alert,
        "low_balance_threshold": profile.low_balance_threshold,
        "monthly_expenses": monthly_expenses,
        "category_data": json.dumps(category_data),
        "currency": currency,
        "savings_goals": savings_goals,
        "filters": {
            "search": request.GET.get("search", ""),
            "category": request.GET.get("category", "All"),
            "start_date": request.GET.get("start_date", ""),
            "end_date": request.GET.get("end_date", ""),
            "period": request.GET.get("period", "all"),
        },
        "export_query": request.GET.urlencode(),
        "currency_choices": UserProfile.CURRENCY_CHOICES,
    }
    return render(request, "expenses/dashboard.html", context)


@login_required(login_url="login")
def profile_settings(request):
    profile = get_user_profile(request.user)

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "settings":
            profile.monthly_budget = request.POST.get("monthly_budget") or 300
            profile.currency = request.POST.get("currency", "$")
            profile.low_balance_threshold = (
                request.POST.get("low_balance_threshold") or 0
            )
            profile.save()
            messages.success(request, "Settings updated.")
            return redirect("profile")

        if action == "password":
            current = request.POST.get("current_password", "")
            new_pass = request.POST.get("new_password", "")
            confirm = request.POST.get("confirm_password", "")
            if not request.user.check_password(current):
                messages.error(request, "Current password is incorrect.")
            elif new_pass != confirm:
                messages.error(request, "New passwords do not match.")
            elif len(new_pass) < 6:
                messages.error(request, "Password must be at least 6 characters.")
            else:
                request.user.set_password(new_pass)
                request.user.save()
                messages.success(request, "Password changed. Please log in again.")
                return redirect("login")

        if action == "add_goal":
            name = request.POST.get("goal_name", "").strip()
            target = request.POST.get("target_amount")
            saved = request.POST.get("saved_amount") or 0
            if name and target:
                SavingsGoal.objects.create(
                    user=request.user,
                    name=name,
                    target_amount=target,
                    saved_amount=saved,
                )
                messages.success(request, "Savings goal added.")
            return redirect("profile")

        if action == "update_goal":
            goal = get_object_or_404(
                SavingsGoal, id=request.POST.get("goal_id"), user=request.user
            )
            goal.saved_amount = request.POST.get("saved_amount") or goal.saved_amount
            goal.save()
            messages.success(request, f"Updated progress for {goal.name}.")
            return redirect("profile")

        if action == "delete_goal":
            goal = get_object_or_404(
                SavingsGoal, id=request.POST.get("goal_id"), user=request.user
            )
            goal.delete()
            messages.success(request, "Savings goal removed.")
            return redirect("profile")

    return render(
        request,
        "expenses/profile.html",
        {
            "profile": profile,
            "goals": SavingsGoal.objects.filter(user=request.user),
            "currency_choices": UserProfile.CURRENCY_CHOICES,
        },
    )


@login_required(login_url="login")
def add_expense(request):
    if request.method == "POST":
        Expense.objects.create(
            title=request.POST["title"],
            amount=request.POST["amount"],
            category=request.POST["category"],
            notes=request.POST.get("notes", ""),
            user=request.user,
        )
        messages.success(request, "Expense added.")
        return redirect("dashboard")
    return render(request, "expenses/add_expense.html")


@login_required(login_url="login")
def add_income(request):
    if request.method == "POST":
        Income.objects.create(
            user=request.user,
            source=request.POST.get("source"),
            amount=request.POST.get("amount"),
        )
        messages.success(request, "Income added.")
        return redirect("dashboard")
    return render(request, "expenses/add_income.html")


@login_required(login_url="login")
def edit_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id, user=request.user)
    if request.method == "POST":
        expense.title = request.POST.get("title")
        expense.category = request.POST.get("category")
        expense.amount = request.POST.get("amount")
        expense.notes = request.POST.get("notes", "")
        expense.save()
        messages.success(request, "Expense updated.")
        return redirect("dashboard")
    return render(
        request,
        "expenses/edit_expense.html",
        {
            "expense": expense,
            "title_choices": Expense.TITLE_CHOICES,
            "category_choices": Expense.CATEGORY_CHOICES,
        },
    )


@login_required(login_url="login")
def delete_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id, user=request.user)
    expense.delete()
    messages.success(request, "Expense deleted.")
    return redirect("dashboard")


@login_required(login_url="login")
def export_csv(request):
    expenses = _export_queryset(request)
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = "attachment; filename=expenses.csv"
    writer = csv.writer(response)
    writer.writerow(["Title", "Amount", "Category", "Date", "Notes"])
    for exp in expenses:
        writer.writerow([exp.title, exp.amount, exp.category, exp.date, exp.notes])
    return response


@login_required(login_url="login")
def export_pdf(request):
    expenses = _export_queryset(request)
    profile = get_user_profile(request.user)
    sym = profile.currency
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = "attachment; filename=expenses.pdf"
    p = canvas.Canvas(response, pagesize=letter)
    y = 750
    p.drawString(200, 800, "Expense Report")
    for exp in expenses:
        line = f"{exp.date} - {exp.title} - {sym}{exp.amount} - {exp.category}"
        p.drawString(50, y, line)
        y -= 25
        if y < 50:
            p.showPage()
            y = 750
    p.showPage()
    p.save()
    return response


def register_page(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        confirm = request.POST.get("password_confirm", "")

        if password != confirm:
            messages.error(request, "Passwords do not match.")
            return redirect("register")
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken")
            return redirect("register")

        User.objects.create_user(username=username, password=password)
        messages.success(request, "Account created successfully! Please log in.")
        return redirect("login")
    return render(request, "expenses/register.html")


def login_page(request):
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST["username"],
            password=request.POST["password"],
        )
        if user is not None:
            login(request, user)
            return redirect("dashboard")
        messages.error(request, "Invalid Username or Password")
        return redirect("login")
    return render(request, "expenses/login.html")


def logout_user(request):
    logout(request)
    return redirect("login")
