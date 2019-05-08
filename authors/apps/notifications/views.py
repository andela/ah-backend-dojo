from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from authors.apps.notifications.models import Notification, Notifier
from authors.apps.notifications.serializers import NotificationSerializer
from rest_framework.permissions import IsAuthenticated

class NotificationViews(APIView):
    
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        current_user = request.user
        notifications = Notification.objects.filter(receiver=current_user)
        serializer = NotificationSerializer(notifications, many=True)
        return Response(
            {
                "notifications_count": len(notifications),
                "notifications": serializer.data
            },
            status.HTTP_200_OK
        )

    def post(self, request):
        current_user = request.user
        notifier = Notifier.objects.filter(user=current_user).first()
        if notifier:
            if notifier.status==True:
                notifier.status = False
                notifier.save()
                return Response(
                    {"message": "you have deactivated notifications"},
                    status.HTTP_200_OK
                )
            notifier.status = True
            notifier.save()
            return Response(
                {"message": "you have activated notifications"},
                status.HTTP_200_OK
            )
