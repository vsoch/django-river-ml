def get_server(request):
    """
    Given a request, parse it to determine the server name and using http/https
    """
    scheme = request.is_secure() and "https" or "http"
    return f"{scheme}://{request.get_host()}"


def format_sse(data: str, event=None) -> str:
    """
    >>> format_sse(data=json.dumps({'abc': 123}), event='Jackson 5')
    'event: Jackson 5\\ndata: {"abc": 123}\\n\\n'
    """
    msg = f"data: {data}\n\n"
    if event is not None:
        msg = f"event: {event}\n{msg}"
    return msg


def humanize_ns(ns: int) -> str:

    if ns == 0:
        return "0ns"

    μs = ("μs", 1000)
    ms = ("ms", μs[1] * 1000)
    s = ("s", ms[1] * 1000)
    m = ("m", s[1] * 60)

    rep = ""

    for d in (m, s, ms, μs):
        k, ns = divmod(ns, d[1])
        if k:
            rep += f"{k}{d[0]}"

    if ns:
        rep += f"{ns}ns"

    return rep
