# home/middleware.py

from django.shortcuts import redirect
from django.urls import reverse

class RedirectUnauthenticatedMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            # Redirect to landing page if the user is not authenticated
            if request.path != reverse('login'):
                return redirect('login')
        return self.get_response(request)
