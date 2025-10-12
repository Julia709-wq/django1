from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(('catalog.urls', 'catalog'), namespace='catalog')),
    path('blogging/', include(('blogging.urls', 'blogging'), namespace='blogging')),
    path('users/', include(('users.urls', 'users'), namespace='users')),
]
