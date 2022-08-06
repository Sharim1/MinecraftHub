from post.models import Post, EarlyAccess
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404, render
from .forms import CommentForm
from django.db.models import Q
from .scrapvideo import YouTube
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.cache import cache_page
import json
import logging


logger = logging.getLogger(__name__)

def load_more(request, offset=0):
    """Gets more posts from database and returns a Json response.

    param:
        offset(int): Number of posts already on the page.

    returns: Json object containing html rendered with received posts data from db
                and total number of posts
    """
    limit = 4
    try:
        offset = int(request.GET.get('offset'))
    except Exception as e:
        offset = 0
    try:
        selected_cat = request.GET.get('categories')[1:-1].replace('"', '').split(',')
        if not selected_cat[0]:
            latest = Post.objects.filter(status=1).order_by('-timestamp')[offset:offset+limit]
            logger.info("Loaded more latest posts from DB.")
        else:
            logger.info("Calling filtered_posts view with selected categories.")
            return filtered_posts(request, offset)
    except Exception as e:
        latest = Post.objects.filter(status=1).order_by('-timestamp')[offset:offset+limit]
        logger.info("Loading latest posts, resetting all filters.")
    posts_html = render_to_string('post.html', {'latest': latest})
    data = {
        'latest': posts_html,
        'total' : Post.objects.all().filter(status=1).count(),
    }
    logger.info("Returning Json response containing latest posts as html.")
    return JsonResponse(data=data)


def filtered_posts(request, offset=0):
    """Gets posts based on selected categories and returns a Json Response.

    param:
        offset(int): Number of posts already on the page.

    returns: Json object containing html rendered with received posts data from db
                and total number of posts
    """
    limit = 4
    try:
        selected_cat = request.GET.get('categories')[1:-1].replace('"', '').split(',')
        if not selected_cat[0]:
            return load_more(request)
        latest = Post.objects.filter(Category__title__in=selected_cat).filter(status=1).distinct()
        logger.info("Got the posts based on the selected categories from DB.")
        posts_html = render_to_string('post.html',{'latest': latest.filter(status=1).order_by('-timestamp')[offset:offset+limit]})
    except Exception as e:
        logger.critical("Unable to filter the posts based on selected categories. Error - {}".format(e))
    data = {
        'latest': posts_html,
        'total': latest.count()
    }
    logger.info("Returning Json response containing selected categories posts as html.")
    return JsonResponse(data=data)


def post_details(request, slug):
    """Renders the requested post based on the slug."""

    try:
        blog = get_object_or_404(Post, slug=slug)
        newlink=""
        newlink=blog.youtube_link.replace("watch?v=", "embed/")
        comments = blog.comments.filter(active=True).order_by("-created_on")
        new_comment = None
        # Comment posted
        if request.method == "POST":
            comment_form = CommentForm(data=request.POST)
            if comment_form.is_valid():
                new_comment = comment_form.save(commit=False)
                new_comment.post = blog
                new_comment.save()
        else:
            comment_form = CommentForm()
    except Exception as e:
        logger.critical("Unable to fetch post details. Slug - {}. Error - {}".format(slug, e))
    try:
        context = {
            'blog': blog,
            'newlink': newlink,
            "comments": comments,
            "new_comment": new_comment,
            "comment_form": comment_form,
        }
    except Exception as e:
        logger.error("Invalid slug used, either it doesn't exist or have been deleted - {}. Error - {}".format(slug, e))
        return render(request, '404.html')
    logger.info("Rendering the post successfully. Slug - {}".format(slug))
    return render(request, 'blog.html', context)


def search(request):
    """Returns queryset based on search query."""

    try:
        query_set = Post.objects.all().filter(status=1)
        search_query = request.GET.get('search_query')
        if search_query:
            query_set = query_set.filter(
                Q(title__icontains=search_query) |
                Q(overview__icontains=search_query)
            ).order_by('-timestamp').distinct()
        posts_html = render_to_string('post.html', {'latest': query_set})
        data = {
            'queryset' : posts_html
        }
    except Exception as e:
        logger.error("Unable to get the search result related to query - {}. Error - {}".format(search_query, e))
    return JsonResponse(data=data)


def latest_videos_pagination(request, videos):
    """Common pagination implementation method being used by early() and loadmore_early() method."""

    paginator = Paginator(videos, 9)
    page=request.GET.get('page')
    try:
        paginated_queryset = paginator.page(page)
    except PageNotAnInteger:
        paginated_queryset = paginator.page(1)
    except EmptyPage:
        paginated_queryset = paginator.page(paginator.num_pages)
    except Exception as e:
        logger.error("Unable to implement pagination on page request - {}. Error - {}".format(page, e))
    return paginated_queryset


@cache_page(3 * 60)
def early(request):
    """Renders early access page along with saving fetched latest videos in json file."""

    try:
        blog = get_object_or_404(EarlyAccess)
    except Exception as e:
        logger.error("Unable to get early access details. Error - {}".format(e))
    try:
        videos = YouTube().get_data()
        json_data = json.dumps(videos)
        with open("latest_videos.json", "w") as outfile:
            outfile.write(json_data)
        logging.info("Got the response from Youtube, saved data in file.")
    except Exception as e:
        with open("latest_videos.json", "r") as infile:
            videos = json.load(infile)
        logging.error("Was unable to get the data from Youtube. Error - {}".format(e))

    paginated_queryset = latest_videos_pagination(request, videos)
    newlink=""
    newlink=blog.youtube_link.replace("watch?v=", "embed/")
    context = {
        'blog': blog,
        'newlink': newlink,
        "videos": paginated_queryset
    }
    return render(request, "early.html", context)


def loadmore_early(request):
    """Pagination with saved json file for latest videos."""

    try:
        with open("latest_videos.json", "r") as infile:
            videos = json.load(infile)
        paginated_queryset = latest_videos_pagination(request, videos)
        videos_html = render_to_string('latest_videos.html', {"videos" : paginated_queryset})
    except Exception as e:
        logger.error("Unable to execute pagination with json file. Error - {}".format(e))
    data = {
        'videos_html' : videos_html
    }
    return JsonResponse(data=data)