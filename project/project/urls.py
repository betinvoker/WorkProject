from django.contrib import admin
from django.urls import path, re_path
from django.conf.urls import url
from django.views.generic import View, TemplateView, DetailView, ListView
from search_reviews import views

urlpatterns = [
    path('', views.UniversitiesListView.as_view(), name='index'),
    path('review/<int:id>/', views.OpinionsListView.as_view(), name='review'),
    path('rating', views.RatingUniversitiesView.as_view(), name='ratings'),
    path('search/', views.Search.as_view(), name='search'),
    path('admin/', admin.site.urls),
]