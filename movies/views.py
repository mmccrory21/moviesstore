from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Exists, OuterRef, Avg, Sum
from .models import Movie, Review, Petition, PetitionVote, Rating, ReviewReport, PurchaseEvent

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

STATE_CENTROIDS = {
    "AL": (32.806671, -86.791130), "AK": (61.370716, -152.404419), "AZ": (33.729759, -111.431221),
    "AR": (34.969704, -92.373123), "CA": (36.116203, -119.681564), "CO": (39.059811, -105.311104),
    "CT": (41.597782, -72.755371), "DE": (39.318523, -75.507141), "FL": (27.766279, -81.686783),
    "GA": (33.040619, -83.643074), "HI": (21.094318, -157.498337), "ID": (44.240459, -114.478828),
    "IL": (40.349457, -88.986137), "IN": (39.849426, -86.258278), "IA": (42.011539, -93.210526),
    "KS": (38.526600, -96.726486), "KY": (37.668140, -84.670067), "LA": (31.169546, -91.867805),
    "ME": (44.693947, -69.381927), "MD": (39.063946, -76.802101), "MA": (42.230171, -71.530106),
    "MI": (43.326618, -84.536095), "MN": (45.694454, -93.900192), "MS": (32.741646, -89.678696),
    "MO": (38.456085, -92.288368), "MT": (46.921925, -110.454353), "NE": (41.125370, -98.268082),
    "NV": (38.313515, -117.055374), "NH": (43.452492, -71.563896), "NJ": (40.298904, -74.521011),
    "NM": (34.840515, -106.248482), "NY": (42.165726, -74.948051), "NC": (35.630066, -79.806419),
    "ND": (47.528912, -99.784012), "OH": (40.388783, -82.764915), "OK": (35.565342, -96.928917),
    "OR": (44.572020, -122.070938), "PA": (40.590752, -77.209755), "RI": (41.680893, -71.511780),
    "SC": (33.856892, -80.945007), "SD": (44.299782, -99.438828), "TN": (35.747845, -86.692345),
    "TX": (31.054487, -97.563461), "UT": (40.150032, -111.862434), "VT": (44.045876, -72.710686),
    "VA": (37.769337, -78.169968), "WA": (47.400902, -121.490494), "WV": (38.491226, -80.954453),
    "WI": (44.268543, -89.616508), "WY": (42.755966, -107.302490),
}

@login_required
def popularity_map(request):
    """
    Renders a map with markers per state; clicking a marker shows that state's top movies.
    A right-hand panel also lists the currently selected state's top titles.
    """
    # Aggregate total quantities per (region, movie)
    raw = (
        PurchaseEvent.objects
        .values('region', 'movie__name')
        .annotate(total=Sum('quantity'))
    )

    # Build a dict: region -> { total_all, top_movies: [(title, count), ...] }
    region_stats = {}
    for row in raw:
        reg = row['region']
        title = row['movie__name']
        cnt = row['total'] or 0
        region_stats.setdefault(reg, {'total': 0, 'movies': {}})
        region_stats[reg]['total'] += cnt
        region_stats[reg]['movies'][title] = region_stats[reg]['movies'].get(title, 0) + cnt

    # Convert movies dicts to sorted lists (top 5)
    payload = []
    for reg, data in region_stats.items():
        if reg not in STATE_CENTROIDS:
            continue
        lat, lon = STATE_CENTROIDS[reg]
        movies_sorted = sorted(data['movies'].items(), key=lambda kv: (-kv[1], kv[0]))[:5]
        payload.append({
            'region': reg,
            'lat': lat, 'lon': lon,
            'total': data['total'],
            'top_movies': [{'title': t, 'count': c} for t, c in movies_sorted]
        })

    template_data = {
        'title': 'Local Popularity Map',
        'points': payload,          # list of per-state payload items
    }
    return render(request, 'movies/popularity_map.html', {'template_data': template_data})