# car_model/middleware.py
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

class AutoRefreshJWTMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        access = request.session.get("access_token")
        refresh = request.session.get("refresh_token")

        if access and refresh:
            try:
                # Validate access token
                AccessToken(access)
            except Exception:
                # Access expired → refresh it
                try:
                    refresh_obj = RefreshToken(refresh)
                    new_access = refresh_obj.access_token
                    request.session["access_token"] = str(new_access)
                    request.META["HTTP_AUTHORIZATION"] = f"Bearer {new_access}"
                except Exception:
                    pass

        return self.get_response(request)
