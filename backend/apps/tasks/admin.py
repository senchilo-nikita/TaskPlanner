from django.contrib import admin

from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "assignee", "created_by", "priority", "status", "due_date")
    list_filter = ("priority", "status")
    search_fields = ("title", "description", "assignee__email", "created_by__email")

