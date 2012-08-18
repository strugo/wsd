"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase

class SimpleTest(TestCase):
    def test_change_balance(self):

from mf2core.models import Tarif
from decimal import Decimal
tarif = Tarif.create(name="50$", cost=Decimal("50"),allow_credit=True)

from mf2core.models import Tarif
from account.settings import ChangeBalanceReason
from django.contrib.auth.models import User
user = User.objects.get(username='system')
profile = user.get_profile()
user = User.objects.get(username='leonid')
profile = user.get_profile()
tarif = Tarif.objects.get(pk=1)
from mf2core.blogic.cycle import activate_dynamics
activate_dynamics(tarif)

from mf2core.blogic.main import buy_tarif
buy_tarif(user, tarif)

        if profile.balance <> 100:
            raise Exception(u"Wrong balance")
        profile.change_balance(-50, ChangeBalanceReason.cash_in)
        if profile.balance <> 50:
            raise Exception(u"Wrong balance")


from mf2core.blogic.credit import CreditLogic
cr = CreditLogic(user)
