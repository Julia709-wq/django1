from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from blogging import views
from blogging.apps import BloggingConfig
from blogging.views import (BlogPostListView, BlogPostDetailView, BlogPostCreateView,
                            BlogPostUpdateView, BlogPostDeleteView)

app_name = BloggingConfig.name

urlpatterns = [
    path('', BlogPostListView.as_view(), name='main_menu'),
    path('post/<int:pk>/', BlogPostDetailView.as_view(), name='blogpost_detail'),
    path('post/create/', BlogPostCreateView.as_view(), name='blogpost_create'),
    path('post/<int:pk>/update/', BlogPostUpdateView.as_view(), name='blogpost_update'),
    path('post/<int:pk>/delete/', BlogPostDeleteView.as_view(), name='blogpost_delete'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
