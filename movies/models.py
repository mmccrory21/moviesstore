from django.db import models
from django.contrib.auth.models import User
class Movie(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    price = models.IntegerField()
    description = models.TextField()
    image = models.ImageField(upload_to='movie_images/')
    def __str__(self):
        return str(self.id) + ' - ' + self.name

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
    title = models.CharField(max_length=200)                     # e.g., “Add ‘Inception’ (2010)”
    rationale = models.TextField(blank=True)                     # optional reason/notes
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id} - {self.title}"

class PetitionVote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    petition = models.ForeignKey(Petition, on_delete=models.CASCADE, related_name='votes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'petition')  # one “Yes” per user per petition

    def __str__(self):
        return f"{self.user.username} → Petition {self.petition_id}"