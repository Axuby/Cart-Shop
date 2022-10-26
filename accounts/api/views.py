
from accounts.api.serializers import AccountSerializer, UserProfileSerializer
from accounts.models import Account, UserProfile
from rest_framework.generics import (GenericAPIView,
                                     ListCreateAPIView,
                                     ListAPIView,
                                     CreateAPIView,
                                     RetrieveUpdateDestroyAPIView,
                                     RetrieveUpdateAPIView)


class AccountsAV(ListAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer


class UserProfileAV(RetrieveUpdateDestroyAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
