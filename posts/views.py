from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from . models import Post, User, Group, Comment, Follow
from . forms import PostForm, CommentForm
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.db.models import Count


@cache_page(20)
def index(request):
        post_list = (
            Post.objects.select_related('author')
            .select_related('group')
            .order_by('-pub_date')
            .annotate(comment_count=Count('post_comments'))
        )
        paginator = Paginator(post_list, 2)
        page_number = request.GET.get('page')
        page = paginator.get_page(page_number)
        return render(request, 'index.html', {'page': page, 'paginator': paginator})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = (
        Post.objects.select_related('author')
            .select_related('group')
            .order_by('-pub_date')
            .annotate(comment_count=Count('post_comments'))
    )
    paginator = Paginator(post_list, 10) # показывать по 10 записей на странице.
    page_number = request.GET.get('page') # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number) # получить записи с нужным смещением
    posts = Post.objects.filter(group=group).order_by("-pub_date")[:12]
    return render(request, "group.html", {"group": group, "posts": posts, 'page': page, 'paginator': paginator})

@login_required()
def new_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST or None, files=request.FILES or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('index')
        return render(request, 'new_post.html', {'form': form})
    form = PostForm()
    return render(request, 'new_post.html', {'form': form})



def profile(request, username):
    user = get_object_or_404(User, username=username)
    post_list = (
        Post.objects.select_related('author')
            .filter(author=user)
            .order_by('-pub_date')
            .annotate(comment_count=Count('post_comments'))
    )
    # является ли текущий юзер фоловером этого профайла
    following = False
    if request.user.is_authenticated:
        favorites = Follow.objects.filter(user=request.user).count()
        if favorites > 0:
            following = True
    user_followers = Follow.objects.filter(author=user).count()
    user_follow = Follow.objects.filter(user=user).count()

    my_post = Post.objects.filter(author=user).count()
    paginator = Paginator(post_list, 3)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        "profile.html",
        {
            'profile': user,
            'paginator': paginator,
            'page': page,
            'following': following,
            'user_followers': user_followers,
            'user_follow': user_follow,
            'my_post': my_post,
        }
    )


def post_view(request, username, post_id):
    user = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id)
    count = Post.objects.filter(author=user).count()
    user_followers = Follow.objects.filter(author=user).count()
    user_follow = Follow.objects.filter(user=user).count
    items = Comment.objects.filter(post=post)
    form = CommentForm()


    return render(
        request,
        "post.html",
        {
            'post': post,
            'profile': user,
            'count': count,
            'items': items,
            'form': form,
            'user_followers': user_followers,
            'user_follow': user_follow,
        }
    )

@login_required()
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST)
    if request.method != 'POST' or not form.is_valid():
        return redirect("post", username=post.author.username, post_id=post_id) #post.author.username

    comment = Comment(author=request.user, post=post, text=form.cleaned_data["text"])
    comment.save()
    return redirect("post", username=request.user.username, post_id=post_id)

@login_required()
def follow_index(request):
    favorite_list = Follow.objects.select_related('author', 'user').filter(user=request.user)
    author_list = [favorite.author for favorite in favorite_list]
    post_list = Post.objects.filter(author__in=author_list).order_by("-pub_date")
    paginator = Paginator(post_list, 5)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        "follow.html",
        {
            'page': page,
            'paginator': paginator,
        }
    )


@login_required()
def profile_follow(request, username):
        author = get_object_or_404(User, username=username)
        obj = Follow.objects.filter(user=request.user, author=author).first()
        if not obj and author.id != request.user.id:
            new = Follow(user=request.user, author=author)
            new.save()
        return redirect('profile', username=username)


@login_required()
def profile_unfollow(request, username):
        author = get_object_or_404(User, username=username)
        obj = Follow.objects.filter(user=request.user, author=author).first()
        if obj:
            obj.delete()
        return redirect('profile', username=username)

@login_required()
def post_edit(request, username, post_id):
        post = get_object_or_404(Post, id=post_id)
        user = get_object_or_404(User, username=username)
        if request.user != user:
                return redirect("post", username=request.user.username, post_id=post_id)

        form = PostForm(request.POST or None, files=request.FILES or None, instance=post)

        if request.method == "POST":
                if form.is_valid():
                        form.save()
                        return redirect("post", username=request.user.username, post_id=post_id)

        return render(
                request, "post_edit.html", {"form": form, "post": post},
        )


def page_not_found(request, exception):
        return render(request, "misc/404.html", {"path": request.path}, status=404)


def server_error(request):
        return render(request, "misc/500.html", status=500)