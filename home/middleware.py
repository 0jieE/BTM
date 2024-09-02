# home/middleware.py

from django.shortcuts import redirect
from django.urls import reverse

class RedirectUnauthenticatedMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # List of paths that do not require authentication
        allowed_paths = [reverse('login'), reverse('staff-register'), reverse('admin-register')]

        if not request.user.is_authenticated:
            # Redirect to login page if the user is not authenticated and the path is not in allowed_paths
            if request.path not in allowed_paths:
                return redirect('login')

        return self.get_response(request)
