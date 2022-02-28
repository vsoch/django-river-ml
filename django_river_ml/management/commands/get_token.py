from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import authenticate, get_user_model
from getpass import getpass
from rest_framework.authtoken.models import Token

User = get_user_model()


class Command(BaseCommand):
    """
    get a token for a user (typically to use the API)
    """

    def add_arguments(self, parser):
        parser.add_argument("username", nargs=1, default=None, type=str)

    help = "Get a user token to interact with the API"

    def handle(self, *args, **options):
        if not options["username"]:
            raise CommandError("Please provide a username")
        username = options["username"][0]
        print("Username: %s" % username)

        # The username must exist
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError("This username does not exist.")

        # Create the user and ask for password
        password = getpass("Enter Password:")
        user = authenticate(None, username=user.username, password=password)

        if user is not None:
            try:
                token = str(Token.objects.get(user=user))
                print(token)
            except Token.DoesNotExist:
                raise CommandError("This username does not have a token.")
        else:
            print("This password is incorrect.")
