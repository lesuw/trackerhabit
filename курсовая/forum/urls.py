from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'forum'  # Пространство имен

urlpatterns = [
    path('', views.CategoryListView.as_view(), name='category_list'),
    path('category/<int:pk>/', views.TopicListView.as_view(), name='category_detail'),
    path('topic/<int:pk>/', views.TopicDetailView.as_view(), name='topic_detail'),

    path('category/create/', views.create_category, name='create_category'),
    path('category/<int:pk>/update/', views.update_category, name='update_category'),
    path('category/<int:pk>/delete/', views.delete_category, name='delete_category'),
    path('category/update-order/', views.update_category_order, name='update_category_order'),

    path('category/<int:category_pk>/create-topic/', views.create_topic, name='create_topic'),
    path('topic/<int:pk>/delete/', views.delete_topic, name='delete_topic'),

    path('topic/<int:topic_pk>/create-message/', views.create_message, name='create_message'),
    path('message/<int:message_pk>/create-reply/', views.create_reply, name='create_reply'),
    path('message/<int:message_pk>/vote/', views.vote_message, name='vote_message'),
    path('message/<int:pk>/delete/', views.delete_message, name='delete_message'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)