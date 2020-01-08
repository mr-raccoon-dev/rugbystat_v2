from django.contrib import admin, messages

from main.admin import CrossLinkMixin
from main.filters import DropdownFilter
from teams.forms import TagThroughForm

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


class TagInline(admin.TabularInline):
    model = Document.tag.through
    form = TagThroughForm
    extra = 1


@admin.register(Document)
class DocumentAdmin(CrossLinkMixin, admin.ModelAdmin):
    list_display = (
        'id', 'title', 'source', 'kind', 'preview'
    )
    list_select_related = ('source', )
    list_filter = (
        ('year', DropdownFilter),
        ('source__title', DropdownFilter),
        ('kind', DropdownFilter),
        'is_image',
        'is_deleted',
    )
    ordering = ('-id', )
    search_fields = ('title', )

    action_form = SourceForm
    actions = ['set_source_action']

    readonly_fields = ('preview', 'versions', 'tag_links')
    # filter_horizontal = ('versions', )
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
            'fields': ('versions', 'tag_links')
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
    inlines = (
        TagInline,
    )

    def preview(self, obj):
        if obj.is_image:
            return '<img src="{}"/>'.format(obj.dropbox_thumb)
        return '-'
    preview.allow_tags = True

    def tag_links(self, obj):
        return self._get_admin_links(obj.tag.all())
    tag_links.short_description = 'Tags'

    def set_source_action(self, request, queryset):
        source = request.POST['source']
        source_obj = Source.objects.get(id=source)
        updated = queryset.update(source=source, kind=source_obj.kind)
        messages.success(request,
                         '{0} documents were updated'.format(updated))
    set_source_action.short_description = u'Update source'

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        for version in form.instance.versions.all():
            version.tag.add(*form.instance.tag.all())
