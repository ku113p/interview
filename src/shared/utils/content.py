def normalize_content(content: object) -> str:
    """Convert message content to string representation.

    Handles various content types including lists and objects.

    Args:
        content: Content to normalize (can be list, string, or any object)

    Returns:
        str: String representation of content
    """
    if isinstance(content, list):
        return "".join(str(part) for part in content)
    if isinstance(content, str):
        return content
    return str(content)
