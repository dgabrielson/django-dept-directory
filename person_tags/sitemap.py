"""
Sitemap for person pages app.
"""
from django.contrib.sitemaps import GenericSitemap

from .models import PersonTag, TagGroup

TagGroup_Sitemap = GenericSitemap({"queryset": TagGroup.objects.active()})

PersonTag_Sitemap = GenericSitemap({"queryset": PersonTag.objects.active()})
