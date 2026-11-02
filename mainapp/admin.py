from django.contrib import admin
from .models import models, Article, Category






# Register your models here.
class ArticleasAdmin(admin.ModelAdmin):
    readonly_fields = ('created_date_at', 'updated_date_at')  # ← usa guiones bajos
    list_display = ('title', 'publico', 'created_date_at')  # opcional, para mejor vista

    pass


admin.site.register(Article,ArticleasAdmin)
admin.site.register(Category)
