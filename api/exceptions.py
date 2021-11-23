from config import logger

__all__ = ['Error', 'BadGatewayError', 'WrongResponseException', 'BadAPIKeyException', 'InsufficientFundsException',
           'UnknownError', 'TooManyRequests', 'BadRequestError']


class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class BadAPIKeyException(Error):
    """Bad api key exception."""

    def __init__(self):
        logger.error('Bad API key used or Unauthorized')


class WrongResponseException(Error):
    """An invalid response was received from the server"""

    def __init__(self, response_text: str):
        """
        :param response: Received response.
        """
        logger.error(f'Wrong response was received {response_text}')
        self.response = response_text


class UnknownError(Error):
    """A unknown error occured."""

    def __init__(self, text: str):
        """
        :param text: Error text.
        """
        logger.error('Response contains unknown error')
        logger.debug(text)
        self.response = text


class InsufficientFundsException(Error):
    """Insufficient funds to complete the transaction."""
    pass


class TooManyRequests(Error):
    """The server received too many requests."""
    pass


class BadGatewayError(Error):

    def __init__(self, text: str = ''):
        """
        :param text: Error text
        """
        if text == '':
            logger.error('Bad gateway error')
        else:
            logger.error(text)
        self.response = text


class BadRequestError(Error):
    """A incorrect method call occured."""
    pass
