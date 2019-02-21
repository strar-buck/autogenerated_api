"""
    @author : RituRaj
    Updated : 21 Feb , 2019
    Generating. Autogenerated serializers used for django models 
"""

# from sets import Set
from django.db.models.fields.files import FieldFile
import django
from .model_tools import (
    get_direct_fields,
    field_processor
)

def DeadlySerializerFactory(model, fields=None, exclude=None, nest=[], nested_fields={}, force_nesting=False, exclude_nest=[]):
    """
        DOCUMENTATION

        :param model : model_name 
        :param fields : Curerntly simple , can be something else in future 

        :param force_nesting:
                If this is true, then for any field which is present in `fields`:
                    * If it has Model.default_nest_fields, then it is nested
                If this is false, then all fields will be used as explicitly specified.

        :param nested_fields:
                Format: {"field_in_relation": ["field1", "field2"]}
                If nested_fields["model_name"] is not specified for a nested field, then:
                    * If Models.default_nesting_fields exists, then this is the list of nested fields
                    * Otherwise, only ID is nested (you shouldn't have nested this field)
        
        :param exclude:
                Takes precedence over `fields`

        Documentation By : RituRaj
    """
    if fields is None:
        fields = "simple"
    if fields == "simple":
        fields = get_direct_fields(model)

    fields = field_processor(fields, model)

    if exclude is not None:
        exclude = field_processor(exclude, model)
        fields = list(fields)
        for i in exclude:
            if i in fields:
                fields.remove(i)
        fields = tuple(fields)

    nest = field_processor(nest, model)

    for x in exclude_nest:
        if x in nest:
            nest.remove(x)

    class ModelDeadlySerializer(object):
        model_foreignkeys = None
        model_related_foreignkeys = None
        model_reverse_o2o_fields = None
        model_local_concrete_fields = None
        model_m2m_fields = None
        model_reverse_m2m_fields = None
        model_relational_fields = None

        def check_field(self, fname):
            if self.fields is None:
                return True
            return fname in self.fields

        def filter_values_list_by_field(self, dict_list, field_name):                                                          
            x = {}
            id_set = set()
            for d in dict_list:
                if d['id'] not in id_set:
                    id_set.add(d['id'])
                    x[d['id']] = {}
                    x[d['id']][field_name]=set()
                    if d[field_name] is not None:
                        x[d['id']][field_name].add(d[field_name])
                else:
                    if d[field_name] not in x[d['id']]:
                        x[d['id']][field_name].add(d[field_name])

            for k in x:
                x[k][field_name] = list(x[k][field_name])

            return x

        def postprocess_values_list(self, dict_list, fields, related_model):

            if 'id' not in fields:
                fields.append('id')

            id_set = set()
            dict_dict = {}
            for d in dict_list:
                if d['id'] not in id_set:
                    id_set.add(d['id'])
                    dict_dict[d['id']] = d
            
            ret_dict = {}
            for index in id_set:
                ret_dict[index] = {}

            for f in fields:
                field_ref = related_model._meta.get_field(f)
                if field_ref.many_to_many or field_ref.one_to_many:
                    res = self.filter_values_list_by_field(dict_list, f)
                    for index in id_set:
                        ret_dict[index][f] = res[index][f]
                else:
                    for index in id_set:
                        ret_dict[index][f] = dict_dict[index][f]

            ret_list = [ret_dict[index] for index in id_set]

            return ret_list

        def load_fields(self):
            # Local Concrete Fields (includes gen fields as well as ForeignKeys)
            if ModelDeadlySerializer.model_local_concrete_fields is None:
                ModelDeadlySerializer.model_local_concrete_fields = []
                temp = []
                for f in model._meta.local_concrete_fields:
                    temp.append(f.name)
                ModelDeadlySerializer.model_local_concrete_fields = set(temp)


            self.local_concrete_fields = []
            for f in ModelDeadlySerializer.model_local_concrete_fields:
                if self.check_field(f):
                    self.local_concrete_fields.append(f)


            if ModelDeadlySerializer.model_foreignkeys is None:
                # Segregating ForeignKeys from local_concrete_fields
                ModelDeadlySerializer.model_foreignkeys = set([field.name for field in model._meta.local_concrete_fields if field.is_relation])


            # Many To Many Fields
            if ModelDeadlySerializer.model_m2m_fields is None:
                ModelDeadlySerializer.model_m2m_fields = set([field.name for field in model._meta.many_to_many])

            self.m2m_fields = []
            for f in ModelDeadlySerializer.model_m2m_fields:
                if self.check_field(f):
                    self.m2m_fields.append(f)

            # Reverse ForeignKeys
            if ModelDeadlySerializer.model_related_foreignkeys is None:
                ModelDeadlySerializer.model_related_foreignkeys = set([field.name for field in model._meta.get_fields() if field.one_to_many])

            self.related_foreignkeys = []

            for f in ModelDeadlySerializer.model_related_foreignkeys:
                if self.check_field(f):
                    self.related_foreignkeys.append(f)

            # Reverse One-To-One Fields
            if ModelDeadlySerializer.model_reverse_o2o_fields is None:
                ModelDeadlySerializer.model_reverse_o2o_fields = set([field.name for field in model._meta.get_fields() if field.one_to_one])

            self.reverse_o2o_fields = []

            for f in ModelDeadlySerializer.model_reverse_o2o_fields:
                if self.check_field(f):
                    self.reverse_o2o_fields.append(f)

            # Reverse M2M fields
            if ModelDeadlySerializer.model_reverse_m2m_fields is None:
                ModelDeadlySerializer.model_reverse_m2m_fields = set([field.name for field in model._meta.get_fields() if field.many_to_many])

            self.reverse_m2m_fields = []

            for f in ModelDeadlySerializer.model_reverse_m2m_fields:
                if self.check_field(f):
                    self.reverse_m2m_fields.append(f)

            if ModelDeadlySerializer.model_relational_fields is None:
                ModelDeadlySerializer.model_relational_fields = set().union(
                    ModelDeadlySerializer.model_foreignkeys,
                    ModelDeadlySerializer.model_m2m_fields,
                    ModelDeadlySerializer.model_related_foreignkeys,
                    ModelDeadlySerializer.model_reverse_o2o_fields,
                    ModelDeadlySerializer.model_reverse_m2m_fields
                )

        def __init__(self, queryset, *args, **kwargs):

            if type(queryset) == django.db.models.QuerySet or type(queryset) == list:
                many = True
            else:
                many = False

            if not many:
                queryset = [queryset]

            # Get fields
            fields_list = kwargs.pop("fields", fields)
            exclude = kwargs.pop("exclude", None)
            fields_list = field_processor(fields_list, model)
            self.fields = set(fields_list)
            if exclude:
                exclude = field_processor(exclude)
                for item in exclude:
                    self.fields.remove(item)

            self.fields.add("id")

            nest_tuple = kwargs.pop("nest", nest)
            nest_tuple = field_processor(nest_tuple, model)
            self.nest = set(nest_tuple)

            if self.fields and self.nest:
                self.fields = self.fields.union(self.nest)

            self.load_fields()


            self.nested_fields_dict = kwargs.pop("nested_fields", nested_fields)
            self.force_nesting = kwargs.pop("force_nesting", force_nesting)
            self.exclude_nest = kwargs.pop("exclude_nest", exclude_nest)

            for item in exclude_nest:
                if item in self.nest:
                    self.nest.remove(item)

            result = []
            result_map = {}
            if type(queryset) is list:
                for item in queryset:
                    item_dict = {}
                    for f in self.local_concrete_fields:
                        if model._meta.get_field(f).is_relation:
                            item_dict[f] = getattr(item, f+"_id")
                        else:
                            try:
                                x = getattr(item, f)
                                if x.field.attr_class is FieldFile:
                                    item_dict[f] = x.name
                            except:
                                item_dict[f] = x
                    result.append(item_dict)
                    result_map[item_dict["id"]] = item_dict
            else:
                temp_result = queryset.values(*(self.local_concrete_fields))
                for item in temp_result:
                    result.append(item)
                    result_map[item["id"]] = item

            model_id_list = list(result_map)

            for x in self.m2m_fields:
                for r in result:
                    r[x] = []

                f = getattr(model, x)
                ThroughModel = f.through

                through_reverse_name = f.field.m2m_column_name()

                query_dict = {}
                query_dict[through_reverse_name+"__in"] = model_id_list

                through_queryset = ThroughModel.objects.filter(**query_dict).values()

                for tq in through_queryset:
                    result_map[tq[through_reverse_name]][x].append(tq[f.field.m2m_reverse_name()])

            for x in self.reverse_o2o_fields:
                query_dict = {}
                f = getattr(model, x)
                reverse_related_name = f.related.field.name
                query_dict[reverse_related_name+"_id__in"] = model_id_list
                qs = f.related.related_model.objects.filter(**query_dict).values()
                for val in qs:
                    result_map[val[reverse_related_name+"_id"]][x] = val['id']

            for x in self.reverse_m2m_fields:
                # for r in result:
                #     r[x] = []

                # f = getattr(model, x).related # for django == 1.8
                f = getattr(model, x).rel # for latest version of django
                ThroughModel = f.through
                through_reverse_name = f.field.m2m_reverse_name()

                query_dict = {}
                query_dict[through_reverse_name+"__in"] = model_id_list

                through_queryset = ThroughModel.objects.filter(**query_dict).values()

                for tq in through_queryset:
                    result_map[tq[through_reverse_name]][x].append(tq[f.field.m2m_column_name()])

            for x in self.related_foreignkeys:
                for r in result:
                    r[x] = []

                rel_obj = getattr(model, x).related
                RelatedModel = rel_obj.related_model

                reverse_name = rel_obj.field.name + "_id"  # eq. parent_id

                query_dict = {}
                query_dict[reverse_name + "__in"] = model_id_list

                rel_queryset = RelatedModel.objects.filter(**query_dict).values('id', reverse_name)

                for rq in rel_queryset:
                    result_map[rq[reverse_name]][x].append(rq['id'])

            if self.force_nesting:
                for x in self.fields:
                    # If already decided to nest, move on
                    if x in self.nest or x in self.exclude_nest:
                        continue
                    # If has default nesting fields specified, then nest!
                    if x in ModelDeadlySerializer.model_relational_fields:
                        fk_field = model._meta.get_field(x)
                        RelatedModel = fk_field.related_model
                        if hasattr(RelatedModel, "default_nest_fields"):
                            self.nest.add(x)

            for x in self.nest:
                fk_field = model._meta.get_field(x)
                RelatedModel = fk_field.related_model
                options = RelatedModel._meta
                related_model_fields = [f.name for f in sorted(options.concrete_fields + options.many_to_many)]
                if self.nested_fields_dict:
                    for f_name , nested_fd_list in self.nested_fields_dict.items():
                        if nested_fd_list:
                            if nested_fd_list[0] == "*" and len(nested_fd_list) == 1:
                                self.nested_fields_dict[f_name] = related_model_fields
                            else:
                                self.nested_fields_dict[f_name] = list(set(nested_fd_list).intersection(set(related_model_fields)))

                if (x not in self.nested_fields_dict):
                    if hasattr(RelatedModel, "default_nest_fields"):
                        self.nested_fields_dict[x] = field_processor(RelatedModel.default_nest_fields, model)
                    else:
                        self.nested_fields_dict[x] = "none"

                if self.nested_fields_dict[x] == "none":
                    self.nested_fields_dict[x] = []

                if "id" not in self.nested_fields_dict[x]:
                    self.nested_fields_dict[x].append("id")

                if fk_field.one_to_many:

                    reverse_name = fk_field.field.name + "_id"
                    query_dict = {}
                    query_dict[reverse_name+"__in"] = model_id_list

                    if reverse_name not in self.nested_fields_dict[x]:
                        self.nested_fields_dict[x].append(reverse_name)

                    rel_queryset = RelatedModel.objects.filter(**query_dict).values(*(self.nested_fields_dict[x]))
                    rel_queryset = self.postprocess_values_list(rel_queryset, self.nested_fields_dict[x], RelatedModel)
                    rel_map = {}
                    for rq in rel_queryset:
                        if rq[reverse_name] not in rel_map:
                            rel_map[rq[reverse_name]] = []
                        rel_map[rq[reverse_name]].append(rq)
                    for t in result:
                        if t["id"] in rel_map:
                            t[x] = rel_map[t["id"]]
                        else:
                            t[x] = []

                elif fk_field.many_to_one:

                    reverse_name = fk_field.related_query_name()
                    query_dict = {}
                    query_dict[reverse_name+"__in"] = model_id_list
                    rel_queryset = RelatedModel.objects.filter(**query_dict).values(*(self.nested_fields_dict[x]))
                    rel_queryset = self.postprocess_values_list(rel_queryset, self.nested_fields_dict[x], RelatedModel)
                    rel_map = {}

                    for rq in rel_queryset:
                        rel_map[rq["id"]] = rq

                    for t in result:

                        if t[x] in rel_map:
                            t[x] = rel_map[t[x]]
                        else:
                            t[x] = None

                elif fk_field.one_to_one:
                    try:
                        reverse_name = fk_field.related_query_name()
                        query_dict = {}
                        query_dict[reverse_name+"__in"] = model_id_list
                    except:
                        reverse_name = fk_field.field.name
                        query_dict = {}
                        query_dict[reverse_name+"_id__in"] = model_id_list

                    rel_queryset = RelatedModel.objects.filter(**query_dict).values(*(self.nested_fields_dict[x]))
                    rel_queryset = self.postprocess_values_list(rel_queryset, self.nested_fields_dict[x], RelatedModel)
                    rel_map = {}

                    for rq in rel_queryset:
                        rel_map[rq["id"]] = rq

                    for t in result:

                        if t[x] in rel_map:
                            t[x] = rel_map[t[x]]
                        else:
                            t[x] = None      

                elif fk_field.many_to_many:

                    try:  # m2m forward
                        reverse_name = fk_field.related_query_name()
                    except:  # m2m reverse
                        reverse_name = fk_field.field.name

                    query_dict = {}
                    query_dict[reverse_name+"__in"] = model_id_list
                    rel_queryset = RelatedModel.objects.filter(**query_dict).values(*(self.nested_fields_dict[x]))
                    rel_queryset = self.postprocess_values_list(rel_queryset, self.nested_fields_dict[x], RelatedModel)
                    rel_map = {}

                    for rq in rel_queryset:
                        rel_map[rq["id"]] = rq

                    for t in result:
                        final = []
                        if t[x]:
                            temp = set(t[x])
                            for q in temp:
                                final.append(rel_map[q])
                            t[x] = final

            # self.data = result
            if not many:
                result = result[0]

            self.data = result

    return ModelDeadlySerializer
