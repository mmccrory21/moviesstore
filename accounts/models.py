from django.db import models
from django.contrib.auth.models import User
from movies.models import RATING_CHOICES

# Create your models here.
def profile_upload_to(instance, filename):
    # stored as: media/profile_pics/<username>/<filename>
    return f"profile_pics/{instance.user.username}/{filename}"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    image = models.ImageField(
        upload_to=profile_upload_to,
        default="profile_pics/default.png",
        blank=True,
        null=True,
    )

    max_content_rating = models.CharField(
        max_length=5,
        choices=[("G","G"),("PG","PG"),("PG-13","PG-13"),("R","R")],
        default="R",
    )

    def __str__(self):
        return f"Profile({self.user.username})"
    @staticmethod
    def level_for(rating: str) -> int:
        return {"G": 0, "PG": 1, "PG-13": 2, "R": 3}.get(rating, 3)

