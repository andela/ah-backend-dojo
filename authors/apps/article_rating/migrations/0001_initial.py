# Generated by Django 2.1 on 2019-04-29 08:08

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('articles', '0002_article_author'),
    ]

    operations = [
        migrations.CreateModel(
            name='ArticleRating',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField(default=0)),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='articles.Article', to_field='slug')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='articlerating', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]