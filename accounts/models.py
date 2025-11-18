from django.db import models
from django.contrib.auth.models import User

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

    def __str__(self):
        return f"Profile({self.user.username})"
