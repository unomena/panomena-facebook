

class FacebookMiddlewareRequiredException(Exception):
    """Exception that should be raised when facebook middleware functionality
    was required but not found.

    """

    def __init__(self, value):
        if value:
            value = 'Facebook Middleware has to be installed to use %s.' % value
        else:
            value = 'Facebook Middleware required.'
        super(FacebookMiddlewareRequiredException, self).__init__(value)


class SignedRequestNotParsedException(Exception):
    """Exception that's raised if the signed request could not be parsed."""

    def __init__(self, value=None):
        if not value:
            value = 'Facebook signed request could not be parsed.'
        super(SignedRequestNotParsedException, self).__init__(value)

