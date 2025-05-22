from django.views.generic import ListView
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from .models import DownloadCategory, DownloadLink

class DownloadListView(ListView):
    model = DownloadCategory
    template_name = 'public/downloads.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return DownloadCategory.objects.filter(is_active=True).prefetch_related(
            'downloads'
        ).filter(downloads__is_active=True).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('Downloads')
        return context

def download_redirect(request, pk):
    download = get_object_or_404(DownloadLink, pk=pk, is_active=True)
    download.increment_download_count()
    return redirect(download.url) 