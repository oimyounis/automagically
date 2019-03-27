import re

from core.helpers import *
from core.constants import *


indexlines = sanitize_list(readfile(INDEX_F))

app = None


class App:
    def __init__(self, name):
        self.name = name
        self.models = {}

    def add_model(self, name):
        model = Model(name)
        self.models[name] = model
        return model

    def __str__(self):
        return 'App: %s\n %s' % (self.name, '')


class Model:
    def __init__(self, name):
        self.name = name
        self.fields = {}

    def add_field(self, name, attrs):
        field = ModelField(name, attrs)
        self.fields[name] = field
        return field


class ModelField:
    def __init__(self, name, attrs):
        self.name = name

        for attr in attrs:
            if attr == 'pk':
                self.pk = True
            elif attr in ('int', 'string', 'bool', 'float', 'longtext'):
                self.type = attr
                # TODO: continue parsing attrs...


def get_directive(string):
    return re.match(r'^([a-zA-Z0-9_]+)\s?:$', string)


def get_definition(string):
    return re.match(r'^([a-zA-Z0-9_]+)\s?:\s?(.+)$', string)


def get_subdefinition(string):
    return re.match(r'^(-|\+)\s?([a-zA-Z0-9_]+)\s?:$', string)


def get_model_field(string):
    return re.match(r'^([a-zA-Z0-9_]+)\s?\(\s?(.+)\)$', string)


active_directive = None


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


parsing_model = None


def handle_subdefinition(subdefinition):
    global app
    global parsing_model

    flag = subdefinition.group(1)
    name = subdefinition.group(2)

    if active_directive == 'models':
        if flag == '-':
            parsing_model = app.add_model(name)
        elif flag == '+':
            pass  # TODO: implement foreign key relation


def handle_model_field(model_field):
    global app
    global parsing_model

    if parsing_model:
        fieldname = model_field.group(1)
        attrs = tuple(map(lambda a: sanitize(a), model_field.group(2).split(',')))
        parsing_model.add_field(fieldname, attrs)


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

print()
