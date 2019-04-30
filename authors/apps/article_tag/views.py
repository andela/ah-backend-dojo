from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.viewsets import ModelViewSet
from authors.apps.article_tag.models import ArticleTag
from authors.apps.article_tag.serializers import ArticleTagSerializer

class ArticleTagViewSet(ModelViewSet):
    queryset = ArticleTag.objects.all()
    serializer_class = ArticleTagSerializer


    def create_tag_if_not_exist(self, provided_tags):
        """method to create a tag if it doesn't exist"""
        unique_tags = {tag.lower() for tag in provided_tags}
        print(unique_tags)
        for provided_tag in unique_tags:
            try:
                ArticleTag.objects.get(tag_text=provided_tag.lower())
                
            except ObjectDoesNotExist:
                serializer = ArticleTagSerializer(data={"tag_text": provided_tag})
                serializer.is_valid(serializer)
                self.perform_create(ArticleTagViewSet, serializer)  
        return unique_tags
