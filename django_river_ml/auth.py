from django.urls import resolve
from django.contrib.auth.models import User

from django_river_ml import settings
import django_river_ml.utils as utils

from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from django.middleware import cache

from datetime import datetime
import uuid
import base64
import re
import time
import jwt


def is_authenticated(request):
    """
    Function to check if a request is authenticated.
    Returns a boolean to indicate if the user is authenticated, and a response with
    the challenge if not.

    request (requests.Request)    : the Request object to inspect
    """
    # Derive the view name from the request PATH_INFO
    func, _, _ = resolve(request.META["PATH_INFO"])
    view_name = "%s.%s" % (func.__module__, func.__name__)

    # If authentication is disabled, return the original view
    if settings.DISABLE_AUTHENTICATION or view_name not in settings.AUTHENTICATED_VIEWS:
        return True, None, None

    # Case 2: Already has a jwt valid token
    is_valid, user = validate_jwt(request)
    if is_valid:
        return True, None, user

    # Case 3: False and response will return request for auth
    user = get_user(request)
    if not user:
        headers = {"Www-Authenticate": get_challenge(request)}
        return False, Response(status=401, headers=headers), user

    # Denied for any other reason
    return False, Response(status=403), user


def generate_jwt(username):
    """Given a username generate a jwt
    token to return to the user with a default expiration of 10 minutes.

    username (str)  : the user's username to add under "sub"
    """
    # The jti expires after TOKEN_EXPIRES_SECONDS
    issued_at = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    filecache = cache.caches["django_river_ml"]
    jti = str(uuid.uuid4())
    filecache.set(jti, "good", timeout=settings.TOKEN_EXPIRES_SECONDS)
    now = int(time.time())
    expires_at = now + settings.TOKEN_EXPIRES_SECONDS

    # import jwt and generate token
    # https://tools.ietf.org/html/rfc7519#section-4.1.5
    payload = {
        "sub": username,
        "exp": expires_at,
        "nbf": now,
        "iat": now,
        "jti": jti,
    }
    token = jwt.encode(payload, settings.JWT_SERVER_SECRET, algorithm="HS256")
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return {
        "token": token,
        "expires_in": settings.TOKEN_EXPIRES_SECONDS,
        "issued_at": issued_at,
    }


def validate_jwt(request):
    """
    Given a jwt token, decode and validate

    request (requests.Request)    : the Request object to inspect
    """
    header = request.META.get("HTTP_AUTHORIZATION", "")
    if re.search("bearer", header, re.IGNORECASE):
        encoded = re.sub("bearer", "", header, flags=re.IGNORECASE).strip()

        # Any reason not valid will issue an error here
        try:
            decoded = jwt.decode(
                encoded, settings.JWT_SERVER_SECRET, algorithms=["HS256"]
            )
        except Exception as exc:
            print("jwt could no be decoded, %s" % exc)
            return False, None

        # Ensure that the jti is still valid
        filecache = cache.caches["django_river_ml"]
        if not filecache.get(decoded.get("jti")) == "good":
            print("Filecache with jti not found.")
            return False, None

        # The user must exist
        try:
            user = User.objects.get(username=decoded.get("sub"))
            return True, user
        except User.DoesNotExist:
            print("Username %s not found" % decoded.get("sub"))
            return False, None

    return False, None


def get_user(request):
    """Given a request, read the Authorization header to get the base64 encoded
    username and token (password) which is a basic auth. If we return the user
    object, the user is successfully authenticated. Otherwise, return None.
    and the calling function should return Forbidden status.

    request (requests.Request)    : the Request object to inspect
    """
    header = request.META.get("HTTP_AUTHORIZATION", "")
    if re.search("basic", header, re.IGNORECASE):
        encoded = re.sub("basic", "", header, flags=re.IGNORECASE).strip()
        decoded = base64.b64decode(encoded).decode("utf-8")
        username, token = decoded.split(":", 1)
        try:
            token = Token.objects.get(key=token)
            if token.user.username == username:
                return token.user
        except:
            pass


def get_token(request):
    """The same as validate_token, but return the token object to check the
    associated user.

    request (requests.Request)    : the Request object to inspect
    """
    # Coming from HTTP, look for authorization as bearer token
    token = request.META.get("HTTP_AUTHORIZATION")

    if token:
        try:
            return Token.objects.get(key=token.replace("BEARER", "").strip())
        except Token.DoesNotExist:
            pass

    # Next attempt - try to get token via user session
    elif request.user.is_authenticated and not request.user.is_anonymous:
        try:
            return Token.objects.get(user=request.user)
        except Token.DoesNotExist:
            pass


def get_challenge(request):
    """Given an unauthenticated request, return a challenge in
    the Www-Authenticate header

    request (requests.Request): the Request object to inspect
    """
    DOMAIN_NAME = utils.get_server(request)
    auth_server = "%s/%s/auth/token" % (DOMAIN_NAME, settings.URL_PREFIX)
    return 'realm="%s",service="%s"' % (
        auth_server,
        DOMAIN_NAME,
    )
