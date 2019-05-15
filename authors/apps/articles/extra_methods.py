import random
import string

from django.utils.text import slugify

from authors.apps.article_likes.models import ArticleLike
from authors.apps.author_follows.models import AuthorFollowing
from .models import Article


def random_string_generator(size=10, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def create_slug(title):
    """
    this method helps to generate a unique slug for each article
    """
    
    slug = slugify(title)
    qs_exists = Article.objects.filter(slug=slug).exists()
    if qs_exists:
        new_slug = "{}-{}".format(slug, random_string_generator(size=4))
        return create_slug(new_slug)
    return slug


def count_(article_object, field):
    total = ArticleLike.objects.filter(article=article_object['id'], like_value=field)
    return len(total)


def like_grand_count(article_object):
    data = {
        "likes": count_(article_object, True),
        "dislikes": count_(article_object, False)
    }
    return data


def endpoint_redirect(like_status):
    values = {"like_value": "", "edit_value": "", "response_msg": ""}

    if like_status == "like":
        values["like_value"] = True
        values["edit_value"] = False
        values["response_msg"] = "liked"
        return values

    elif like_status == "dislike":
        values["like_value"] = False
        values["edit_value"] = True
        values["response_msg"] = "disliked"
        return values

    else:
        return False


def author_stats(author_name):
    count_ = {}
    followers = len(AuthorFollowing.objects.filter(following=author_name))
    following = len(AuthorFollowing.objects.filter(follower=author_name))
    count_["followers"] = followers
    count_["following"] = following
    return count_
