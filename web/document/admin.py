from django.contrib import admin
from .models import Document
from .models import DocumentESignatureLog


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    pass


@admin.register(DocumentESignatureLog)
class DocumentESignatureLogAdmin(admin.ModelAdmin):
    pass
