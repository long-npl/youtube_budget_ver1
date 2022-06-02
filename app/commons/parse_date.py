from dateutil.parser import parse as base_parse, ParserError
import datetime


class NoDefaultDate(object):

    def replace(self, **fields):
        none_fields = [f for f in ('year', 'month', 'day') if f not in fields]
        if len(none_fields) > 0:
            raise ParserError(f"missing {','.join(none_fields)} info")
        return datetime.datetime(1994, 1, 1).replace(**fields)

    @property
    def day(self):
        raise ParserError("missing day info")

    @property
    def month(self):
        raise ParserError("missing month info")

    @property
    def year(self):
        raise ParserError("missing year info")


def parse_date(v: str):
    return base_parse(v, default=NoDefaultDate()).date()


def parse(v: str):
    return base_parse(v, default=NoDefaultDate())
