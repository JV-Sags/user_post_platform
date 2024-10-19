from django.contrib import admin
from .models import User, Post

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'contact_number', 'is_approved', 'is_active')
    list_filter = ('is_approved', 'is_active')
    search_fields = ('username', 'email')

    def approve_user(self, request, queryset):
        queryset.update(is_approved=True, is_active=True)
    approve_user.short_description = "Approve selected users"

    actions = [approve_user]

class PostAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'content')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'content')

admin.site.register(User, UserAdmin)
admin.site.register(Post, PostAdmin)
