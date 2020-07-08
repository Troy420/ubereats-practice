"""foodtasker URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from foodtaskerapp import views
from django.contrib.auth import views as auth_views

from django.conf import settings
from django.conf.urls.static import static

# ----------------------------------------------------------------------------------
# TypeError at /restaurant/sign-in/
# __init__() takes 1 positional argument but 2 were given
# ----------------------------------------------------------------------------------
# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('', views.home, name='home'),
#     path('restaurant/sign-in/', auth_views.LoginView,  <-----
#             {'template_name': 'restaurant/sign_in.html'},
#             name= 'restaurant-sign-in'),
#     path('restaurant/sign-out', auth_views.LogoutView,
#             {'next_page': '/'},
#             name='restaurant-sign-out'),
# ]


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),

    # Restaurant
    path('restaurant/sign-in/', auth_views.LoginView.as_view(
        template_name='restaurant/sign_in.html'), name='restaurant-sign-in'),
    path('restaurant/sign-out/', auth_views.LogoutView.as_view(next_page='/'),
         name='restaurant-sign-out'),
    path('restaurant/', views.restaurant_home, name='restaurant-home'),
    path('restaurant/sign-up/', views.restaurant_sign_up,
         name='restaurant-sign-up'),

    #  Sign in / Sign up / Sign out
    path('api/social/', include('rest_framework_social_oauth2.urls')),

    # Convert token (sign in/ sign up)

    # revoke token (sign out)
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
