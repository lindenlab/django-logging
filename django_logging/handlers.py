import datetime
import json
import gzip
import time
from logging import StreamHandler, DEBUG
from logging.handlers import RotatingFileHandler
from threading import Thread

from . import settings
from .log_object import LogObject, ErrorLogObject, SqlLogObject


def message_from_record(record):
    if isinstance(record.msg, dict) or isinstance(record.msg, str):
        if settings.DEBUG:
            message = record.msg
        else:
            message = dict(raw=record.msg)
    elif isinstance(record.msg, Exception):
        message = ErrorLogObject.format_exception(record.msg)
    else:
        try:
            message = record.msg.to_dict
        except AttributeError:
            url = "https://github.com/cipriantarta/django-logging/issues"
            return dict(raw="Unable to parse LogObject. Please file in a bug at: %s" % url)
    return message


class DefaultFileHandler(RotatingFileHandler):
    def emit(self, record):
        if isinstance(record.msg, SqlLogObject):
            return
        super(DefaultFileHandler, self).emit(record)
        message = self.format(record)

    def format(self, record):
        created = int(record.created)
        message = message_from_record(record)
        return json.dumps({record.levelname: {created: message}}, sort_keys=True)

    def rotation_filename(self, default_name):
        return '{}-{}.gz'.format(default_name, time.strftime('%Y%m%d'))

    def rotate(self, source, dest):
        with open(source, 'rb+') as fh_in:
            with gzip.open(dest, 'wb') as fh_out:
                fh_out.writelines(fh_in)
            fh_in.seek(0)
            fh_in.truncate()


class DebugFileHandler(DefaultFileHandler):
    def emit(self, record):
        if record.levelno != DEBUG:
            return
        return super(DebugFileHandler, self).emit(record)


class ConsoleHandler(StreamHandler):
    def emit(self, record):
        return super(ConsoleHandler, self).emit(record)

    def format(self, record):
        if isinstance(record.msg, LogObject) or isinstance(record.msg, SqlLogObject) or isinstance(record.msg, ErrorLogObject):
            created = int(record.created)
            if settings.FLATTEN_CONSOLE_LOG:
                # flatten out message so that it has as many keys in the top
                # level of the dict as possible for logging in kibana, which
                # does not support nested objects.
                #
                # https://www.elastic.co/guide/en/kibana/current/nested-objects.html
                message = record.msg.to_dict_flat
                message["level"] = record.levelname

                # This may be unneeded if the formatter already includes a
                # timestamp.
                message["timestamp"] = datetime.datetime.fromtimestamp(created).isoformat()

                # Use "name" to make it easier to filter these out in kibana.
                message["name"] = "djlogger." + ("error" if isinstance(record.msg, ErrorLogObject) else "sql" if isinstance(record.msg, SqlLogObject) else "log")

            else:
                message = {record.levelname: {datetime.datetime.fromtimestamp(created).isoformat(): record.msg.to_dict}}

            # disable pretty printing entirely if indent is disabled so that all
            # of a log message ends up on the same line
            if settings.INDENT_CONSOLE_LOG is None:
                return json.dumps(message, sort_keys=True, indent=settings.INDENT_CONSOLE_LOG)

            try:
                indent = int(settings.INDENT_CONSOLE_LOG)
            except (ValueError, TypeError):
                indent = 1
            import pprint
            message = pprint.pformat(message, indent, 160, compact=True)
            return message
        elif isinstance(record.msg, dict):
            created = int(record.created)
            message = {record.levelname: {created: record.msg}}
            return json.dumps(message, sort_keys=True, indent=settings.INDENT_CONSOLE_LOG)
        else:
            return super(ConsoleHandler, self).format(record)


class SQLFileHandler(RotatingFileHandler):
    def emit(self, record):
        if not isinstance(record.msg, SqlLogObject):
            return
        super(SQLFileHandler, self).emit(record)
        message = self.format(record)

    def format(self, record):
        created = int(record.created)
        message = {record.levelname: {created: record.msg.to_dict}}
        return json.dumps(message, sort_keys=True)

    def rotation_filename(self, default_name):
        return '{}-{}.gz'.format(default_name, time.strftime('%Y%m%d'))

    def rotate(self, source, dest):
        with open(source, 'rb+') as fh_in:
            with gzip.open(dest, 'wb') as fh_out:
                fh_out.writelines(fh_in)
            fh_in.seek(0)
            fh_in.truncate()
