# Generated by Django 2.1 on 2019-05-02 10:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("articles", "0002_auto_20190502_1012"),
        ("profiles", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Comment",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("body", models.TextField()),
                ("created_at", models.DateTimeField(auto_now=True)),
                ("updated_at", models.DateTimeField(auto_now=True, null=True)),
                (
                    "article",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="articles.Article",
                    ),
                ),
                (
                    "author",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="profiles.Profile",
                    ),
                ),
            ],
        )
    ]