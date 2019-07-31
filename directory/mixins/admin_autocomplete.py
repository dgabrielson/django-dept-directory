from django.contrib.admin.views.autocomplete import AutocompleteJsonView
from django.http import Http404, JsonResponse

##############################################################


class LabelAutocompleteJsonView(AutocompleteJsonView):
    """
    Additional imports::

from django.contrib.admin.views.autocomplete import AutocompleteJsonView
from django.http import Http404, JsonResponse


    In a model admin derived class, use::

    def autocomplete_view(self, request):
        return LabelAutocompleteJsonView.as_view(
            autocomplete_text=self.autocomplete_text,
            model_admin=self)(request)

    def autocomplete_text(self, obj):
        "change this to update the text of autocomplete for this object"
        return str(obj)
    """

    autocomplete_text = str

    def get(self, request, *args, **kwargs):
        """
        Return a JsonResponse with search results of the form:
        {
            results: [{id: "123" text: "foo"}],
            pagination: {more: true}
        }
        """
        if not self.model_admin.get_search_fields(request):
            raise Http404(
                "%s must have search_fields for the autocomplete_view."
                % type(self.model_admin).__name__
            )
        if not self.has_perm(request):
            return JsonResponse({"error": "403 Forbidden"}, status=403)

        self.term = request.GET.get("term", "")
        self.paginator_class = self.model_admin.paginator
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        return JsonResponse(
            {
                "results": [
                    {"id": str(obj.pk), "text": self.autocomplete_text(obj)}
                    for obj in context["object_list"]
                ],
                "pagination": {"more": context["page_obj"].has_next()},
            }
        )
