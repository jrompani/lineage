from django.shortcuts import render, redirect
from functools import wraps
from .models import ApiEndpointToggle
from django.http import JsonResponse
from apps.lineage.server.database import LineageDB
from django.contrib import messages


def endpoint_enabled(endpoint_field):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            toggle = ApiEndpointToggle.objects.first()
            if not toggle or not getattr(toggle, endpoint_field, False):
                return render(request, "errors/404.html", status=404)
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def safe_json_response(func):
    def wrapper(*args, **kwargs):
        data = func(*args, **kwargs)
        if data is None:
            return JsonResponse({"error": "Falha ao obter dados do banco de dados"}, status=400)
        return JsonResponse(data, safe=False)
    return wrapper


def require_lineage_connection(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        db = LineageDB()
        if not db.is_connected():
            messages.error(request, "Banco de dados do Lineage está indisponível no momento.")
            return redirect('profile')
        return view_func(request, *args, **kwargs)
    return wrapper
