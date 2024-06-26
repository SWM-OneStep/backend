# myapp/signals.py
from allauth.socialaccount.signals import social_account_added, social_account_updated
from django.dispatch import receiver


@receiver(social_account_added)
def social_account_added_receiver(request, sociallogin, **kwargs):
    print(sociallogin.account.extra_data)
    print(sociallogin.serialize())


@receiver(social_account_updated)
def social_account_updated_receiver(request, sociallogin, **kwargs):
    print(sociallogin.account.extra_data)
    print(sociallogin.serialize())
