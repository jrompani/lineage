from django.shortcuts import get_object_or_404
from django.http import Http404
from apps.main.faq.models import FAQ
from apps.main.news.models import News
from django.utils.translation import get_language, gettext as _
from utils.render_theme_page import render_theme_page


def public_news_list(request):
    latest_news_list = News.objects.filter(is_published=True, is_private=False).order_by('-pub_date')[:5]

    language = get_language()
    news_with_translations = []

    for news in latest_news_list:
        translation = news.translations.filter(language=language).first()
        if translation:
            news_with_translations.append({
                'news': news,
                'translation': translation
            })

    context = {
        'latest_news_list': news_with_translations
    }

    return render_theme_page(request, 'public', 'news_index.html', context)


def public_news_detail(request, slug):
    news = get_object_or_404(News, slug=slug)
    if news.is_private and not request.user.is_authenticated:
        raise Http404(_("Notícia privada não está disponível."))

    language = get_language()
    translation = news.translations.filter(language=language).first()

    if not translation:
        raise Http404(_("Tradução não disponível para esta notícia."))

    context = {
        'news': news,
        'translation': translation
    }

    return render_theme_page(request, 'public', 'news_detail.html', context)


def public_faq_list(request):
    language = get_language()  # Obtém o idioma atual
    public_faqs = FAQ.objects.filter(is_public=True)

    # Obter traduções para o idioma atual
    translated_public_faqs = []
    for faq in public_faqs:
        translation = faq.translations.filter(language=language).first()
        if translation:
            translated_public_faqs.append(translation)

    context = {
        'public_faqs': translated_public_faqs,
    }

    return render_theme_page(request, 'public', 'faq.html', context)
