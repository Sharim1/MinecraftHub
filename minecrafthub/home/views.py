import logging
from django.shortcuts import get_object_or_404, render
from post.models import Post, EarlyAccess
from django.db.models import Count
from django.views.decorators.http import require_http_methods
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.http.response import JsonResponse
from django.views.decorators.cache import cache_page
from . import models


logger = logging.getLogger(__name__)

@cache_page(3 * 60)
def index(request):
    """View for the home page. Gets first few posts from db amd renders it."""
    try:
        early=get_object_or_404(EarlyAccess)
        newlink=early.youtube_link.replace("watch?v=", "embed/")
        latest = Post.objects.filter(status=1).order_by('-timestamp')[0:5]
        categories_count = get_category_count()
        logger.info("Got first few posts and category count for the home page successfully.")
    except Exception as e:
        logger.critical("Unable to fetch the posts or category count. Error - {}".format(e))
    context = {
            'latest': latest,
            'categories_count' : categories_count,
            'newlink':newlink
        }
    return render(request, 'index.html', context)


def get_category_count():
    """Gets count of posts for each category and returns it."""

    try:
        query_set = Post.objects.filter(status=1).values('Category__title').annotate(Count('Category__title'))
    except Exception as e:
        logger.error("Unable to get the category count. Error - {}".format(e))
    return query_set

def fetch_posts_in_cat(request, category):
    """Fetches posts within the categroy passed."""

    limit = 4
    try:
        latest = Post.objects.filter(Category__title__in=[category]).distinct().\
                                                order_by('-timestamp')[0:0+limit]
        logger.info("Got the posts of {} category successfully.".format(category))
    except Exception as e:
        logger.error("Unable to fetch posts of {} category. Error - {}".format(category, e))
    context = {'latest': latest}
    return render(request,'worlds.html', context)


@cache_page(3 * 60)
def worlds(request):
    """Gets all the posts related to category 'worlds' renders the related posts."""

    return fetch_posts_in_cat(request, "Worlds")


@cache_page(3 * 60)
def mods(request):
    """Gets all the posts related to category 'Mods' renders the related posts."""

    return fetch_posts_in_cat(request, "Mod")


def contact(request):
    """Renders contact page."""
    return render (request, 'contact.html')


@require_http_methods(["POST"])
def save_contacts(request):
    """Gets the details from the form and submits to the DB."""

    name = request.POST.get("name")
    email = request.POST.get("email")
    message = request.POST.get("message")

    try:
        validate_email(email)
    except ValidationError as e:
        logger.error('Invalid email was submitted - {}. Error - {}'.format(email, e))
        return JsonResponse({"message": "wrong"})
    else:
        if not models.ContactUs.objects.filter(email__iexact=email).exists():
            data = models.ContactUs(name=name, email=email, message=message)
            data.save()
            logger.info("Contact form details saved successfully.")
        else:
            logger.info("Email id already exists.")
    return JsonResponse({"message": "success"})


def page_not_found(request, exception):
    return render(request, '404.html', status=404)


def privacy_policy(request):
    return render (request, 'privacy.html')