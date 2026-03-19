from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect

from .models import Task


@login_required
def update_task_status(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    if request.method == "POST" and request.user in (task.assignee, task.created_by):
        status = request.POST.get("status")
        if status in dict(Task.Status.choices):
            task.status = status
            task.save(update_fields=["status", "updated_at"])
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse({"ok": True, "status": task.status, "status_label": task.get_status_display()})
            messages.success(request, "Статус задачи обновлен.")
            return redirect(f"/?tab=kanban")
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": False, "error": "invalid_status"}, status=400)
    elif request.method == "POST" and request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"ok": False, "error": "forbidden"}, status=403)
    return redirect(f"/?tab=kanban")
