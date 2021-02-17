from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import View, DetailView, ListView
from django.views.generic.base import ContextMixin
from django.db.models import Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Universities, Opinions, Ratings
from django.db.models import Q

#   Главная страница
class UniversitiesListView(ListView):
    template_name = "search_reviews/index.html"
    paginate_by = 20

    def get_queryset(self):
        return Universities.universities_objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['popular_universities'] = Universities.popular_universities_objects.all()

        return context

#   Выбранный университет
class OpinionsListView(ListView):
    template_name = "search_reviews/reviews.html"

    def get(self, request, id, *args, **kwargs):
        university = Universities.objects.get(id=id)
        opinions = Opinions.objects.filter(university_id = id)
        status = self.request.GET.get("status")

        if status != None:
            filter_status = Opinions.objects.filter(university_id = id).filter(status = status)
        else:
            filter_status = Opinions.objects.filter(university_id = id)

        positive_opinions = opinions.filter(status = "True").count
        negative_opinions = opinions.filter(status = "False").count

        #   Пагинатор выбирает из таблицы Opinions 5 комментариев, на странице может быть не меньше двух комментариев
        paginator = Paginator(filter_status, 5, orphans = 2)

        page_number = request.GET.get('page')
        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        return render(request, "search_reviews/reviews.html", context = { "page_obj" : page_obj, "university" : university, "opinions" : opinions,
                                 "positive_opinions" : positive_opinions, "negative_opinions" : negative_opinions, "status" : status})

#   Страница поиска университетов
class Search(ListView):
    template_name = "search_reviews/search.html"
    paginate_by = 12

    def get_queryset(self):
        query = (Q(abbreviated__icontains = self.request.GET.get("q")) | Q(name__icontains = self.request.GET.get("q")))
        return Universities.objects.filter(query)
    
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["q"] = f'q={self.request.GET.get("q")}&'
        return context

#   Рейтинг университетов по версии ИНТЕРФАКС
class RatingUniversitiesView(View):
    def get(self, request):
        search_query = request.GET.get('search', '')
        order = request.GET.get('order', 'name')

        if search_query:
            rating = Ratings.objects.filter(query).order_by(order)
        else:
            rating = Ratings.objects.all().order_by(order)

        table_header = Ratings._meta.get_fields()

        return render(request, "search_reviews/rating_universities.html", context = {"table_header" : table_header, "rating" : rating})