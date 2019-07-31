from django.conf.urls import include, url
from django.views.generic import TemplateView

from ..views import by_person_detail, by_person_list

urlpatterns = [
    url(
        r"^$",
        TemplateView.as_view(template_name="directory/index.html"),
        name="directory-index",
    ),
    url(r"^table/", include("directory.urls.table")),
    url(r"^visual-1col/", include("directory.urls.visual_1col")),
    url(r"^visual-4col/", include("directory.urls.visual_4col")),
    url(r"^by-person/$", by_person_list, name="directory-by-person-list"),
    url(
        r"^by-person/(?P<slug>[\w-]+)/$",
        by_person_detail,
        name="directory-by-person-detail",
    ),
]
