from django.shortcuts import render
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from .forms import CustomUserCreationForm, CustomErrorList
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import ProfileImageForm
from django.contrib import messages
from .forms import ProfileImageForm
from .models import Profile
from .forms import ProfileSettingsForm

@login_required
def orders(request):
    template_data = {}
    template_data['title'] = 'Orders'
    template_data['orders'] = request.user.order_set.all()
    return render(request, 'accounts/orders.html',
        {'template_data': template_data})
@login_required
def logout(request):
    auth_logout(request)
    return redirect('home.index')
def login(request):
    template_data = {}
    template_data['title'] = 'Login'
    if request.method == 'GET':
        return render(request, 'accounts/login.html',
            {'template_data': template_data})
    elif request.method == 'POST':
        user = authenticate(
            request,
            username = request.POST['username'],
            password = request.POST['password']
        )
        if user is None:
            template_data['error'] = 'The username or password is incorrect.'
            return render(request, 'accounts/login.html',
                {'template_data': template_data})
        else:
            auth_login(request, user)
            return redirect('home.index')
def signup(request):
    template_data = {}
    template_data['title'] = 'Sign Up'
    if request.method == 'GET':
        template_data['form'] = CustomUserCreationForm()
        return render(request, 'accounts/signup.html',
            {'template_data': template_data})
    elif request.method == 'POST':
        form = CustomUserCreationForm(request.POST,
            error_class=CustomErrorList)
        if form.is_valid():
            form.save()
            return redirect('accounts.login')
        else:
            template_data['form'] = form
            return render(request, 'accounts/signup.html',
                {'template_data': template_data})
@login_required
def profile_page(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ProfileSettingsForm(request.POST, request.FILES)
        if form.is_valid():
            img = form.cleaned_data.get("image")
            if img:
                profile.image = img
            val = form.cleaned_data.get("max_content_rating")
            if val:
                profile.max_content_rating = val
            profile.save()
            messages.success(request, "Profile updated!")
            return redirect("accounts.profile")
        else:
            # surface errors to the page
            messages.error(request, f"Please fix the form: {form.errors.as_text()}")
    else:
        form = ProfileSettingsForm(initial={"max_content_rating": profile.max_content_rating})

    template_data = {"title": "My Profile", "profile": profile, "form": form}
    return render(request, "accounts/profile.html", {"template_data": template_data})