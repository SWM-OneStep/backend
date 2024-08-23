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


def sentry_data(method, url, status_code, headers):
    span = sentry_sdk.start_span(
        op="http.request",
        description="%s %s" % (method, url),
    )

    span.set_data("http.reqeust.method", method)

    span.set_data("http.request.url", url)

    span.set_data("http.response.status_code", status_code)
    span.set_data("http.response_content_length", headers["content-length"])

    span.finish()
