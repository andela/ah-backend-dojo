from django.urls import path
from authors.apps.reports.views import ReportArticleViewSet

urlpatterns = [
    path(
        "<str:slug>/report-article/", 
        ReportArticleViewSet.as_view({'post':'create'}), name="report"
    ),
    path(
        "report-article/<int:report_id>/", 
        ReportArticleViewSet.as_view({'get':'retrieve', 'put':'update', 'delete':'destroy'}), name="edit-report"
    ),
    path(
        "report-article/", 
        ReportArticleViewSet.as_view({'get':'list'}), name="reports-list"
    ),

]