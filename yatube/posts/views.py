from typing import Any, Dict, Type, Union

from django.contrib.auth.decorators import login_required
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect

from .forms import PostForm
from .models import Group, Post, User
from .utils import paginator_func
from .constants import (GROUP_PER_PAGE_LIMIT, INDEX_PER_PAGE_LIMIT,
                        PROFILE_PER_PAGE_LIMIT)


def index(request: HttpRequest) -> HttpResponse:
    posts: QuerySet = Post.objects.select_related(
        'group', 'author',
    ).all()
    page_obj = paginator_func(posts, INDEX_PER_PAGE_LIMIT, request)
    context: Dict[str, QuerySet] = {
        'page_obj': page_obj,
    }

    return render(request, 'posts/index.html', context)


def group_posts(request: HttpRequest, slug: Any) -> HttpResponse:
    group: Type[Group] = get_object_or_404(Group, slug=slug)
    posts: QuerySet = group.posts.all()
    page_obj = paginator_func(posts, GROUP_PER_PAGE_LIMIT, request)
    context: Dict[str, Union[Type[Group], QuerySet]] = {
        'group': group,
        'page_obj': page_obj,
    }

    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = user.posts.all()
    page_obj = paginator_func(posts, PROFILE_PER_PAGE_LIMIT, request)
    context = {
        'author': user,
        'page_obj': page_obj,
    }

    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = Post.objects.get(id=post_id)
    context = {}
    if post.author.username == request.user.username:
        context['is_edit'] = True

    context['post'] = post

    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if form.is_valid():
        new_post = form.save(commit=False)
        new_post.author = request.user
        new_post.save()

        return redirect('posts:profile', request.user.username)

    context = {
        'form': form,
    }

    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author.username != request.user.username:

        return redirect('posts:post_detail', post_id)

    form = PostForm(request.POST or None, instance=post)
    if form.is_valid():
        form.save()

        return redirect('posts:post_detail', post_id)

    context = {
        'form': form,
        'is_edit': True,
        'post_id': post_id,
    }

    return render(request, 'posts/create_post.html', context)
