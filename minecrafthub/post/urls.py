from . import views
from django.urls import path, include


urlpatterns = [
    path('load_more_posts', views.load_more, name="load_more_posts"),
    path('filtered_posts', views.filtered_posts, name="filtered_posts"),
    path('tinymce/', include('tinymce.urls')),
    path('<slug:slug>/', views.post_details, name="post_details"),
    path('search', views.search, name="search"),
    path('early-access', views.early, name="early"),
    path('loadmore_early', views.loadmore_early, name="loadmore_early"),
]

handler404 = "home.views.page_not_found"