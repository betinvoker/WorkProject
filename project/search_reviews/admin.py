from django.contrib import admin
from .models import Universities, Opinions, Ratings

#   Показывает комментарии относящиеся к выбранному университету
class UniversitiesInline(admin.TabularInline):
    model = Opinions
    extra = 1

@admin.register(Universities)
class UniversitiesAdmin(admin.ModelAdmin):
    list_display = ("id", "abbreviated", "name", "link", "logo")
    list_display_links = ("id", "abbreviated", "name")
    search_fields = ("abbreviated", "name")
    readonly_fields = ("link",)
    empty_value_display = "---"
    list_per_page = 50
    #   Показывает комментарии относящиеся к выбранному университету
    inlines = [UniversitiesInline]

@admin.register(Opinions)
class OpinionsAdmin(admin.ModelAdmin):
    list_display = ("id", "text", "date_opinion", "status", "status_ai", "university_id")
    list_editable = ("text",)
    list_filter = ("status",)
    search_fields = ("text", "university_id__abbreviated", "university_id__name")
    readonly_fields = ("status", "status_ai")
    empty_value_display = "---"
    list_per_page = 15

    fieldsets = (
        (None, {
            "fields" : ("text", "date_opinion",)
        }), 
        ("Сравнение статуса", {
            "classes" : ("collapse",),
            "fields" : (("status", "status_ai",),)
        })
    )

@admin.register(Ratings)
class RatingsAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "link", "rating_summary", "rating_education", "rating_brand", 
        "rating_research", "rating_socialization", "rating_internationalization", "rating_innovation")
    list_display_links = ("id", "name")
    search_fields = ("name",)
    readonly_fields = ("link", "rating_summary", "rating_education", "rating_brand", "rating_research",
        "rating_socialization", "rating_internationalization", "rating_innovation")
    empty_value_display = "---"

    fieldsets = (
        (None, {
            "fields" : ("name", "link")
        }),
        ("Рейтинг", {
            "fields" : (("rating_education", "rating_brand", "rating_research"), ("rating_socialization", "rating_internationalization", "rating_innovation"),)
        }),
        ("Сводный рейтинг", {
            "fields" : ("rating_summary",)
        })
    )