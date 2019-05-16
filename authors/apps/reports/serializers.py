from rest_framework.serializers import (
    HyperlinkedModelSerializer,
    ValidationError,
    PrimaryKeyRelatedField,
    CurrentUserDefault
)
from authors.apps.reports.models import ReportArticle
from authors.apps.profiles.serializers import ProfileSerializer

class ReportArticleSerializer(HyperlinkedModelSerializer):
    reporter = ProfileSerializer(read_only=True)

    def validate_violation_subject(self, violation_subject):
        if violation_subject not in ("spam", "harassment", "rules violation"):
            raise ValidationError(
                "status should be 'spam', 'harassment', 'rules violation'")
        return violation_subject

    def validate_report_status(self, report_status):
        if report_status not in ["pending", 'allegations_true', 'allegations_false', "under_investigation"]:
            raise ValidationError(
                "status should be 'pending', 'allegations_true', 'allegations_false' or 'under_investigation'")
        return report_status

    class Meta:
        model = ReportArticle
        fields = (
            'id', 'reporter', 'article', 'violation_subject', 'violation_report', 
            'report_status', 'submission_date')
    
