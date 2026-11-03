"""Project middleware helpers."""
from django.conf import settings


class VietnameseDefaultMiddleware:
    """Make Vietnamese the default language for first-time visitors.

    ``LocaleMiddleware`` falls back to the browser's ``Accept-Language``
    header when the visitor has made no explicit language choice, which
    would show English to e.g. English-configured browsers. This middleware
    rewrites that header to the project default whenever no explicit choice
    (cookie or session) exists yet. Once the visitor picks a language via
    ``set_language``, the ``LANGUAGE_COOKIE_NAME`` cookie takes precedence
    and this middleware stops interfering.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        has_explicit_choice = (
            settings.LANGUAGE_COOKIE_NAME in request.COOKIES
            or request.session.get('_language')
        )
        if not has_explicit_choice:
            request.META['HTTP_ACCEPT_LANGUAGE'] = settings.LANGUAGE_CODE
        return self.get_response(request)


default_language_middleware = VietnameseDefaultMiddleware
