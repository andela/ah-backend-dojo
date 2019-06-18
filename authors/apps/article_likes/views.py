from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from authors.apps.articles.models import Article
from authors.apps.articles.serializers import ArticleSerializer
from .models import ArticleLike
from authors.apps.articles.extra_methods import endpoint_redirect
from .serializers import ArticleLikeSerializer
from authors.apps.profiles.models import Profile

class LikeArticleStatus(generics.GenericAPIView):
    # permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = ArticleLike.objects.all()
    serializer_class = ArticleLikeSerializer

    def get(self, request, **kwargs):
        """Get specific like for a particular authenticated user"""
        try:
            current_user = request.user
            user = Profile.objects.get(user=current_user)
            user_name = user.user
            article_slug = kwargs['slug']
            article = Article.objects.get(slug=article_slug)
            articleLike = ArticleLike.objects.get(article_id=article.id, liked_by_id=user_name)
            print(articleLike)
            serializer = self.serializer_class(articleLike, many=False)
            return Response({
                "status": serializer.data.get("like_value"),
            })
        except ObjectDoesNotExist:
            return Response({
                "status": "none",
            })

class ArticleLikesDislikesViews(APIView):
    """
    This deals with;
    1. Liking an article
    2. Removing a like
    """
    #Route protection
    permission_classes = (IsAuthenticated,)

    def post(self, request, slug, like_status):
        author = request.user
        article = get_object_or_404(Article, slug=slug, delete_status=False)

        query = ArticleLike.objects.filter(liked_by_id=author.username, article_id=article.id).first()
        
        serializer = ArticleLikeSerializer(query)
        article_like_object = serializer.data
        
        if endpoint_redirect(like_status):

            endpoint = endpoint_redirect(like_status)

            
            if query:
                if article_like_object['like_value'] == endpoint["like_value"]:
                        query.delete()
                        return Response(
                                {
                                    "article": article.title,
                                    "message": "your {} has been successfully revoked".format(like_status)
                                },
                                status.HTTP_200_OK
                            )
                
                article_like_object['like_value'] = endpoint["like_value"]
                serializer = ArticleLikeSerializer(query, article_like_object)
                if serializer.is_valid():
                    serializer.save()
            else:           
                data = {}
                data['liked_by'] = author.username
                data['article'] = article.id        
                data['like_value'] = endpoint["like_value"]

                serializer = ArticleLikeSerializer(data=data)
                if serializer.is_valid():
                    serializer.save()

            return Response(
                {
                    "article": article.title,
                    "message": "you have {} this article".format(endpoint["response_msg"])
                },
                status.HTTP_200_OK
            )
        
        return Response(
            {"error": "invalid route"},
            status.HTTP_400_BAD_REQUEST
        )