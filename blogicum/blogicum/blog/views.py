from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone
from constants import MAX_POSTS_PER_PAGE
from .form import CommentForm, PostForm, ProfileEditForm
from .models import Category, Post, Comment


User = get_user_model()


def get_published_posts():
    """Return filtered QuerySet published posts"""
    posts = Post.objects.select_related('category', 'location'
                                        ).order_by('-pub_date')
    return posts.filter(pub_date__lte=timezone.now(), is_published=True,
                        category__is_published=True)


def index(request):
    post_list = get_published_posts()
    paginator = Paginator(post_list, MAX_POSTS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get('page'))
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'blog/index.html', context)


def post_detail(request, id):
    post = get_object_or_404(Post, pk=id)
    is_available = (post.is_published
                    and post.pub_date <= timezone.now()
                    and post.category.is_published)
    if not is_available:
        if not request.user.is_authenticated or request.user != post.author:
            raise Http404("Пост не найден")
    form = CommentForm()
    comments = Comment.objects.filter(post=id)
    context = {
        'comments': comments,
        'form': form,
        'post': post,
    }
    return render(request, 'blog/detail.html', context)


def category_posts(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug,
                                 is_published=True)
    post_list = get_published_posts().filter(category=category)
    paginator = Paginator(post_list, MAX_POSTS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get('page'))
    context = {
        'category': category,
        'page_obj': page_obj,
    }
    return render(request, 'blog/category.html', context)


def profile(request, username):
    user = get_object_or_404(User, username=username)
    post_list = Post.objects.select_related('author').filter(
        author=user).order_by('-pub_date')
    paginator = Paginator(post_list, MAX_POSTS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get('page'))
    context = {
        'page_obj': page_obj,
        'profile': user,
    }
    return render(request, 'blog/profile.html', context)


@login_required
def edit_profile(request):
    if request.method == 'GET':
        form = ProfileEditForm()
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('blog:profile', username=request.user.username)
    return render(request, 'blog/user.html', {'form': form})


@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            if post.pub_date and post.pub_date > timezone.now():
                post.is_published = False
            post.author = request.user
            post.save()
            return redirect('blog:profile', username=request.user.username)
    else:
        form = PostForm()
    return render(request, 'blog/create.html', {'form': form})


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(instance=post)
    if request.user != post.author:
        return redirect('blog:post_detail', post_id)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', post_id)
    return render(request, 'blog/create.html', {'form': form})


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(instance=post)
    if request.user != post.author:
        return redirect('blog:post_detail', post_id)
    if request.method == 'POST':
        post.delete()
        return redirect('blog:index')
    return render(request, 'blog/create.html', {'form': form})


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm()
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            post.comment_count = post.comments.count()
            post.save(update_fields=['comment_count'])
            return redirect('blog:post_detail', post_id)
    return render(request, 'includes/comments.html', {'form': form,
                                                      'post': post})


@login_required
def edit_comment(request, post_id, comment_id):
    post = get_object_or_404(Post, id=post_id)
    comment = get_object_or_404(Comment, id=comment_id)
    form = CommentForm(instance=comment)
    if request.user == comment.author:
        if request.method == 'POST':
            form = CommentForm(request.POST, instance=comment)
            if form.is_valid():
                comment.post_id = post_id
                comment.id = comment_id
                form.save()
                return redirect('blog:post_detail', id=post_id)
    return render(request, 'blog/comment.html', {'form': form,
                                                 'post': post,
                                                 'comment': comment})


@login_required
def delete_comment(request, post_id, comment_id):
    post = get_object_or_404(Post, id=post_id)
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user != comment.author and request.user != post.author:
        return redirect('blog:post_detail', post_id)
    if request.user == comment.author or request.user.is_staff:
        if request.method == 'POST':
            comment.delete()
            post.comment_count = post.comments.count()
            post.save(update_fields=['comment_count'])
            return redirect('blog:post_detail', post_id)
    return render(request, 'blog/comment.html', {'post': post,
                                                 'comment': comment})
