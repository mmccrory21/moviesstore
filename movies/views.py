from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Exists, OuterRef, Avg
from .models import Movie, Review, Petition, PetitionVote, Rating, ReviewReport

# Create your views here.
def index(request):
    search_term = request.GET.get('search')
    if search_term:
        movies = Movie.objects.filter(name__icontains=search_term)
    else:
        movies = Movie.objects.all()
    template_data = {}
    template_data['title'] = 'Movies'
    template_data['movies'] = Movie.objects.all()
    return render(request, 'movies/index.html', {'template_data': template_data})
def show(request, id):
    movie = Movie.objects.get(id=id)
    reviews = Review.objects.filter(movie=movie, is_removed=False)
    avg = movie.ratings.aggregate(avg=Avg('value'))['avg']
    user_rating = None
    if request.user.is_authenticated:
        r = Rating.objects.filter(movie=movie, user=request.user).first()
        if r:
            user_rating = r.value
    template_data = {}
    template_data['title'] = movie.name
    template_data['movie'] = movie
    template_data['reviews'] = reviews
    template_data['avg_rating'] = avg
    template_data['user_rating'] = user_rating
    return render(request, 'movies/show.html', {'template_data': template_data})
@login_required
def create_review(request, id):
    if request.method == 'POST' and request.POST['comment']!= '':
        movie = Movie.objects.get(id=id)
        review = Review()
        review.comment = request.POST['comment']
        review.movie = movie
        review.user = request.user
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)
@login_required
def edit_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user != review.user:
        return redirect('movies.show', id=id)
    if request.method == 'GET':
        template_data = {}
        template_data['title'] = 'Edit Review'
        template_data['review'] = review
        return render(request, 'movies/edit_review.html',
            {'template_data': template_data})
    elif request.method == 'POST' and request.POST['comment'] != '':
        review = Review.objects.get(id=review_id)
        review.comment = request.POST['comment']
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)
@login_required
def delete_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    review.delete()
    return redirect('movies.show', id=id)

@login_required
def report_review(request, id, review_id):
    if request.method != 'POST':
        return redirect('movies.show', id=id)

    review = get_object_or_404(Review, pk=review_id, movie_id=id)

    # Record the report (no duplicates per user)
    ReviewReport.objects.get_or_create(user=request.user, review=review)

    # Soft-delete / hide the review immediately
    review.is_removed = True
    review.save()

    return redirect('movies.show', id=id)

@login_required
def petitions(request):
    # POST => create a petition
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        rationale = request.POST.get('rationale', '').strip()
        if title:
            Petition.objects.create(title=title, rationale=rationale, created_by=request.user)
            return redirect('movies.petitions')

    # GET => list with Yes counts; show if current user already voted
    qs = Petition.objects.all().order_by('-created_at').annotate(yes_count=Count('votes'))
    already = PetitionVote.objects.filter(user=request.user, petition=OuterRef('pk'))
    qs = qs.annotate(user_voted=Exists(already))

    template_data = {'title': 'Petitions', 'petitions': qs}
    return render(request, 'movies/petitions.html', {'template_data': template_data})

@login_required
def petition_vote(request, petition_id):
    if request.method != 'POST':
        return redirect('movies.petitions')
    p = get_object_or_404(Petition, pk=petition_id)
    PetitionVote.objects.get_or_create(user=request.user, petition=p)  # idempotent
    return redirect('movies.petitions')

@login_required
def rate_movie(request, id):
    if request.method != 'POST':
        return redirect('movies.show', id=id)

    movie = get_object_or_404(Movie, id=id)
    try:
        value = int(request.POST.get('rating', ''))
    except ValueError:
        return redirect('movies.show', id=id)

    if value < 1 or value > 5:
        return redirect('movies.show', id=id)

    # Create or update the user's rating for this movie
    Rating.objects.update_or_create(
        user=request.user, movie=movie,
        defaults={'value': value}
    )
    return redirect('movies.show', id=id)
