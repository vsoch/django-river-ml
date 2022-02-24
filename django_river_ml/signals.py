from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model

UserModel = get_user_model()


@receiver(post_save, sender=UserModel)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    """Create a token for the user when the user is created (with oAuth2)

    1. Assign user a token
    2. Assign user to default group

    Create a token instance for all newly created User instances. We only
    run on user creation to avoid having to check for existence on each call
    to User.save.
    """
    if created:
        Token.objects.create(user=instance)
