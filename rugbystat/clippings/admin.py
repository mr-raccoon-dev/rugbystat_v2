from django.contrib import admin
from clippings.models import Source, SourceObject, Document


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    pass

@admin.register(SourceObject)
class SourceObjectAdmin(admin.ModelAdmin):
    pass

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    pass
