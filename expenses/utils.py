from datetime import timedelta

from django.db.models import Q
from django.utils import timezone
from django.utils.dateparse import parse_date

from .models import UserProfile


def get_user_profile(user):
    profile, _ = UserProfile.objects.get_or_create(user=user)
    return profile


def apply_expense_filters(queryset, request):
    search = request.GET.get("search", "").strip()
    category = request.GET.get("category", "All")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    period = request.GET.get("period", "all")

    if search:
        queryset = queryset.filter(
            Q(title__icontains=search) | Q(notes__icontains=search)
        )
    if category and category != "All":
        queryset = queryset.filter(category=category)
    if start_date:
        parsed = parse_date(start_date)
        if parsed:
            queryset = queryset.filter(date__gte=parsed)
    if end_date:
        parsed = parse_date(end_date)
        if parsed:
            queryset = queryset.filter(date__lte=parsed)

    if period == "this_month":
        now = timezone.localdate()
        queryset = queryset.filter(date__year=now.year, date__month=now.month)
    elif period == "last_month":
        today = timezone.localdate()
        first_this_month = today.replace(day=1)
        last_month_end = first_this_month - timedelta(days=1)
        queryset = queryset.filter(
            date__year=last_month_end.year,
            date__month=last_month_end.month,
        )

    return queryset
