from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import UserRegisterForm, PostForm
from .models import Post
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
import logging

logger = logging.getLogger(__name__)

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            contact_number = form.cleaned_data.get('contact_number')
            if get_user_model().objects.filter(contact_number=contact_number).exists():
                messages.error(request, 'A user with this contact number already exists.')
                return redirect('register')

            user = form.save(commit=False)
            user.is_active = False  # Disable login until approved
            user.save()
            messages.success(request, 'Account successfully created. Please wait for admin approval.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'core/register.html', {'form': form})

@login_required
def create_post(request):
    if Post.objects.filter(user=request.user).exists():
        messages.error(request, 'You can only post once.')
        return redirect('home')
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            messages.success(request, 'Post created successfully.')
            return redirect('home')
    else:
        form = PostForm()
    return render(request, 'core/create_post.html', {'form': form})

def post_list_view(request):
    posts = Post.objects.all().order_by('-created_at')
    paginator = Paginator(posts, 3)  # 3 posts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'core/home.html', {'page_obj': page_obj})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)

            if user is not None:
                # Ensure user is active and approved before logging in
                if user.is_active and user.is_approved:
                    login(request, user)
                    messages.success(request, f"Welcome back, {user.username}!")
                    logger.info(f"User {username} logged in successfully.")
                    return redirect('home')
                else:
                    messages.error(request, "Your account is not active or not approved.")
                    logger.warning(f"Login attempt for inactive or unapproved user: {username}.")
                    return redirect('login')
            else:
                messages.error(request, "Invalid username or password.")
                logger.warning("Login failed: Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
            logger.warning("Login failed: Invalid form data.")

    form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})
