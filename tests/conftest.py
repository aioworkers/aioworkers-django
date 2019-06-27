import pytest


@pytest.fixture(scope='session')
def db_name():
    return 'test.db.sqlite'


@pytest.fixture(scope='session')
def db_url(db_name):
    return f"sqlite:///{db_name}"


@pytest.fixture
def config_yaml(db_url):
    return f"""
    db:
      cls: aioworkers_orm.databases.Database
      dsn: {db_url}
    models:
      cls: aioworkers_django.models.DjangoModels
      database: db
      models:
        question: polls.Question
        choice: polls.Choice
    """
