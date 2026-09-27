def detect_device(user_agent: str | None) -> str:
    if not user_agent:
        return "unknown"

    ua = user_agent.lower()
    if "mobile" in ua or "android" in ua or "iphone" in ua:
        return "mobile"
    if "tablet" in ua or "ipad" in ua:
        return "tablet"
    return "desktop"


def detect_browser(user_agent: str | None) -> str:
    if not user_agent:
        return "unknown"

    ua = user_agent.lower()
    if "edg" in ua:
        return "edge"
    if "chrome" in ua and "safari" in ua:
        return "chrome"
    if "firefox" in ua:
        return "firefox"
    if "safari" in ua:
        return "safari"
    if "opera" in ua or "opr" in ua:
        return "opera"
    return "other"
