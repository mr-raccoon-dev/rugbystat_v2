from django.contrib import admin
from django.contrib.admin.filters import AllValuesFieldListFilter

from clippings.models import Source, SourceObject, Document


class DropdownFilter(AllValuesFieldListFilter):
    template = 'admin/dropdown_filter.html'


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_filter = ('type', )
    search_fields = ('title', )


@admin.register(SourceObject)
class SourceObjectAdmin(admin.ModelAdmin):
    list_filter = ('source', 'year', 'date', )
    search_fields = ('source__title', )


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_filter = (
        ('year', DropdownFilter),
        'source__type', 
        'is_image', 
        'is_deleted', 
    )
    search_fields = ('title', )
