#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2012-2016 Snowflake Computing Inc. All right reserved.
#
import logging
from logging import getLogger

from snowflake.connector.constants import UTF8
from .compat import BASE_EXCEPTION_CLASS, PY2


class Error(BASE_EXCEPTION_CLASS):
    u"""
    Exception that is base class for all other error exceptions
    """

    def __init__(self, msg=None, errno=None, sqlstate=None, sfqid=None):
        self.logger = getLogger(__name__)
        self.msg = msg
        self.errno = errno or -1
        self.sqlstate = sqlstate or "n/a"
        self.sfqid = sfqid

        if not self.msg:
            self.msg = u'Unknown error'

        if self.errno != -1:
            if self.sqlstate != "n/a":
                if self.logger.getEffectiveLevel() in (logging.INFO,
                                                       logging.DEBUG):
                    self.msg = u'{errno:06d} ({sqlstate}): {sfqid}: {msg}'.format(
                        errno=self.errno, msg=self.msg,
                        sqlstate=self.sqlstate,
                        sfqid=self.sfqid)
                else:
                    self.msg = u'{errno:06d} ({sqlstate}): {msg}'.format(
                        errno=self.errno,
                        sqlstate=self.sqlstate,
                        msg=self.msg)
            else:
                if self.logger.getEffectiveLevel() in (logging.INFO,
                                                       logging.DEBUG):
                    self.msg = u'{errno:06d}: {sfqid}: {msg}'.format(
                        errno=self.errno, msg=self.msg,
                        sfqid=self.sfqid)
                else:
                    self.msg = u'{errno:06d}: {msg}'.format(errno=self.errno,
                                                            msg=self.msg)

    def __repr__(self):
        return self.__str__()

    def __unicode__(self):
        return self.msg

    def __bytes__(self):
        return self.__unicode__().encode(UTF8)

    @staticmethod
    def default_errorhandler(connection, cursor, errorclass, errorvalue):
        u"""
        Default error handler that raises an error
        """
        raise errorclass(
            msg=errorvalue[u'msg'] if u'msg' in errorvalue else None,
            errno=errorvalue[u'errno'] if u'errno' in errorvalue else None,
            sqlstate=errorvalue[
                u'sqlstate'] if u'sqlstate' in errorvalue else None,
            sfqid=errorvalue[u'sfqid'] if u'sfqid' in errorvalue else None)

    @staticmethod
    def errorhandler_wrapper(connection, cursor, errorclass, errorvalue):
        u"""
        Error handler wrapper that calls the errorhandler method
        """
        if connection is not None:
            connection.messages.append((errorclass, errorvalue))
        if cursor is not None:
            cursor.messages.append((errorclass, errorvalue))
            cursor.errorhandler(connection, cursor, errorclass, errorvalue)
            return
        elif connection is not None:
            connection.errorhandler(connection, cursor, errorclass, errorvalue)
            return

        if issubclass(errorclass, Error):
            raise errorclass(msg=errorvalue[u'msg'],
                             errno=errorvalue[
                                 u'errno'] if u'errno' in errorvalue else None,
                             sqlstate=errorvalue[u'sqlstate'
                             ] if u'sqlstate' in errorvalue else None,
                             sfqid=errorvalue[
                                 u'sfqid'] if u'sfqid' in errorvalue else None)
        else:
            raise errorclass(errorvalue)


if PY2:
    Error.__str__ = lambda self: self.__unicode__().encode(UTF8)
else:
    Error.__str__ = lambda self: self.__unicode__()


class Warning(BASE_EXCEPTION_CLASS):
    u"""Exception for important warnings"""
    pass


class InterfaceError(Error):
    u"""Exception for errors related to the interface"""
    pass


class DatabaseError(Error):
    u"""Exception for errors related to the database"""
    pass


class InternalError(DatabaseError):
    u"""Exception for errors internal database errors"""
    pass


class OperationalError(DatabaseError):
    u"""Exception for errors related to the database's operation"""
    pass


class ProgrammingError(DatabaseError):
    u"""Exception for errors programming errors"""
    pass


class IntegrityError(DatabaseError):
    u"""Exception for errors regarding relational integrity"""
    pass


class DataError(DatabaseError):
    u"""Exception for errors reporting problems with processed data"""
    pass


class NotSupportedError(DatabaseError):
    u"""Exception for errors when an unsupported database feature was used"""
    pass


# internal errors
class InternalServerError(Error):
    u"""Exception for 500 HTTP code for retry"""

    def __init__(self):
        Error.__init__(self, msg=u'HTTP 500: InternalServerError')


class ServiceUnavailableError(Error):
    u"""Exception for 503 HTTP code for retry"""

    def __init__(self):
        Error.__init__(self, msg=u'HTTP 503: ServiceUnavailable')


class GatewayTimeoutError(Error):
    u"""Exception for 504 HTTP error for retry"""

    def __init__(self):
        Error.__init__(self, msg=u'HTTP 504: GatewayTimeout')


class ForbiddenError(Error):
    """Exception for 403 HTTP error for retry"""

    def __init__(self):
        Error.__init__(self, msg=u'HTTP 403: Forbidden')


class RequestTimeoutError(Error):
    u"""Exception for 408 HTTP error for retry"""

    def __init__(self):
        Error.__init__(self, msg=u'HTTP 408: RequestTimeout')


class BadRequest(Error):
    u"""Exception for 400 HTTP error for retry"""

    def __init__(self):
        Error.__init__(self, msg=u'HTTP 400: BadRequest')