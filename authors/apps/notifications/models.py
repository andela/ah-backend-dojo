from django.db import models
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from authors.apps.authentication.models import User
from authors.apps.articles.models import Article, FavoriteArticle
from authors.apps.author_follows.models import AuthorFollowing
from authors.apps.comments.models import Comment
from django.db.models.signals import post_save

class Notification(models.Model):
    receiver = models.ForeignKey(User, to_field="username", on_delete=models.CASCADE) # edit name
    body = models.CharField(max_length=100)
    link = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    def __str__(self):
        return self.body

class Notifier(models.Model):
    user = models.ForeignKey(User, to_field="username", on_delete=models.CASCADE)
    status = models.BooleanField(default=True)

def notifier_check(sender, instance, **kwargs):
    notifier = Notifier.objects.filter(user=instance.username).first()
    if not notifier:
        create_notifier = Notifier.objects.create(
            user=instance
        )
        create_notifier.save()   

def save_notification(sender, instance, **kwargs):
    """
    this method sends notifications to;
    1. Followers of an author when the author publishes
    """

    email_body = {}
    email_body["subject"] = "Author's Haven Notifications"
    if isinstance(instance, Article):
        followers = AuthorFollowing.objects.filter(following=instance.author)
        email_body["notification"] = "New article written by {}".format(instance.author.username)
        for follower in followers:
            notify = Notifier.objects.filter(user=follower.follower).first()
            if notify.status:
                receiver = User.objects.filter(username=follower.follower).first()
                notification = Notification.objects.create(
                    receiver=receiver,
                    body=email_body["notification"],
                    link="{}/api/articles/{}/".format(settings.WEB_HOST, instance.id)
                )
                notification.save()
                email_body["receipient"] = receiver.email
                context = {
                    "username": receiver.username,
                    "notification_msg": email_body["notification"],
                    "object_url": "{}/api/articles/{}/".format(
                        settings.WEB_HOST,
                        instance.id
                    )
                }
                notification_email(email_body, context)

    if isinstance(instance, Comment):
        favoriting_users = FavoriteArticle.objects.filter(article=instance.article).exclude(favorited_by=instance.author.user)
        email_body["notification"] = 'Article with the title "{}" has a new comment from {}'.format(instance.article, instance.author)
        for user in favoriting_users:
            notify = Notifier.objects.filter(user=user.favorited_by).first()
            if notify.status:
                notification = Notification.objects.create(
                    receiver=user.favorited_by,
                    body=email_body["notification"],
                    link="{}/api/articles/{}/comments/{}/".format(
                        settings.WEB_HOST,
                        instance.article.slug,
                        instance.id
                    )
                )
                notification.save()
                email_body["receipient"] = user.favorited_by.email
                context = {
                    "username": user.favorited_by.username,
                    "notification_msg": email_body["notification"],
                    "object_url": "{}/api/articles/{}/comments/{}/".format(
                        settings.WEB_HOST,
                        instance.article.slug,
                        instance.id
                    )
                }
                notification_email(email_body, context)
            
def notification_email(email_body, context):
    template_name = "notification.html"
    html_content = render_to_string(template_name, context)
    subject = email_body["subject"]
    text_content = email_body["notification"]
    sender = settings.EMAIL_HOST_USER
    receipient = [email_body["receipient"]]

    email = EmailMultiAlternatives(subject, text_content, sender, receipient)
    email.attach_alternative(html_content, "text/html")
    email.send()

post_save.connect(save_notification, sender=Article)
post_save.connect(save_notification, sender=Comment)
post_save.connect(notifier_check, sender=User)


