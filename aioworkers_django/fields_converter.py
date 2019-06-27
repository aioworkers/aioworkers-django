import logging

import sqlalchemy as sa
import sqlalchemy.types as sa_types
from django.db.models import ForeignKey, OneToOneField
from sqlalchemy.dialects.postgresql import ARRAY as SA_ARRAY
from sqlalchemy.dialects.postgresql import JSONB as SA_JSONB
from sqlalchemy.dialects.postgresql import UUID as SA_UUID

logger = logging.getLogger(__name__)

"""
# Inspired by https://github.com/dvhb/dvhb-hybrid/blob/master/dvhb_hybrid/amodels/convert.py
"""


class ConversionError(Exception):
    pass


class DjangoFieldConverter:
    types = {
        # Django internal type => SQLAlchemy type
        'ArrayField': SA_ARRAY,
        'AutoField': sa_types.Integer,
        'BigAutoField': sa_types.BigInteger,
        'BigIntegerField': sa_types.BigInteger,
        'BooleanField': sa_types.Boolean,
        'CharField': sa_types.String,
        'DateField': sa_types.Date,
        'DateTimeField': sa_types.DateTime,
        'DecimalField': sa_types.Numeric,
        'DurationField': sa_types.Interval,
        'FileField': sa_types.String,
        'FilePathField': sa_types.String,
        'FloatField': sa_types.Float,
        'GenericIPAddressField': sa_types.String,
        'IntegerField': sa_types.Integer,
        'JSONField': SA_JSONB,
        'NullBooleanField': sa_types.Boolean,
        'PositiveIntegerField': sa_types.Integer,
        'PositiveSmallIntegerField': sa_types.SmallInteger,
        'SlugField': sa_types.String,
        'SmallIntegerField': sa_types.SmallInteger,
        'TextField': sa_types.Text,
        'TimeField': sa_types.Time,
        'UUIDField': SA_UUID,
    }

    @classmethod
    def _convert_type(cls, dj_field, sa_type):
        kwargs = {}
        if sa_type is SA_ARRAY:
            internal_type = dj_field.base_field.get_internal_type()
            kwargs['item_type'] = cls.types.get(internal_type)
            if kwargs['item_type'] is None:
                raise ConversionError(
                    'Unable convert array: '
                    'item type "%s" not found' % internal_type
                )
        elif sa_type is sa_types.Numeric:
            kwargs['scale'] = dj_field.decimal_places,
            kwargs['precision'] = dj_field.max_digits
        elif sa_type in (sa_types.String, sa_types.Text):
            kwargs['length'] = dj_field.max_length
        elif sa_type is SA_UUID:
            kwargs['as_uuid'] = True
        return sa_type(**kwargs)

    @classmethod
    def convert(cls, dj_field):
        result = []
        if isinstance(dj_field, (ForeignKey, OneToOneField)):
            result.append(dj_field.column)
            convert_from = dj_field.target_field
        else:
            result.append(dj_field.name)
            convert_from = dj_field
        internal_type = convert_from.get_internal_type()
        convert_to = cls.types.get(internal_type)
        if convert_to is not None:
            result.append(cls._convert_type(convert_from, convert_to))
        else:
            logger.info(
                'Not found corresponding '
                'SQLAlchemy type for "%s"(%r)',
                internal_type,
                dj_field
            )
        return sa.column(*result)
