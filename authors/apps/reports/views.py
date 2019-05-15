from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from authors.apps.articles.models import Article
from authors.apps.profiles.models import Profile
from authors.apps.reports.models import ReportArticle
from authors.apps.reports.serializers import ReportArticleSerializer

# Create your views here.
class ReportArticleViewSet (ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = ReportArticle.objects.all().order_by('submission_date')
    serializer_class = ReportArticleSerializer
    
    def list(self, request):
        current_user = Profile.objects.get(user=request.user)
        if not request.user.is_superuser:
            self.queryset = ReportArticle.objects.all().filter(reporter=current_user)\
            .order_by('submission_date')
        serializer = ReportArticleSerializer(self.queryset, many=True)
        return Response({"reports": serializer.data})

    """
    override retrieve method from the RetrieveModelMixin class
    """
    def retrieve(self, request, *args, **kwargs):
        try:
            reported_article = ReportArticle.objects.get(id=kwargs.get("report_id"))
            serializer = self.get_serializer(reported_article)
            current_user = Profile.objects.get(user=request.user)
            if request.user.is_superuser or reported_article.reporter == current_user:
                return Response ({"report":serializer.data})
            else:
                return Response (
                    {"error":"You don't have the permissions to perform this request"},
                    status=status.HTTP_403_FORBIDDEN
                )
        except ObjectDoesNotExist:
            return Response({"error": "Article doesn't exist on the system"},
             status=status.HTTP_404_NOT_FOUND
            )

    def create(self, request, *args, **kwargs):
        try:
            article = Article.objects.get(slug=self.kwargs.get("slug"))
            data = request.data
            data["article"] = article.slug
            serializer = self.get_serializer(data=data)

            serializer.is_valid(raise_exception=True)

            if article.author == self.request.user:
                return Response({
                    "error": "You are not allowed to report your own article" 
                }, status=status.HTTP_403_FORBIDDEN)
            self.perform_create(serializer)
            return Response (serializer.data, status=status.HTTP_201_CREATED)
        except ObjectDoesNotExist:
            return Response({"error": "Article doesn't exist on the system"},
             status=status.HTTP_404_NOT_FOUND
            )

    def update(self, request, *args, **kwargs):
        try:
            reported_article = ReportArticle.objects.get(id=kwargs.get("report_id"))
            current_user = Profile.objects.get(user=request.user)
            data = request.data
            data["article"] = reported_article.article.slug

            if request.user.is_superuser and "report_status" in request.data \
                and self.admin_rights(request):
                data["violation_subject"] = reported_article.violation_subject
                data["violation_report"] = reported_article.violation_report
                data["report_status"] = request.data.get("report_status")
                serializer = self.get_serializer(reported_article, data=data)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)
                return Response (
                    {"message":"The status of the report on the article has been updated successfully"},
                    status=status.HTTP_201_CREATED
                )
            elif reported_article.reporter == current_user \
                and reported_article.report_status in ("pending", ):
                serializer = self.get_serializer(reported_article, data=data)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)
                return Response (
                    {"message":"The report on the article has been updated successfully"},
                    status=status.HTTP_201_CREATED
                )
            else:
                return Response (
                    {"error":"You don't have the permissions to perform this request"},
                    status=status.HTTP_403_FORBIDDEN
                )
        except ObjectDoesNotExist:
            return Response({"error": "No such report on the system"},
             status=status.HTTP_404_NOT_FOUND
            )

    def destroy(self, request, *args, **kwargs):
        try:
            reported_article = ReportArticle.objects.get(id=kwargs.get("report_id"))
            current_user = Profile.objects.get(user=request.user)
            if request.user.is_superuser or (reported_article.reporter == current_user \
            and reported_article.report_status in ("pending", )):
                self.perform_destroy(reported_article)
                return Response (
                    {"message":"The report on the article has been deleted successfully"})
            else:
                return Response (
                    {"error":"You don't have the permissions to perform this request"},
                    status=status.HTTP_403_FORBIDDEN
                )
        except ObjectDoesNotExist:
            return Response({"error": "Article doesn't exist on the system"},
             status=status.HTTP_404_NOT_FOUND
            )


    def perform_create(self, serializer):
        reporter = Profile.objects.get(user=self.request.user)
        serializer.save(reporter=reporter)

    def admin_rights(self, myrequest):
        input_data = ("violation_subject", "violation_report")
        for given_option in input_data:
            if given_option in myrequest.data:
                return False
        return True


