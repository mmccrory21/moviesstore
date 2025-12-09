from django.contrib import admin
from .models import Movie, Review, ReviewReport, Rating, PurchaseEvent
class MovieAdmin(admin.ModelAdmin):
    ordering = ['name']
    search_fields = ['name']

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'movie', 'user', 'date', 'is_removed')
    list_filter = ('is_removed', 'date', 'movie', "content_rating")
    search_fields = ('comment', 'user__username', 'movie__name')

@admin.register(PurchaseEvent)
class PurchaseEventAdmin(admin.ModelAdmin):
    list_display = ("movie","region","quantity","created_at","user")
    list_filter = ("region","created_at","movie")
    search_fields = ("movie__name","user__username")
    autocomplete_fields = ("movie","user")

admin.site.register(Movie, MovieAdmin)
admin.site.register(Review)
admin.site.register(Rating)
# Register your models here.
