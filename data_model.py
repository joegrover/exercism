import datetime
import mongoengine


class Product(mongoengine.Document):
    name = mongoengine.StringField(required=True, primary_key=True)
    meta = {
        "db_alias": "core",
    }


class User(mongoengine.Document):
    date_added = mongoengine.DateTimeField(default=datetime.datetime.now)
    name = mongoengine.StringField(required=True)
    products = mongoengine.ListField(mongoengine.ReferenceField(Product))
    meta = {
        "db_alias": "core",
    }


class Sample(mongoengine.Document):
    # A sample should belong to only one product, if the product is deleted, delete
    # the sample as well
    product = mongoengine.ReferenceField(
        Product, reverse_delete_rule=mongoengine.CASCADE
    )
    name = mongoengine.StringField(required=True, primary_key=True)
    # TODO: Kinda stuck here... I would like Sample objects to have a list
    # of references to variables and vice versa, but I need to have
    # the Variable class defined in order to reference it...
    # going with a generic reference for now, which means I can't
    # implement a `reverse_delete_rule`
    variables = mongoengine.ListField(mongoengine.GenericReferenceField())
    meta = {
        "db_alias": "core",
    }


class Variable(mongoengine.Document):
    # A variable should belong to only one product, if the product is deleted, delete
    # the variable as well.
    product = mongoengine.ReferenceField(
        Product, reverse_delete_rule=mongoengine.CASCADE
    )
    # Right now "name" could be a primary key, but if we have multiple products in this
    # database then Variable names might collide.
    name = mongoengine.StringField(required=True)
    # Variables can belong to many samples, if a sample is deleted remove that sample
    # from the variable's list of samples.
    samples = mongoengine.ListField(
        mongoengine.ReferenceField(Sample, reverse_delete_rule=mongoengine.PULL)
    )
    meta = {
        "db_alias": "core",
    }


class DataTable(mongoengine.Document):
    # XXX: It is kinda funny... the NHGIS DataTable model is sort of the document
    # corollary to the USA Samples (table), Variables (table) join situation...
    # I guess the main difference being that even if tables have the same
    # name across Datasets, they don't necessarily share all the other attributes
    # (possible values, labels, etc.) like a microdata variable. Anyway, maybe
    # think about a more generic DataTable model constructed from Sample.Variable
    # combos.
    # A datatable should belong to only one product, if the product is deleted, delete
    # the data table as well
    product = mongoengine.ReferenceField(
        Product, reverse_delete_rule=mongoengine.CASCADE
    )
    name = mongoengine.StringField(required=True, primary_key=True)
    meta = {
        "db_alias": "core",
    }


class ExtractRequest(mongoengine.Document):
    # If a user or product associated with this extract is deleted, also
    # delete the extract request document.
    user = mongoengine.ReferenceField(User, reverse_delete_rule=mongoengine.CASCADE)
    product = mongoengine.ReferenceField(
        Product, reverse_delete_rule=mongoengine.CASCADE
    )
    samples = mongoengine.ListField(
        mongoengine.ReferenceField(Sample, reverse_delete_rule=mongoengine.PULL)
    )
    variables = mongoengine.ListField(
        mongoengine.ReferenceField(Variable, reverse_delete_rule=mongoengine.PULL)
    )
    submitted_at = mongoengine.DateTimeField(default=datetime.datetime.now)
    meta = {
        "db_alias": "core",
    }
