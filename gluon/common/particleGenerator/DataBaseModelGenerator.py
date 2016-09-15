#!/usr/bin/python
from __future__ import print_function
import sys
import re
import yaml
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base


class DataBaseModelProcessor(object):

    def __init__(self):
        self.db_models = {}

    def add_model(self, model):
        self.data = model

    def get_table_class(self, table_name):
        try:
            return self.db_models[table_name]
        except ValueError as e:
            raise Exception('Unknown table name %s' % table_name)


    def build_sqla_models(self, base=None):
        """Make SQLAlchemy classes for each of the elements in the data read"""

        if not base:
            base = declarative_base()
        if not self.data:
            raise Exception('Cannot create Database Model from empty model.')

        def de_camel(s):
            s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', s)
            return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

        # Make a model class that we've never thought of before
        for table_name, table_data in self.data.iteritems():
            self.get_primary_key(table_data)

        for table_name, table_data in self.data.iteritems():
            try:
                attrs = {}
                for col_name, col_desc in table_data['attributes'].iteritems():
                    try:

                        options = {}
                        args = []

                        # Step 1: deal with object xrefs
                        if col_desc['type'] in self.data:
                            # This is a foreign key reference.  Make the column
                            # like the FK, but drop the primary from it and
                            # use the local one.
                            tgt_name = col_desc['type']
                            tgt_data = self.data[tgt_name]

                            primary_col = tgt_data['primary']
                            repl_col_desc = \
                                dict(tgt_data['attributes'][primary_col])

                            if 'primary' in repl_col_desc:
                                # The FK will be a primary, doesn't mean we are
                                del repl_col_desc['primary']

                            # May still be the local PK if we used to be,
                            # though
                            if col_desc.get('primary'):
                                repl_col_desc['primary'] = True

                            # Set the SQLA col option to make clear what's
                            # going on
                            args.append(sa.ForeignKey('%s.%s' %
                                                      (de_camel(tgt_name),
                                                       primary_col)))

                            # The col creation code will now duplicate the FK
                            # column nicely
                            col_desc = repl_col_desc

                        # Step 2: convert our special types to ones a DB likes
                        if col_desc['type'] == 'uuid':
                            # UUIDs, from a DB perspective,  are a form of
                            # string
                            repl_col_desc = dict(col_desc)
                            repl_col_desc['type'] = 'string'
                            repl_col_desc['length'] = 64
                            col_desc = repl_col_desc

                        # Step 3: with everything DB-ready, spit out the table
                        # definition
                        if col_desc.get('primary', False):
                            options['primary_key'] = True
                            # Save the information about the primary key as well
                            # in the object
                            attrs['_primary_key'] = col_name

                        required = col_desc.get('required', False)
                        options['nullable'] = not required

                        if col_desc['type'] == 'string':
                            attrs[col_name] = sa.Column(sa.String(
                                col_desc['length']), *args, **options)
                        elif col_desc['type'] == 'integer':
                            attrs[col_name] = sa.Column(sa.Integer(), *args,
                                                        **options)
                        elif col_desc['type'] == 'boolean':
                            attrs[col_name] = sa.Column(sa.Boolean(), *args,
                                                        **options)
                        elif col_desc['type'] == 'enum':
                            attrs[col_name] = sa.Column(
                                sa.Enum(*col_desc['values']), *args,
                                **options)
                        else:
                            raise Exception('Unknown column type %s' %
                                            col_desc['type'])
                    except:
                        print('During processing of attribute ', col_name,
                              file=sys.stderr)
                        raise
                if not '_primary_key' in attrs:
                    raise Exception("One and only one primary key has to "
                                    "be given to each column")
                attrs['__tablename__'] = de_camel(table_name)
                attrs['__name__'] = table_name

                self.db_models[table_name] = type(table_name, (base,), attrs)
            except:
                print('During processing of table ', table_name,
                      file=sys.stderr)
                raise

    @classmethod
    def get_primary_key(cls, table_data):
        primary = []
        for k, v in table_data['attributes'].iteritems():
            if 'primary' in v:
                primary = k
                break
        # If not specified, a UUID is used as the PK
        if not primary:
            table_data['attributes']['uuid'] = \
                {'type': 'string', 'length': 36, 'primary': True,
                 'required': True}
            primary = 'uuid'

        table_data['primary'] = primary
        return primary
