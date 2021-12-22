from django.contrib import admin
from django.urls import include, path



urlpatterns = [
    path("clientfile/", include("clientfile.urls")),
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("medical_info/", include("medical_info.urls")),
    # path('', views.index, name='index'),
    # path('auth/', include('AuthService.urls')),
]