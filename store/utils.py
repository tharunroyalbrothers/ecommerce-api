from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, PermissionDenied, ValidationError

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, NotAuthenticated):
        return Response(
            {"message": "Please login through your account before accessing this resource."},
            status=status.HTTP_401_UNAUTHORIZED
        )

    if isinstance(exc, PermissionDenied):
        return Response(
            {"message": str(exc)},
            status=status.HTTP_403_FORBIDDEN
        )

    if isinstance(exc, ValidationError):
        if isinstance(exc.detail, list) and exc.detail:
            return Response({"message": exc.detail[0]}, status=status.HTTP_400_BAD_REQUEST)
        elif isinstance(exc.detail, dict) and exc.detail:
            first_error = next(iter(exc.detail.values()))
            if isinstance(first_error, list) and first_error:
                return Response({"message": first_error[0]}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"message": str(first_error)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": str(exc.detail)}, status=status.HTTP_400_BAD_REQUEST)

    return response
