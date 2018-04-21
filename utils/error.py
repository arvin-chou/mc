import traceback
from config.config import _logging
logger = _logging.getLogger(__name__)


ErrorCode = {
    'CE_UNKNOWN_REQUEST': 2001,
    'CE_INVALID_PARAM': 2002,
    'CE_NOT_EXIST': 2003,
    'CE_NAME_CONFLICT': 2004,
    'CE_EXCEED_LIMIT': 2005,
    'CE_DATA_DUPLICATE': 2006,
    'CE_IMAGE_RESIZE': 2007,
    'CE_UNAUTHORIZED': 2008,
}

_ErrorCode = {
    2001: 'CE_UNKNOWN_REQUEST',
    2002: 'CE_INVALID_PARAM',
    2003: 'CE_NOT_EXIST',
    2004: 'CE_NAME_CONFLICT',
    2005: 'CE_EXCEED_LIMIT',
    2006: 'CE_DATA_DUPLICATE',
    2007: 'CE_IMAGE_RESIZE',
    2008: 'CE_UNAUTHORIZED',
}


class CustomError(Exception):
    def __init__(self, code=2001, msg='', *args):
        # *args is used to get a list of the parameters passed in
        self.args = [a for a in args]


def omitError(ErrorToken='CE_UNKNOWN_REQUEST', ErrorMsg='', __ErrorCode=0):
    #logger.debug('traceback.format_exc(%s)', traceback.format_exc())
    #logger.debug('error: errorId:{0}({1}), message: {2}\n'.format(
    #    ErrorCode[ErrorToken], ErrorToken, ErrorMsg))
    return {
            'errorId': ErrorCode[ErrorToken] if 0 == __ErrorCode else _ErrorCode[__ErrorCode],
            'message': ErrorMsg
            }
