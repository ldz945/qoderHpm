"""
URL configuration for hpm project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from hpm.views import UserViewSet, current_user, role_list, dashboard_summary

router = DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/me/', current_user, name='current_user'),
    path('api/auth/roles/', role_list, name='role_list'),
    path('api/dashboard/summary/', dashboard_summary, name='dashboard_summary'),
    path('api/', include(router.urls)),
    path('api/master-data/', include('master_data.urls')),
    path('api/projects/', include('project.urls')),
    path('api/plans/', include('plan.urls')),
    path('api/changes/', include('change.urls')),
    path('api/acceptances/', include('acceptance.urls')),
    path('api/auxiliary/', include('auxiliary.urls')),
    path('api/interfaces/', include('interfaces.urls')),
]
