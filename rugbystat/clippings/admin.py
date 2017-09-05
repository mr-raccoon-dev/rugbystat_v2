from django.contrib import admin, messages
from django.db.models import FileField

from main.filters import DropdownFilter
from .forms import SourceForm
from .models import Source, SourceObject, Document


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_filter = ('kind', )
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
        ('kind', DropdownFilter), 
        'is_image', 
        'is_deleted', 
    )
    list_display = (
        'id', 'title', 'source', 'kind', 'preview'
    )
    ordering = ('-id', )
    search_fields = ('title', )
    readonly_fields = ('preview', 'tag', )
    action_form = SourceForm
    actions = ['set_source_action']
    filter_horizontal = ('versions', )
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'preview')
            }
        ),
        (None, {
            'fields': (('source', 'source_issue', 'kind'), )
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
    # formfield_overrides = {
    #     FileField: {'widget': admin.widgets.AdminTextInputWidget},
    # }

    def preview(self, obj):
        if obj.is_image:
            return '<img src="{}"/>'.format(obj.dropbox_thumb)
        return '-'
    preview.allow_tags = True

    def set_source_action(self, request, queryset):
        source = request.POST['source']
        source_obj = Source.objects.get(id=source)
        updated = queryset.update(source=source, kind=source_obj.kind)
        messages.success(request, 
                         '{0} documents were updated'.format(updated))
    set_source_action.short_description = u'Update source'
