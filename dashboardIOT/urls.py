from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('admin/', admin.site.urls),
    path('garbage/', include("garbage.urls")),
    path('pets/', include("pets.urls")),
    path('api/', include("api.urls")),
    path('orchards/', include("orchards.urls")),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
