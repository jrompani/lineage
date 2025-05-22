from django.shortcuts import render, get_object_or_404
from django.utils.translation import gettext_lazy as _, get_language
from django.views.generic import ListView, DetailView, TemplateView
from django.utils import translation
from django.db.models import Prefetch
from .models import (
    WikiPage, WikiPageTranslation,
    WikiSection, WikiSectionTranslation,
    WikiUpdate, WikiUpdateTranslation,
    WikiEvent, WikiEventTranslation,
    WikiRate, WikiRateTranslation,
    WikiFeature, WikiFeatureTranslation
)


class WikiHomeView(TemplateView):
    template_name = 'wiki/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        language = get_language()
        
        # Get active pages with translations
        pages = WikiPage.objects.filter(
            is_active=True,
            translations__language=language
        ).prefetch_related(
            Prefetch(
                'translations',
                queryset=WikiPageTranslation.objects.filter(language=language),
                to_attr='_translation'
            )
        )
        
        # Add pages with their translations to context
        context['pages'] = [
            {
                'page': page,
                'translation': page._translation[0] if page._translation else None
            }
            for page in pages
        ]
        
        return context


class WikiGeneralView(TemplateView):
    template_name = 'wiki/general.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        language = get_language()
        
        # Get server information
        server_info = WikiPage.objects.filter(
            is_active=True,
            translations__language=language,
            translations__title__icontains='server'
        ).prefetch_related(
            Prefetch(
                'translations',
                queryset=WikiPageTranslation.objects.filter(language=language),
                to_attr='_translation'
            )
        )
        
        # Get game features
        game_features = WikiFeature.objects.filter(
            is_active=True,
            feature_type='gameplay',
            translations__language=language
        ).prefetch_related(
            Prefetch(
                'translations',
                queryset=WikiFeatureTranslation.objects.filter(language=language),
                to_attr='_translation'
            )
        )
        
        # Get getting started guides
        getting_started = WikiPage.objects.filter(
            is_active=True,
            translations__language=language,
            translations__title__icontains='getting started'
        ).prefetch_related(
            Prefetch(
                'translations',
                queryset=WikiPageTranslation.objects.filter(language=language),
                to_attr='_translation'
            )
        )
        
        # Get community guidelines
        community_guidelines = WikiPage.objects.filter(
            is_active=True,
            translations__language=language,
            translations__title__icontains='guidelines'
        ).prefetch_related(
            Prefetch(
                'translations',
                queryset=WikiPageTranslation.objects.filter(language=language),
                to_attr='_translation'
            )
        )
        
        # Get technical support
        technical_support = WikiPage.objects.filter(
            is_active=True,
            translations__language=language,
            translations__title__icontains='support'
        ).prefetch_related(
            Prefetch(
                'translations',
                queryset=WikiPageTranslation.objects.filter(language=language),
                to_attr='_translation'
            )
        )
        
        # Add all data to context
        context.update({
            'server_info': [
                {
                    'page': info,
                    'translation': info._translation[0] if info._translation else None
                }
                for info in server_info
            ],
            'game_features': [
                {
                    'feature': feature,
                    'translation': feature._translation[0] if feature._translation else None
                }
                for feature in game_features
            ],
            'getting_started': [
                {
                    'page': guide,
                    'translation': guide._translation[0] if guide._translation else None
                }
                for guide in getting_started
            ],
            'community_guidelines': [
                {
                    'page': guideline,
                    'translation': guideline._translation[0] if guideline._translation else None
                }
                for guideline in community_guidelines
            ],
            'technical_support': [
                {
                    'page': support,
                    'translation': support._translation[0] if support._translation else None
                }
                for support in technical_support
            ]
        })
        
        return context


class WikiRatesView(TemplateView):
    template_name = 'wiki/rates.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        language = get_language()
        
        # Get all rate types
        exp_rates = WikiRate.objects.filter(
            is_active=True,
            rate_type='exp',
            translations__language=language
        ).prefetch_related(
            Prefetch(
                'translations',
                queryset=WikiRateTranslation.objects.filter(language=language),
                to_attr='_translation'
            )
        )
        
        drop_rates = WikiRate.objects.filter(
            is_active=True,
            rate_type='drop',
            translations__language=language
        ).prefetch_related(
            Prefetch(
                'translations',
                queryset=WikiRateTranslation.objects.filter(language=language),
                to_attr='_translation'
            )
        )
        
        adena_rates = WikiRate.objects.filter(
            is_active=True,
            rate_type='adena',
            translations__language=language
        ).prefetch_related(
            Prefetch(
                'translations',
                queryset=WikiRateTranslation.objects.filter(language=language),
                to_attr='_translation'
            )
        )
        
        spoil_rates = WikiRate.objects.filter(
            is_active=True,
            rate_type='spoil',
            translations__language=language
        ).prefetch_related(
            Prefetch(
                'translations',
                queryset=WikiRateTranslation.objects.filter(language=language),
                to_attr='_translation'
            )
        )
        
        quest_rates = WikiRate.objects.filter(
            is_active=True,
            rate_type='quest',
            translations__language=language
        ).prefetch_related(
            Prefetch(
                'translations',
                queryset=WikiRateTranslation.objects.filter(language=language),
                to_attr='_translation'
            )
        )
        
        # Add all rates to context
        context.update({
            'exp_rates': [
                {
                    'rate': rate,
                    'translation': rate._translation[0] if rate._translation else None
                }
                for rate in exp_rates
            ],
            'drop_rates': [
                {
                    'rate': rate,
                    'translation': rate._translation[0] if rate._translation else None
                }
                for rate in drop_rates
            ],
            'adena_rates': [
                {
                    'rate': rate,
                    'translation': rate._translation[0] if rate._translation else None
                }
                for rate in adena_rates
            ],
            'spoil_rates': [
                {
                    'rate': rate,
                    'translation': rate._translation[0] if rate._translation else None
                }
                for rate in spoil_rates
            ],
            'quest_rates': [
                {
                    'rate': rate,
                    'translation': rate._translation[0] if rate._translation else None
                }
                for rate in quest_rates
            ]
        })
        
        return context


class WikiRaidsView(TemplateView):
    template_name = 'wiki/raids.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        language = get_language()
        
        # Get all raid types
        regular_raids = WikiPage.objects.filter(
            is_active=True,
            translations__language=language,
            translations__title__icontains='regular raid'
        ).prefetch_related(
            Prefetch(
                'translations',
                queryset=WikiPageTranslation.objects.filter(language=language),
                to_attr='_translation'
            )
        )
        
        special_raids = WikiPage.objects.filter(
            is_active=True,
            translations__language=language,
            translations__title__icontains='special raid'
        ).prefetch_related(
            Prefetch(
                'translations',
                queryset=WikiPageTranslation.objects.filter(language=language),
                to_attr='_translation'
            )
        )
        
        world_raids = WikiPage.objects.filter(
            is_active=True,
            translations__language=language,
            translations__title__icontains='world raid'
        ).prefetch_related(
            Prefetch(
                'translations',
                queryset=WikiPageTranslation.objects.filter(language=language),
                to_attr='_translation'
            )
        )
        
        # Add all raids to context
        context.update({
            'regular_raids': [
                {
                    'raid': raid,
                    'translation': raid._translation[0] if raid._translation else None
                }
                for raid in regular_raids
            ],
            'special_raids': [
                {
                    'raid': raid,
                    'translation': raid._translation[0] if raid._translation else None
                }
                for raid in special_raids
            ],
            'world_raids': [
                {
                    'raid': raid,
                    'translation': raid._translation[0] if raid._translation else None
                }
                for raid in world_raids
            ]
        })
        
        return context


class WikiAssistanceView(TemplateView):
    template_name = 'wiki/assistance.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        language = get_language()
        
        # Get common issues
        common_issues = WikiPage.objects.filter(
            is_active=True,
            translations__language=language,
            translations__title__icontains='issue'
        ).prefetch_related(
            Prefetch(
                'translations',
                queryset=WikiPageTranslation.objects.filter(language=language),
                to_attr='_translation'
            )
        )
        
        # Get FAQs
        faqs = WikiPage.objects.filter(
            is_active=True,
            translations__language=language,
            translations__title__icontains='faq'
        ).prefetch_related(
            Prefetch(
                'translations',
                queryset=WikiPageTranslation.objects.filter(language=language),
                to_attr='_translation'
            )
        )
        
        # Get technical support
        technical_support = WikiPage.objects.filter(
            is_active=True,
            translations__language=language,
            translations__title__icontains='support'
        ).prefetch_related(
            Prefetch(
                'translations',
                queryset=WikiPageTranslation.objects.filter(language=language),
                to_attr='_translation'
            )
        )
        
        # Add all data to context
        context.update({
            'common_issues': [
                {
                    'issue': issue,
                    'translation': issue._translation[0] if issue._translation else None
                }
                for issue in common_issues
            ],
            'faqs': [
                {
                    'faq': faq,
                    'translation': faq._translation[0] if faq._translation else None
                }
                for faq in faqs
            ],
            'technical_support': [
                {
                    'support': support,
                    'translation': support._translation[0] if support._translation else None
                }
                for support in technical_support
            ]
        })
        
        return context


class WikiEventsView(ListView):
    template_name = 'wiki/events.html'
    context_object_name = 'events'

    def get_queryset(self):
        language = get_language()
        return WikiEvent.objects.filter(
            is_active=True,
            translations__language=language
        ).prefetch_related(
            Prefetch(
                'translations',
                queryset=WikiEventTranslation.objects.filter(language=language),
                to_attr='_translation'
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        language = get_language()
        
        # Get regular events
        regular_events = WikiEvent.objects.filter(
            is_active=True,
            event_type='regular',
            translations__language=language
        ).prefetch_related(
            Prefetch(
                'translations',
                queryset=WikiEventTranslation.objects.filter(language=language),
                to_attr='_translation'
            )
        )
        
        # Get special events
        special_events = WikiEvent.objects.filter(
            is_active=True,
            event_type='special',
            translations__language=language
        ).prefetch_related(
            Prefetch(
                'translations',
                queryset=WikiEventTranslation.objects.filter(language=language),
                to_attr='_translation'
            )
        )
        
        # Add events to context
        context.update({
            'regular_events': [
                {
                    'event': event,
                    'translation': event._translation[0] if event._translation else None
                }
                for event in regular_events
            ],
            'special_events': [
                {
                    'event': event,
                    'translation': event._translation[0] if event._translation else None
                }
                for event in special_events
            ]
        })
        
        return context


class WikiUpdatesView(ListView):
    template_name = 'wiki/updates.html'
    context_object_name = 'updates'

    def get_queryset(self):
        language = get_language()
        return WikiUpdate.objects.filter(
            is_active=True,
            translations__language=language
        ).prefetch_related(
            Prefetch(
                'translations',
                queryset=WikiUpdateTranslation.objects.filter(language=language),
                to_attr='_translation'
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add updates with translations to context
        context['updates'] = [
            {
                'update': update,
                'translation': update._translation[0] if update._translation else None
            }
            for update in self.get_queryset()
        ]
        
        return context


class WikiFeaturesView(TemplateView):
    template_name = 'wiki/features.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        language = get_language()
        
        # Get all feature types
        custom_features = WikiFeature.objects.filter(
            is_active=True,
            feature_type='custom',
            translations__language=language
        ).prefetch_related(
            Prefetch(
                'translations',
                queryset=WikiFeatureTranslation.objects.filter(language=language),
                to_attr='_translation'
            )
        )
        
        gameplay_features = WikiFeature.objects.filter(
            is_active=True,
            feature_type='gameplay',
            translations__language=language
        ).prefetch_related(
            Prefetch(
                'translations',
                queryset=WikiFeatureTranslation.objects.filter(language=language),
                to_attr='_translation'
            )
        )
        
        qol_features = WikiFeature.objects.filter(
            is_active=True,
            feature_type='qol',
            translations__language=language
        ).prefetch_related(
            Prefetch(
                'translations',
                queryset=WikiFeatureTranslation.objects.filter(language=language),
                to_attr='_translation'
            )
        )
        
        vip_features = WikiFeature.objects.filter(
            is_active=True,
            feature_type='vip',
            translations__language=language
        ).prefetch_related(
            Prefetch(
                'translations',
                queryset=WikiFeatureTranslation.objects.filter(language=language),
                to_attr='_translation'
            )
        )
        
        anti_cheat_features = WikiFeature.objects.filter(
            is_active=True,
            feature_type='anti_cheat',
            translations__language=language
        ).prefetch_related(
            Prefetch(
                'translations',
                queryset=WikiFeatureTranslation.objects.filter(language=language),
                to_attr='_translation'
            )
        )
        
        community_features = WikiFeature.objects.filter(
            is_active=True,
            feature_type='community',
            translations__language=language
        ).prefetch_related(
            Prefetch(
                'translations',
                queryset=WikiFeatureTranslation.objects.filter(language=language),
                to_attr='_translation'
            )
        )
        
        # Add all features to context
        context.update({
            'custom_features': [
                {
                    'feature': feature,
                    'translation': feature._translation[0] if feature._translation else None
                }
                for feature in custom_features
            ],
            'gameplay_features': [
                {
                    'feature': feature,
                    'translation': feature._translation[0] if feature._translation else None
                }
                for feature in gameplay_features
            ],
            'qol_features': [
                {
                    'feature': feature,
                    'translation': feature._translation[0] if feature._translation else None
                }
                for feature in qol_features
            ],
            'vip_features': [
                {
                    'feature': feature,
                    'translation': feature._translation[0] if feature._translation else None
                }
                for feature in vip_features
            ],
            'anti_cheat_features': [
                {
                    'feature': feature,
                    'translation': feature._translation[0] if feature._translation else None
                }
                for feature in anti_cheat_features
            ],
            'community_features': [
                {
                    'feature': feature,
                    'translation': feature._translation[0] if feature._translation else None
                }
                for feature in community_features
            ]
        })
        
        return context


class WikiPageDetailView(DetailView):
    template_name = 'wiki/page.html'
    model = WikiPage
    context_object_name = 'page'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        language = get_language()
        return WikiPage.objects.filter(
            is_active=True,
            translations__language=language
        ).prefetch_related(
            Prefetch(
                'translations',
                queryset=WikiPageTranslation.objects.filter(language=language),
                to_attr='_translation'
            ),
            Prefetch(
                'sections',
                queryset=WikiSection.objects.filter(is_active=True).prefetch_related(
                    Prefetch(
                        'translations',
                        queryset=WikiSectionTranslation.objects.filter(language=language),
                        to_attr='_translation'
                    )
                )
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add page translation to context
        context['page'] = {
            'page': self.object,
            'translation': self.object._translation[0] if self.object._translation else None
        }
        
        # Add sections with translations to context
        context['sections'] = [
            {
                'section': section,
                'translation': section._translation[0] if section._translation else None
            }
            for section in self.object.sections.all()
        ]
        
        return context


class WikiSectionDetailView(DetailView):
    template_name = 'wiki/section.html'
    model = WikiSection
    context_object_name = 'section'
    pk_url_kwarg = 'pk'

    def get_queryset(self):
        language = get_language()
        return WikiSection.objects.filter(
            is_active=True,
            translations__language=language
        ).prefetch_related(
            Prefetch(
                'translations',
                queryset=WikiSectionTranslation.objects.filter(language=language),
                to_attr='_translation'
            ),
            Prefetch(
                'page',
                queryset=WikiPage.objects.filter(is_active=True).prefetch_related(
                    Prefetch(
                        'translations',
                        queryset=WikiPageTranslation.objects.filter(language=language),
                        to_attr='_translation'
                    )
                )
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add section translation to context
        context['section'] = {
            'section': self.object,
            'translation': self.object._translation[0] if self.object._translation else None
        }
        
        # Add page with translation to context
        context['page'] = {
            'page': self.object.page,
            'translation': self.object.page._translation[0] if self.object.page._translation else None
        }
        
        return context
