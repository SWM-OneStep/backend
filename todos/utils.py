import sentry_sdk

from todos.lexorank import LexoRank


def validate_lexo_order(prev, next, updated):
    updated_lexo = LexoRank(updated)
    if prev is None and next is None:
        return True
    if prev is None:
        next_lexo = LexoRank(next)
        if next_lexo.compare_to(updated_lexo) <= 0:
            return False
    elif next is None:
        prev_lexo = LexoRank(prev)
        if prev_lexo.compare_to(updated_lexo) >= 0:
            return False
    else:
        prev_lexo = LexoRank(prev)
        next_lexo = LexoRank(next)
        if (
            prev_lexo.compare_to(updated_lexo) >= 0
            or next_lexo.compare_to(updated_lexo) <= 0
        ):
            return False
    return True


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
