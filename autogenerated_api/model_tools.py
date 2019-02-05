"""
    @author : RituRaj
    updated : 5 feb , 2019
"""


from django.apps import apps
from django.conf import settings

AUTOGENERATE_APPS = settings.AUTOGENERATE_APPS

LOCALCONCRETE = "#LOCAL"
NONREL = "#NONREL"
FKEY = "#FKEY"
REVFKEY = "#REVFKEY"
M2M = "#M2M"
REVM2M = "#REVM2M"


_LOADED = []
_APP_MODELS = {}
_MODEL_OBJECTS = {}

_LOCAL_CONCRETE_FIELD_NAMES = {}
_NON_RELATION_FIELD_NAMES = {}
_FOREIGN_KEY_NAMES = {}
_REVERSE_FOREIGN_KEY_NAMES = {}
_M2M_FIELD_NAMES = {}
_REVERSE_M2M_FIELD_NAMES = {}


def get_models(app_name):
    if app_name in _APP_MODELS:
        return _APP_MODELS[app_name]
    models = list(apps.get_app_config(app_name).get_models())

    _APP_MODELS[app_name] = models
    for m in models:
        _MODEL_OBJECTS[m.__name__] = m

    return models

def _lazy_load():
    global _LOADED
    if not _LOADED:
        success = True
        for app_name in AUTOGENERATE_APPS:
            try:
                get_models(app_name)
            except:
                success = False
        if success:
            _LOADED = True


############### FUNCTIONS ###############

def _fix_type(model):
    if type(model) == str:
        model_name = model
        model = _MODEL_OBJECTS[model]
    else:
        model_name = model.__name__
    return (model, model_name)

# x is a list
def _pre_set(x):
    return list(x)

# a list should be returned
def _pre_get(x):
    return list(x)

# a structure supporting ".in" should be returned
# name means "get x in a set-like form"
def _get_set(x):
    return x


def get_local_concrete_fields(model):
    model, model_name = _fix_type(model)

    if model_name in _LOCAL_CONCRETE_FIELD_NAMES:
        return _pre_get(_LOCAL_CONCRETE_FIELD_NAMES[model_name])

    lc_fields = []
    fk_fields = []
    nr_fields = []

    for f in model._meta.local_concrete_fields:
        lc_fields.append(f.name)
        if f.is_relation:
            fk_fields.append(f.name)
        else:
            nr_fields.append(f.name)

    _LOCAL_CONCRETE_FIELD_NAMES[model_name] = _pre_set(lc_fields)
    _FOREIGN_KEY_NAMES[model_name] = _pre_set(fk_fields)
    _NON_RELATION_FIELD_NAMES[model_name] = _pre_set(nr_fields)

    return lc_fields

def get_foreign_keys(model):
    model, model_name = _fix_type(model)

    if model_name in _FOREIGN_KEY_NAMES:
        return _pre_get(_FOREIGN_KEY_NAMES[model_name])

    get_local_concrete_fields()
    return _FOREIGN_KEY_NAMES[model_name]


def get_non_relational_fields(model):
    model, model_name = _fix_type(model)

    if model_name in _NON_RELATION_FIELD_NAMES:
        return _pre_get(_NON_RELATION_FIELD_NAMES[model_name])

    get_local_concrete_fields()
    return _NON_RELATION_FIELD_NAMES[model_name]


def get_m2m_fields(model):
    model, model_name = _fix_type(model)

    if model_name in _M2M_FIELD_NAMES:
        return _pre_get(_M2M_FIELD_NAMES[model_name])

    result = [field.name for field in model._meta.many_to_many]
    _M2M_FIELD_NAMES[model_name] = _pre_set(result)
    return result


def get_reverse_foreign_keys(model):
    model, model_name = _fix_type(model)

    if model_name in _REVERSE_FOREIGN_KEY_NAMES:
        return _pre_get(_REVERSE_FOREIGN_KEY_NAMES[model_name])

    # result = [field.name for field in model._meta.get_all_related_objects()] # deprecated in latest version of django
    result = [field.name for field in model._meta.get_fields() if (field.one_to_one or field.one_to_many)]
    _REVERSE_FOREIGN_KEY_NAMES[model_name] = _pre_set(result)
    return result

def get_reverse_m2m_fields(model):
    model, model_name = _fix_type(model)

    if model_name in _REVERSE_M2M_FIELD_NAMES:
        return _pre_get(_REVERSE_M2M_FIELD_NAMES[model_name])

    # result = [field.name for field in model._meta.get_all_related_many_to_many_objects()]
    result = [field.name for field in model._meta.get_fields() if field.many_to_many]
    _REVERSE_M2M_FIELD_NAMES[model_name] = _pre_set(result)
    return result

def get_all_fields(model):
    result = get_local_concrete_fields(model) + get_m2m_fields(model) + get_reverse_m2m_fields(model) + get_reverse_foreign_keys(model)
    return result

def get_direct_fields(model):
    result = get_local_concrete_fields(model) + get_m2m_fields(model)
    return result

SYNTAX = {
    "LOCAL_CONCRETE_STR": (LOCALCONCRETE, get_local_concrete_fields),
    "NON_RELATION_STR": (NONREL, get_non_relational_fields),
    "FOREIGN_KEY_STR": (FKEY, get_foreign_keys),
    "REVERSE_FOREIGN_KEY_STR": (REVFKEY, get_reverse_foreign_keys),
    "M2M_FIELD_STR": (M2M, get_m2m_fields),
    "REVERSE_M2M_FIELD_STR": (REVM2M, get_reverse_m2m_fields)
}


def field_processor(field_list, model):
    _lazy_load()
    model, model_name = _fix_type(model)
    field_set = set(field_list)

    for key in SYNTAX:
        hashstr, getter = SYNTAX[key]
        if hashstr in field_set:
            field_set.remove(hashstr)
            field_set = field_set.union(getter(model))

    return list(field_set)
