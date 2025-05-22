from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from core.models import BaseModel
from django_ckeditor_5.fields import CKEditor5Field
from django.conf import settings


class WikiPage(BaseModel):
    """Model for wiki pages"""
    slug = models.SlugField(_('Slug'), unique=True)
    order = models.IntegerField(_('Order'), default=0)
    is_active = models.BooleanField(_('Active'), default=True)
    created_at = models.DateTimeField(_('Created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated at'), auto_now=True)

    class Meta:
        verbose_name = _('Wiki Page')
        verbose_name_plural = _('Wiki Pages')
        ordering = ['order', 'translations__title']

    def save(self, *args, **kwargs):
        if not self.slug:
            pt_translation = self.translations.filter(language='pt').first()
            if pt_translation:
                self.slug = slugify(pt_translation.title)
        super(WikiPage, self).save(*args, **kwargs)

    def __str__(self):
        pt_translation = self.translations.filter(language='pt').first()
        return pt_translation.title if pt_translation else f"{_('Wiki Page')} {self.pk}"


class WikiPageTranslation(BaseModel):
    LANGUAGES = [
        ('pt', _('Portuguese')),
        ('en', _('English')),
        ('es', _('Spanish')),
    ]

    page = models.ForeignKey(
        WikiPage,
        on_delete=models.CASCADE,
        related_name='translations',
        verbose_name=_("Wiki Page")
    )
    language = models.CharField(
        max_length=5,
        choices=LANGUAGES,
        verbose_name=_("Language")
    )
    title = models.CharField(
        max_length=200,
        verbose_name=_("Title")
    )
    content = CKEditor5Field(
        verbose_name=_("Content"),
        config_name='extends'
    )

    class Meta:
        unique_together = ('page', 'language')
        verbose_name = _("Wiki Page Translation")
        verbose_name_plural = _("Wiki Page Translations")

    def __str__(self):
        return f"{self.title} ({self.get_language_display()})"


class WikiSection(BaseModel):
    """Model for wiki sections"""
    page = models.ForeignKey(
        WikiPage,
        on_delete=models.CASCADE,
        related_name='sections',
        verbose_name=_("Wiki Page")
    )
    order = models.IntegerField(_('Order'), default=0)
    section_type = models.CharField(
        max_length=50,
        choices=[
            ('info', _('Information')),
            ('guide', _('Guide')),
            ('warning', _('Warning')),
            ('note', _('Note')),
            ('tip', _('Tip')),
        ],
        default='info',
        verbose_name=_("Section Type")
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("Icon")
    )
    is_active = models.BooleanField(_('Active'), default=True)
    created_at = models.DateTimeField(_('Created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated at'), auto_now=True)

    class Meta:
        verbose_name = _('Wiki Section')
        verbose_name_plural = _('Wiki Sections')
        ordering = ['page', 'order', 'translations__title']

    def __str__(self):
        pt_translation = self.translations.filter(language='pt').first()
        return pt_translation.title if pt_translation else f"{_('Wiki Section')} {self.pk}"


class WikiSectionTranslation(BaseModel):
    LANGUAGES = [
        ('pt', _('Portuguese')),
        ('en', _('English')),
        ('es', _('Spanish')),
    ]

    section = models.ForeignKey(
        WikiSection,
        on_delete=models.CASCADE,
        related_name='translations',
        verbose_name=_("Wiki Section")
    )
    language = models.CharField(
        max_length=5,
        choices=LANGUAGES,
        verbose_name=_("Language")
    )
    title = models.CharField(
        max_length=200,
        verbose_name=_("Title")
    )
    content = CKEditor5Field(
        verbose_name=_("Content"),
        config_name='extends'
    )
    subtitle = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Subtitle")
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("Description")
    )

    class Meta:
        unique_together = ('section', 'language')
        verbose_name = _("Wiki Section Translation")
        verbose_name_plural = _("Wiki Section Translations")

    def __str__(self):
        return f"{self.title} ({self.get_language_display()})"


class WikiUpdate(BaseModel):
    """Model for server updates"""
    version = models.CharField(_('Version'), max_length=50)
    release_date = models.DateField(_('Release Date'))
    is_active = models.BooleanField(_('Active'), default=True)
    created_at = models.DateTimeField(_('Created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated at'), auto_now=True)

    class Meta:
        verbose_name = _('Server Update')
        verbose_name_plural = _('Server Updates')
        ordering = ['-release_date', '-version']

    def __str__(self):
        return f"v{self.version} - {self.release_date}"


class WikiUpdateTranslation(BaseModel):
    LANGUAGES = [
        ('pt', _('Portuguese')),
        ('en', _('English')),
        ('es', _('Spanish')),
    ]

    update = models.ForeignKey(
        WikiUpdate,
        on_delete=models.CASCADE,
        related_name='translations',
        verbose_name=_("Server Update")
    )
    language = models.CharField(
        max_length=5,
        choices=LANGUAGES,
        verbose_name=_("Language")
    )
    content = CKEditor5Field(
        verbose_name=_("Content"),
        config_name='extends'
    )

    class Meta:
        unique_together = ('update', 'language')
        verbose_name = _("Server Update Translation")
        verbose_name_plural = _("Server Update Translations")

    def __str__(self):
        return f"v{self.update.version} - {self.get_language_display()}"


class WikiEvent(BaseModel):
    """Model for server events"""
    EVENT_TYPES = (
        ('regular', _('Regular')),
        ('special', _('Special')),
    )

    event_type = models.CharField(_('Event Type'), max_length=20, choices=EVENT_TYPES)
    is_active = models.BooleanField(_('Active'), default=True)
    created_at = models.DateTimeField(_('Created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated at'), auto_now=True)

    class Meta:
        verbose_name = _('Server Event')
        verbose_name_plural = _('Server Events')
        ordering = ['event_type', 'translations__title']

    def __str__(self):
        pt_translation = self.translations.filter(language='pt').first()
        return pt_translation.title if pt_translation else f"{_('Event')} {self.pk}"


class WikiEventTranslation(BaseModel):
    LANGUAGES = [
        ('pt', _('Portuguese')),
        ('en', _('English')),
        ('es', _('Spanish')),
    ]

    event = models.ForeignKey(
        WikiEvent,
        on_delete=models.CASCADE,
        related_name='translations',
        verbose_name=_("Server Event")
    )
    language = models.CharField(
        max_length=5,
        choices=LANGUAGES,
        verbose_name=_("Language")
    )
    title = models.CharField(
        max_length=200,
        verbose_name=_("Title")
    )
    description = CKEditor5Field(
        verbose_name=_("Description"),
        config_name='extends'
    )
    schedule = models.CharField(
        max_length=200,
        verbose_name=_("Schedule")
    )
    requirements = CKEditor5Field(
        verbose_name=_("Requirements"),
        config_name='extends',
        blank=True
    )
    rewards = CKEditor5Field(
        verbose_name=_("Rewards"),
        config_name='extends',
        blank=True
    )

    class Meta:
        unique_together = ('event', 'language')
        verbose_name = _("Server Event Translation")
        verbose_name_plural = _("Server Event Translations")

    def __str__(self):
        return f"{self.title} ({self.get_language_display()})"


class WikiRate(BaseModel):
    rate_type = models.CharField(max_length=50, choices=[
        ('exp', _('Experience')),
        ('drop', _('Drop')),
        ('adena', _('Adena')),
        ('spoil', _('Spoil')),
        ('quest', _('Quest')),
    ])
    value = models.FloatField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Wiki Rate')
        verbose_name_plural = _('Wiki Rates')
        ordering = ['rate_type', 'created_at']

    def __str__(self):
        return f"{self.get_rate_type_display()}: {self.value}x"


class WikiRateTranslation(BaseModel):
    rate = models.ForeignKey(WikiRate, on_delete=models.CASCADE, related_name='translations')
    language = models.CharField(max_length=10, choices=settings.LANGUAGES)
    title = models.CharField(max_length=200)
    content = models.TextField()

    class Meta:
        unique_together = ('rate', 'language')
        verbose_name = _('Wiki Rate Translation')
        verbose_name_plural = _('Wiki Rate Translations')

    def __str__(self):
        return f"{self.title} ({self.language})"


class WikiFeature(BaseModel):
    feature_type = models.CharField(max_length=50, choices=[
        ('custom', _('Custom')),
        ('gameplay', _('Gameplay')),
        ('qol', _('Quality of Life')),
        ('vip', _('VIP')),
        ('anticheat', _('Anti-Cheat')),
        ('community', _('Community')),
    ])
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Wiki Feature')
        verbose_name_plural = _('Wiki Features')
        ordering = ['feature_type', 'created_at']

    def __str__(self):
        return self.translations.get().title


class WikiFeatureTranslation(BaseModel):
    feature = models.ForeignKey(WikiFeature, on_delete=models.CASCADE, related_name='translations')
    language = models.CharField(max_length=10, choices=settings.LANGUAGES)
    title = models.CharField(max_length=200)
    content = models.TextField()

    class Meta:
        unique_together = ('feature', 'language')
        verbose_name = _('Wiki Feature Translation')
        verbose_name_plural = _('Wiki Feature Translations')

    def __str__(self):
        return f"{self.title} ({self.language})"
