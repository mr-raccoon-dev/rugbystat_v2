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
        ('source__title', DropdownFilter), 
        'source__type', 
        'is_image', 
        'is_deleted', 
    )
    list_display = (
        'title', 'source', 'preview'
    )
    search_fields = ('title', )
    filter_horizontal = ('tag', 'versions')
    readonly_fields = ('preview',)
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'preview')
            }
        ),
        (None, {
            'fields': (('source', 'source_issue'), )
            }
        ),
        (None, {
            'fields': ('dropbox', 'dropbox_path', 'dropbox_thumb')
            }
        ),
        (None, {
            'fields': (('year', 'month', 'date'),)
            }
        ),
        (None, {
            'fields': ('versions', 'tag')
            }
        ),
        (None, {
            'fields': (('is_image', 'is_deleted'),)
            }
        ),
    )

    def preview(self, obj):
        return '<img src="{}"/>'.format(obj.dropbox_thumb)
    preview.allow_tags = True
