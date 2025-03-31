import json
from authlib.integrations.django_client import OAuth
from django.conf import settings
from django.shortcuts import redirect, render, redirect
from django.urls import reverse
from urllib.parse import quote_plus, urlencode

oauth = OAuth()

oauth.register(
    "auth0",
    client_id=settings.AUTH0_CLIENT_ID,
    client_secret=settings.AUTH0_CLIENT_SECRET,
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f"https://{settings.AUTH0_DOMAIN}/.well-known/openid-configuration",
)

def login(request):
    return oauth.auth0.authorize_redirect(
        request, request.build_absolute_uri(reverse("callback"))
    )

def callback(request):
    try:
        token = oauth.auth0.authorize_access_token(request)
    except:
        return redirect(request.build_absolute_uri(reverse("index")))
    request.session["user"] = token
    return redirect(request.build_absolute_uri(reverse("home")))

def index(request):
    return render(request, "index.html")

def home(request):
    if not request.session.get("user"):
        return redirect(request.build_absolute_uri(reverse("login")))
    return render(request, "home.html", context={
            "user_data": request.session.get("user"),
        },
    )

def logout(request):
    if not request.session.get("user"):
        return redirect(request.build_absolute_uri(reverse("login")))
    request.session.clear()
    return redirect(
        f"https://{settings.AUTH0_DOMAIN}/v2/logout?"
        + urlencode(
            {
                "returnTo": request.build_absolute_uri(reverse("index")),
                "client_id": settings.AUTH0_CLIENT_ID,
            },
            quote_via=quote_plus,
        ),
    )