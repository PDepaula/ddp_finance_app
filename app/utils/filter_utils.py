def pluralize(count, singular='', plural='s'):
    """
    Returns singular if count is 1, plural otherwise.

    Args:
        count: The count to check
        singular: String to return when count is 1
        plural: String to return when count is not 1
    
    Returns:
        The appropriate suffix based on the count
    """
    return singular if count == 1 else plural