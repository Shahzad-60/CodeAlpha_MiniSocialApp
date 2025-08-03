from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from .models import Post, Comment
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Post, Like
from .models import Follow  # make sure ye import upar likha ho

@login_required
def home(request):
    if request.method == "POST":
        # If it's a post creation
        if 'title' in request.POST:
            title = request.POST.get('title')
            content = request.POST.get('content')
            Post.objects.create(user=request.user, title=title, content=content)
            return redirect('home')

        # If it's a comment
        elif 'comment_content' in request.POST:
            post_id = request.POST.get('post_id')
            content = request.POST.get('comment_content')
            post = Post.objects.get(id=post_id)
            Comment.objects.create(user=request.user, post=post, content=content)
            return redirect('home')

    posts = Post.objects.all().order_by('-created_at')
    
    # Get liked posts for current user
    liked_posts = set()
    following_users =[] 

    if request.user.is_authenticated:
        liked_posts = set(Like.objects.filter(user=request.user).values_list('post_id', flat=True))
        following_users = Follow.objects.filter(follower=request.user).values_list('following__username', flat=True)
      
    return render(request, 'home.html', { 
        'posts': posts,
        'liked_posts': liked_posts,
        'following_users': following_users
    })

@login_required
def add_comment(request, post_id):
    if request.method == "POST":
        post = get_object_or_404(Post, id=post_id)
        content = request.POST.get("comment")
        if content:
            Comment.objects.create(user=request.user, post=post, content=content)
    return redirect("home")  # ya


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        else:
            # Get posts and liked_posts for template
            posts = Post.objects.all().order_by('-created_at')
            liked_posts = set()
            if request.user.is_authenticated:
                liked_posts = set(Like.objects.filter(user=request.user).values_list('post_id', flat=True))
            
            return render(request, 'home.html', {
                'error': 'Invalid credentials',
                'posts': posts,
                'liked_posts': liked_posts
            })

    # Get posts and liked_posts for template
    posts = Post.objects.all().order_by('-created_at')
    liked_posts = set()
    if request.user.is_authenticated:
        liked_posts = set(Like.objects.filter(user=request.user).values_list('post_id', flat=True))
    
    return render(request, 'home.html', {
        'posts': posts,
        'liked_posts': liked_posts
    })

def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        if not User.objects.filter(username=username).exists():
            User.objects.create_user(username=username, email=email, password=password)
            return redirect('home')
        else:
            # Get posts and liked_posts for template
            posts = Post.objects.all().order_by('-created_at')
            liked_posts = set()
            if request.user.is_authenticated:
                liked_posts = set(Like.objects.filter(user=request.user).values_list('post_id', flat=True))
            
            return render(request, 'home.html', {
                'error': 'Username already taken',
                'posts': posts,
                'liked_posts': liked_posts
            })

    # Get posts and liked_posts for template
    posts = Post.objects.all().order_by('-created_at')
    liked_posts = set()
    if request.user.is_authenticated:
        liked_posts = set(Like.objects.filter(user=request.user).values_list('post_id', flat=True))
    
    return render(request, 'home.html', {
        'posts': posts,
        'liked_posts': liked_posts
    })

def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, user=request.user)
    post.delete()
    return redirect('home')


@login_required
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)

    if request.method == 'POST':
        new_content = request.POST.get('new_content')
        comment.content = new_content
        comment.save()
        return redirect('home')

    return render(request, 'edit_comment.html', {'comment': comment})

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)
    comment.delete()
    return redirect('home')

@login_required
def toggle_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)

    if not created:
        like.delete()
        liked = False
    else:
        liked = True

    return JsonResponse({
        'liked': liked,
        'like_count': post.likes.count()
    })

@login_required
def comment_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':
        content = request.POST.get('comment_content')
        if content:
            Comment.objects.create(user=request.user, post=post, content=content)
        return redirect('home')

    return render(request, 'comment_post.html', {'post': post})

@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, user=request.user)

    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        post.title = title
        post.content = content
        post.save()
        return redirect('home')

    return render(request, 'edit_post.html', {'post': post})


@login_required
def follow_user(request, username):
    target_user = get_object_or_404(User, username=username)

    # Apne aap ko follow na kare
    if target_user != request.user:
        existing = Follow.objects.filter(follower=request.user, following=target_user)
        if existing.exists():
            existing.delete()  # Already followed, so unfollow
        else:
            Follow.objects.create(follower=request.user, following=target_user)

    return redirect('home')
