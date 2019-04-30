import random
import string
from django.utils.text import slugify
from .models import Article

def random_string_generator(size=10, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def create_slug(object_model, title):
    """
    this method helps to generate a unique slug for each article
    """
    slug = slugify(title)
    qs_exists = Article.objects.filter(slug=slug).exists()
    if qs_exists:
        new_slug = "{}-{}".format(slug, random_string_generator(size=4))
        return create_slug(title, new_slug)
    return slug