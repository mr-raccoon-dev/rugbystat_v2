from django.contrib import admin
from django.contrib.admin.filters import AllValuesFieldListFilter

from .forms import SourceForm
from .models import Source, SourceObject, Document


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
    readonly_fields = ('preview',)
    action_form = SourceForm
    actions = ['set_source_action']
    filter_horizontal = ('tag', 'versions')
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

    def set_source_action(self, request, queryset):
        source = request.POST['source']
        updated = queryset.update(source=source)
        messages.success(request, 
                         '{0} documents were updated'.format(updated))
    set_source_action.short_description = u'Update source'
