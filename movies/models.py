from django.db import models
from django.contrib.auth.models import User
RATING_CHOICES = [
    ("G", "G"),
    ("PG", "PG"),
    ("PG-13", "PG-13"),
    ("R", "R"),
]
class Movie(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    price = models.IntegerField()
    description = models.TextField()
    image = models.ImageField(upload_to='movie_images/')
    def __str__(self):
        return str(self.id) + ' - ' + self.name
    content_rating = models.CharField(
        max_length=5, choices=RATING_CHOICES, default="PG-13"
    )

    # optional convenience:
    def rating_level(self):
        order = {"G": 0, "PG": 1, "PG-13": 2, "R": 3}
        return order.get(self.content_rating, 3)

class Review(models.Model):
    id = models.AutoField(primary_key=True)
    comment = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_removed = models.BooleanField(default=False)
    def __str__(self):
        return str(self.id) + ' - ' + self.movie.name

class ReviewReport(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='reports')
    reason = models.CharField(max_length=255, blank=True)  # optional
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'review')  # one report per user per review

    def __str__(self):
        return f"{self.user.username} → Review {self.review_id}"
    
class Petition(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)          # e.g., “Add Inception (2010)”
    rationale = models.TextField(blank=True)          # optional
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id} - {self.title}"

class PetitionVote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    petition = models.ForeignKey(Petition, on_delete=models.CASCADE, related_name='votes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'petition')        # one


class Rating(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey('Movie', on_delete=models.CASCADE, related_name='ratings')
    value = models.IntegerField(choices=RATING_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'movie')  # one rating per user per movie

    def __str__(self):
        return f"{self.user.username} → {self.movie.name}: {self.value}"
    

US_STATES = [
    ("AL","Alabama"),("AK","Alaska"),("AZ","Arizona"),("AR","Arkansas"),("CA","California"),
    ("CO","Colorado"),("CT","Connecticut"),("DE","Delaware"),("FL","Florida"),("GA","Georgia"),
    ("HI","Hawaii"),("ID","Idaho"),("IL","Illinois"),("IN","Indiana"),("IA","Iowa"),
    ("KS","Kansas"),("KY","Kentucky"),("LA","Louisiana"),("ME","Maine"),("MD","Maryland"),
    ("MA","Massachusetts"),("MI","Michigan"),("MN","Minnesota"),("MS","Mississippi"),("MO","Missouri"),
    ("MT","Montana"),("NE","Nebraska"),("NV","Nevada"),("NH","New Hampshire"),("NJ","New Jersey"),
    ("NM","New Mexico"),("NY","New York"),("NC","North Carolina"),("ND","North Dakota"),("OH","Ohio"),
    ("OK","Oklahoma"),("OR","Oregon"),("PA","Pennsylvania"),("RI","Rhode Island"),("SC","South Carolina"),
    ("SD","South Dakota"),("TN","Tennessee"),("TX","Texas"),("UT","Utah"),("VT","Vermont"),
    ("VA","Virginia"),("WA","Washington"),("WV","West Virginia"),("WI","Wisconsin"),("WY","Wyoming"),
]

class PurchaseEvent(models.Model):
    """
    Minimal 'purchase' record tied to a region.
    If you already have Orders, you can create these rows when an order completes.
    """
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    movie = models.ForeignKey('Movie', on_delete=models.CASCADE, related_name='purchase_events')
    region = models.CharField(max_length=2, choices=US_STATES)  # state code, e.g., 'GA'
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['region']),
            models.Index(fields=['movie']),
        ]

    def __str__(self):
        return f"{self.region} • {self.movie.name} x{self.quantity}"
    