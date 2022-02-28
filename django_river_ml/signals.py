from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

UserModel = get_user_model()


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
        try:
            Token.objects.get(user=instance)
        except Token.DoesNotExist:
            Token.objects.create(user=instance)
