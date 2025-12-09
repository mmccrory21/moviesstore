from django.contrib.auth.forms import UserCreationForm
from django.forms.utils import ErrorList
from django.utils.safestring import mark_safe
from django import forms
from movies.models import RATING_CHOICES
class CustomErrorList(ErrorList):
    def __str__(self):
        if not self:
            return ''
        return mark_safe(''.join([
            f'<div class="alert alert-danger" role="alert"> {e}</div>' for e in self]))
class CustomUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].help_text = None
            self.fields[fieldname].widget.attrs.update({'class': 'form-control'})
class ProfileImageForm(forms.Form):
    image = forms.ImageField(required=True, label="Choose a new profile picture")
class ProfileSettingsForm(forms.Form):
    image = forms.ImageField(required=False, label="Choose a new profile picture")
    max_content_rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        required=True,
        label="Max Content Rating",
        help_text="Movies above this rating will be blurred/disabled",
    )