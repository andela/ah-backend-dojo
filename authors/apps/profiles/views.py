from rest_framework import generics, status, permissions
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Profile
from .renderers import ProfileRenderer
from .serializers import ProfileSerializer
from .exceptions import ProfileDoesNotExist
from .permissions import IsOwnerOrReadOnly
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404


class ProfileRetrieveUpdateView(generics.GenericAPIView):
    """
    Class for retriving  and updating user profile
    """
    permission_classes = (permissions.IsAuthenticated,IsOwnerOrReadOnly)
    renderer_classes = (ProfileRenderer,)
    serializer_class = ProfileSerializer

    def get(self, request, *args, **kwargs):
        #Function to retrieve user profile
        serializer = self.serializer_class(
            get_object_or_404(Profile, user=self.kwargs.get("username")))
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        # Function to update user profile

        try:
            user = get_user_model().objects.get(username=self.kwargs.get("username"))
        except ObjectDoesNotExist:
            raise Http404()

        profile = Profile.objects.get(user=user.username)

        if not profile.user.pk == request.user.id:
            return Response({"detail": "You don't have permissions to update this user"}, 
            status=status.HTTP_403_FORBIDDEN)
        serializer = self.serializer_class(
            profile, data=request.data["profile"], partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

