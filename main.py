from core.helpers import *
from core.constants import *


indexlines = sanitize_list(readfile(INDEX_F))

app = None
active_directive = None
parsing_model = None


class App:
    def __init__(self, name):
        self.name = name
        self.models = {}

    def add_model(self, name):
        model = Model(name)
        self.models[name] = model
        return model

    def reverse_models(self):
        lines = []
        if self.models:
            lines.append('from django.db import models\n\n')
            for name, model in app.models.items():
                lines.append(str(model))

        return '\n'.join(lines)

    def __str__(self):
        return 'App: %s' % self.name


class Model:
    def __init__(self, name):
        self.name = name
        self.fields = {}

    def add_field(self, name, attrs, fk=False):
        field = ModelField(name, attrs, fk)
        self.fields[name] = field
        return field

    def __str__(self):
        output = ['class %s(models.Model):' % self.name]
        for name, field in self.fields.items():
            output.append('    %s' % str(field))

        output += ['', '']

        return '\n'.join(output)


class Relation:
    O2O = 'o2o'
    O2M = 'o2m'
    M2M = 'm2m'
    CASCADE = 'cascade'
    SET_NULL = 'set_null'
    DO_NOTHING = 'do_nothing'
    SET_DEFAULT = 'set_default'

    ACTIONS = (CASCADE, SET_NULL, DO_NOTHING, SET_DEFAULT)

    def __init__(self, model, type=O2M):
        self.model = model
        self.on_delete = None
        self.on_update = None
        self.type = type

    def get_on_delete_text(self):
        if not self.on_delete:
            return ''

        return 'models.%s' % self.on_delete.upper()

    def get_on_update_text(self):
        if not self.on_update:
            return ''

        return 'models.%s' % self.on_update.upper()


class ModelField:
    def __init__(self, name, attrs, fk=False):
        self.name = name
        self.type = None
        self.pk = False
        self.fk = fk
        self.relation = None
        self.null = False
        self.blank = False

        if self.fk:
            self.relation = Relation(name)

        self.parse_attributes(attrs)

    def parse_attributes(self, attrs):
        for attr in attrs:
            if attr == 'pk' and not self.fk:
                self.pk = True
            elif attr in ('int', 'string', 'bool', 'float', 'longtext', 'date', 'time', 'datetime') and not self.fk:
                self.type = attr
                if attr == 'string':
                    self.max_length = 255
            elif attr == 'null':
                self.null = True
            elif attr == 'blank':
                self.blank = True
            elif attr in (Relation.O2O, Relation.O2M, Relation.M2M):
                self.relation.type = attr
            elif ':' in attr:
                parts = attr.split(':')
                attribute = parts[0].strip()
                val = parts[1].strip()

                if attribute == 'default':
                    self.default = val
                elif attribute == 'max':
                    if self.type == 'int':
                        self.max_length = int(val)
                    elif self.type == 'float':
                        self.max_length = float(val)
                    elif self.type in ('string', 'longtext'):
                        self.max_length = val
                elif self.fk and attribute == 'on_delete':
                    if val not in Relation.ACTIONS:
                        raise Exception("Unknown value provided to the %s option: %s" % (attribute, val))
                    self.relation.on_delete = val
                elif self.fk and attribute == 'on_update':
                    if val not in Relation.ACTIONS:
                        raise Exception("Unknown value provided to the %s option: %s" % (attribute, val))
                    self.relation.on_update = val

            else:
                raise Exception("Unknown attribute passed: %s" % attr)

    def get_field_type_text(self):
        _type = ''
        if self.type == 'int':
            _type = 'Integer'
        elif self.type == 'string':
            _type = 'Char'
        elif self.type == 'bool':
            _type = 'Boolean'
        elif self.type == 'float':
            _type = 'Float'
        elif self.type == 'longtext':
            _type = 'Text'
        elif self.type == 'date':
            _type = 'Date'
        elif self.type == 'time':
            _type = 'Time'
        elif self.type == 'datetime':
            _type = 'DateTime'
        elif self.fk:
            if self.relation:
                if self.relation.type == Relation.O2M:
                    return 'ForeignKey'
                elif self.relation.type == Relation.O2O:
                    _type = 'OneToOne'
                elif self.relation.type == Relation.M2M:
                    _type = 'ManyToMany'
            else:
                raise Exception('No relation defined on field %s' % self.name)

        return '%sField' % _type

    def get_attrs_text(self):
        attrs_text = []

        if self.fk and self.relation:
            attrs_text.append("'%s'" % self.relation.model)
            if self.relation.on_delete:
                attrs_text.append('on_delete=%s' % self.relation.get_on_delete_text())
            if self.relation.on_update:
                attrs_text.append('on_update=%s' % self.relation.get_on_update_text())
        if self.pk:
            attrs_text.append('primary_key=True')
        if hasattr(self, 'max_length'):
            attrs_text.append('max_length=%s' % self.max_length)
        if self.null:
            attrs_text.append('null=True')
        if self.blank:
            attrs_text.append('blank=True')
        if hasattr(self, 'default'):
            attrs_text.append('default=%s' % self.default)

        return ', '.join(attrs_text)

    def __str__(self):
        return '{name} = models.{field_type}({attrs})'.format(
            name=self.name,
            field_type=self.get_field_type_text(),
            attrs=self.get_attrs_text()
        )


def get_directive(string):
    return re.match(r'^([a-zA-Z0-9_]+)\s?:$', string)


def get_definition(string):
    return re.match(r'^([a-zA-Z0-9_]+)\s?:\s?(.+)$', string)


def get_subdefinition(string):
    return re.match(r'^(-|\+)\s?([a-zA-Z0-9_]+)\s?:$', string)


def get_model_field(string):
    return re.match(r'^(\+)?\s?([a-zA-Z0-9_]+)\s?\(\s?(.+)\)$', string)


def parse(lines):
    for line in lines:
        parse_line(line)


def handle_directive(directive):
    global active_directive

    directive = directive.group(1)
    active_directive = directive


def handle_definition(definition):
    global app

    defname = definition.group(1)
    value = definition.group(2)

    if active_directive == 'app':
        if defname == 'name':
            app = App(value)


def handle_subdefinition(subdefinition):
    global app
    global parsing_model

    flag = subdefinition.group(1)
    name = subdefinition.group(2)

    if active_directive == 'models':
        if flag == '-':
            parsing_model = app.add_model(name)
        elif flag == '+':
            pass  # TODO: implement defining foreign key relation


def handle_model_field(model_field):
    global app
    global parsing_model

    if parsing_model:
        fk = False

        if model_field.group(1) == '+':
            fk = True

        fieldname = model_field.group(2)
        attrs = tuple(map(lambda a: sanitize(a), model_field.group(3).split(',')))
        parsing_model.add_field(fieldname, attrs, fk)


def parse_line(line):
    directive = get_directive(line)

    if directive:
        handle_directive(directive)
    else:
        definition = get_definition(line)

        if definition:
            handle_definition(definition)
        else:
            subdefinition = get_subdefinition(line)

            if subdefinition:
                handle_subdefinition(subdefinition)
            else:
                model_field = get_model_field(line)

                if model_field:
                    handle_model_field(model_field)


parse(indexlines)
models = app.reverse_models()

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), 'output')

if not os.path.exists(OUTPUT_PATH):
    os.makedirs(OUTPUT_PATH)

with open(os.path.join(OUTPUT_PATH, MODELS_OUTPUT), 'w+t') as handle:
    handle.write(models)

print()
