from django.urls import path
from . import views
from django.contrib.sitemaps.views import sitemap
from post.sitemaps import PostSitemap
from django.contrib import admin


sitemaps = {
    "posts": PostSitemap,
}

urlpatterns = [
    path('', views.index, name="home"),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path('worlds', views.worlds, name="worlds"),
    path('mods', views.mods, name="mods"),
    path('contact', views.contact, name="contact"),
    path('contact-form', views.save_contacts, name="contact-form"),
    path('privacy-policy', views.privacy_policy, name="privacy_policy"),
]