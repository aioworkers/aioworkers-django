import sqlalchemy
from orm import NoMatch

from aioworkers_django.models import DjangoModel
from tests.app.polls.models import Question as DjangoQuestion


class Question(DjangoModel):
    __django_model__ = DjangoQuestion

    @classmethod
    async def get_by_id_sql(cls, i):
        t = cls.objects.table
        sql = sqlalchemy.select([t.c.id]).select_from(t).where(t.c.id == i)
        o = await cls.objects.database.fetch_one(query=sql)
        if not o:
            raise NoMatch()
        return cls.from_row(o)
