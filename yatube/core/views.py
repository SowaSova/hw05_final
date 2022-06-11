from http import HTTPStatus

from django.shortcuts import render


def page_not_found(request, exception):
    template_name = 'core/404.html'
    page_context = {
        'path': request.path,
    }
    return render(
        request, template_name, page_context, status=HTTPStatus.NOT_FOUND
    )


def server_error(request):
    template_name = 'core/500.html'
    return render(
        request, template_name, status=HTTPStatus.INTERNAL_SERVER_ERROR
    )


def permission_denied(request, exception):
    template_name = 'core/403.html'
    return render(request, template_name, status=HTTPStatus.FORBIDDEN)


def csrf_failure(request, reason=''):
    template_name = 'core/403csrf.html'
    return render(request, template_name)
