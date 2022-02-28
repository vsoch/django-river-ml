from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

import sys

UserModel = get_user_model()


def get_user_token(user):
    """
    Get a user token.
    """
    try:
        return str(Token.objects.get(user=user))
    except Token.DoesNotExist:
        sys.exit("Token for %s does not exist." % user)


def create_user_token(user):
    """
    Function to create the token for the user, if it doesn't exist.
    """
    try:
        token = Token.objects.get(user=user)
    except Token.DoesNotExist:
        token = Token.objects.create(user=user)
    return str(token)


@receiver(post_save, sender=UserModel)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    """Create a token for the user when the user is created

    1. Assign user a token

    Create a token instance for all newly created User instances. We only
    run on user creation to avoid having to check for existence on each call
    to User.save. We also check if one is already created in case another app
    or the main user application is running the same function.
    """
    if created:
        create_user_token(instance)
