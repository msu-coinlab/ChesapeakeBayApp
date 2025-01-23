from django.contrib import admin
from . import models


@admin.register(models.EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject' )
    search_fields = ('title', 'subject')
    ordering = ('title', 'subject')

    pass
@admin.register(models.EmailGroup)
class EmailGroupAdmin(admin.ModelAdmin):
    list_display = ('title',  )
    search_fields = ('title', )
    ordering = ('title', )
    pass

@admin.register(models.EmailMassive)
class EmailsMassiveAdmin(admin.ModelAdmin):
    list_display = ('title', 'from_user', 'email_template', 'created_at', 'send', 'sent' )
    search_fields = ('title', 'from_user', 'email_template', 'crated_at')
    ordering = ('sent', 'send', 'created_at', 'title', 'from_user')
    pass

@admin.register(models.EmailInstant)
class EmailsInstantAdmin(admin.ModelAdmin):
    list_display = ('subject', 'message', 'created_at', 'send', 'sent' )
    search_fields = ('subject', 'message', 'crated_at')
    ordering = ('sent', 'send', 'created_at', 'subject', 'message')
    pass

@admin.register(models.Email)
class EmailAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'status', 'error', 'created_at' )
    search_fields = ('recipient', 'status', 'error', 'created_at' )
    ordering =('created_at', 'status', 'error', 'recipient' )
    pass
