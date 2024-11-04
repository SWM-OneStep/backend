import sentry_sdk


def set_sentry_user(user):
    sentry_sdk.set_user(
        {
            "id": user.id,
            "username": user.username,
        }
    )


def sentry_validation_error(where: str, error, user_id):
    sentry_sdk.capture_message(
        "Validation Error in" + where,
        level="error",
        extra={"error": error, "user_id": user_id},
    )
