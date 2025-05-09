from django.contrib import admin
from .models import Category, Topic, Message, MessageVote

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'created_at', 'updated_at')
    list_editable = ('order',)
    ordering = ('order',)

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'author', 'created_at', 'is_pinned')
    list_filter = ('category', 'author', 'is_pinned')
    search_fields = ('title', 'description')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('author', 'topic', 'created_at', 'parent')
    list_filter = ('topic', 'author')
    search_fields = ('content',)

@admin.register(MessageVote)
class MessageVoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'vote', 'created_at')
    list_filter = ('vote',)