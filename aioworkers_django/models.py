import logging

from aioworkers_orm.models import AIOWorkersModelMetaClass, Model, Models
from aioworkers_orm.registry import ModelsRegistry
from orm.models import ModelMetaclass

from aioworkers_django.fields_converter import DjangoFieldConverter

logger = logging.getLogger(__name__)


class DjangoModelMetaClass(AIOWorkersModelMetaClass):
    def __new__(mcls, name, bases, attrs) -> type:
        django_model = attrs.get('__django_model__')

        if django_model is None and not attrs.get('__abstract__'):
            raise ValueError('Django model has to be specified.')

        cls = super(ModelMetaclass, mcls).__new__(mcls, name, bases, attrs)

        return cls


class DjangoModel(Model, metaclass=DjangoModelMetaClass):
    """
    A base model which have to be used if django model have to be extended with custom
    sqlalchemy methods.
    """
    __abstract__ = True
    __django_model__ = None


class DjangoModels(Models):
    """
    Entity to load Django models into aioworkers context.
    """

    def create_models(self):
        import django.apps
        models = self.config.get('models', {})
        for model_name, model_label in models.items():
            model = django.apps.apps.get_model(model_label)

            ModelsRegistry.create_model(**self.get_model_spec(model))
            self._ids.add(model_label)

    def get_model_spec(self, model):
        options = model._meta
        fields = []
        for field in options.get_fields():
            fields.append(DjangoFieldConverter.convert(field))
        return dict()
