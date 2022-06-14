from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from yatube.utils import pagination

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


def index(request):
    template = 'posts/index.html'
    posts = pagination(request, Post.objects.all())
    context = {
        'page_obj': posts
    }
    return render(request, template, context)


def group_posts(request, slug):
    group_template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    paginator = pagination(request, group.posts.all())
    context = {
        'group': group,
        'page_obj': paginator,
    }
    return render(request, group_template, context)


def profile(request, username):
    profile_template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    paginator = pagination(request, posts)
    count = author.posts.count()
    following = request.user.is_authenticated and author.following.filter(
        user=request.user).exists()
    context = {
        'page_obj': paginator,
        'author': author,
        'count': count,
        'following': following,
    }
    return render(request, profile_template, context)


def post_detail(request, post_id):
    post_detail_template = 'posts/post_detail.html'
    post = get_object_or_404(Post, pk=post_id)
    post_count = post.author.posts.count()
    comments = pagination(request, post.comments.all())
    form = CommentForm()
    context = {
        'post': post,
        'author': post.author,
        'post_count': post_count,
        'form': form,
        'comments': comments,
    }
    return render(request, post_detail_template, context)


@login_required
def post_create(request):
    create_post_template = 'posts/create_post.html'
    group = Group.objects.all()
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    )
    if form.is_valid():
        form.instance.author = request.user
        form.save()
        return redirect('posts:profile', username=request.user.username)

    context = {
        'form': form,
        'group': group
    }
    return render(request, create_post_template, context)


def post_edit(request, post_id):
    post_edit_template = 'posts/create_post.html'
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post.id)
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post.id)
    context = {
        'form': form,
        'post': post,
        'is_edit': True
    }
    return render(request, post_edit_template, context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    template = 'posts/follow.html'
    page_obj = pagination(request, Post.objects.filter(
        author__following__user=request.user))
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(
            user=request.user,
            author=author,
        )
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    user = get_object_or_404(Follow, user=request.user, author=author)
    if author.following.filter(author=author, user=request.user
                               ).exists():
        user.delete()
    return redirect('posts:profile', username=username)
