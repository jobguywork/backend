from rest_framework import decorators
from rest_framework.throttling import UserRateThrottle

from donate.models import Donate
from donate.serializers import DonateSerializer
from utilities.tools import create


@decorators.authentication_classes([])
@decorators.permission_classes([])
class DonateCreateView(create.CreateView):
    """
    post:

        name min 3, max 50

        coin

            LTC ,ONE ,TOMO ,DOGE ,ADA ,TRX ,DOT ,BUST ,USDT

        amount is float and must be postive

        link max 500, optional
    """
    serializer_class = DonateSerializer
    model = Donate
    throttle_classes = [UserRateThrottle]
