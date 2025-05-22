from django.shortcuts import render, redirect
from ..models import ApiEndpointToggle
from django.views.decorators.http import require_http_methods
from django.contrib.admin.views.decorators import staff_member_required


@staff_member_required
@require_http_methods(["GET", "POST"])
def api_config_panel(request):
    toggle, _ = ApiEndpointToggle.objects.get_or_create(pk=1)

    # Campos que devem ser ignorados
    ignore_fields = {"id", "uuid", "created_at", "created_by", "updated_at", "updated_by"}

    # Campos booleanos que não estão na lista de ignorados
    fields = [
        field.name for field in ApiEndpointToggle._meta.fields
        if field.get_internal_type() == "BooleanField" and field.name not in ignore_fields
    ]

    if request.method == "POST":
        for field in fields:
            setattr(toggle, field, field in request.POST)
        toggle.save()
        return redirect("server:api_config_panel")

    context = {
        "toggle": toggle,
        "fields": fields,
    }
    return render(request, "pages/api_config_panel.html", context)
