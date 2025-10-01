from django.contrib import admin
from .models import Movie, Review, ReviewReport, Petition, PetitionVote
class MovieAdmin(admin.ModelAdmin):
    ordering = ['name']
    search_fields = ['name']

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'movie', 'user', 'date', 'is_removed')
    list_filter = ('is_removed', 'date', 'movie')
    search_fields = ('comment', 'user__username', 'movie__name')

admin.site.register(Movie, MovieAdmin)
admin.site.register(Review)
admin.site.register(Petition)
admin.site.register(PetitionVote)

# Register your models here.
