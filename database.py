import mongoengine
import data_model
import json
import pandas

# Connect to DB, defaults work here.
mongoengine.register_connection(
    alias="core", name="extract_requests", host="0.0.0.0", port=27017,
)


def add_product(product_name):
    p = data_model.Product()
    p.name = product_name.lower()
    p.save()
    return p


def valid_product(product_name):
    """Verify that passed product name corresponds to actual IPUMS product.

    Args:
        product_name (str): short name of an IPUMS product

    Returns:
        data_model.Product: Product Document object
    """
    try:
        p = data_model.Product.objects().get(name=product_name.lower())
    except mongoengine.DoesNotExist:
        # XXX We won't worry about bogus product names getting in right now.
        p = add_product(product_name)
    return p


def add_sample(sample_name, product_name):
    p = valid_product(product_name)
    s = data_model.Sample()
    s.name = sample_name.lower()
    s.product = p.to_dbref()
    s.save()
    return s


def valid_sample(sample_name, product_name):
    try:
        s = data_model.Sample.objects().get(name=sample_name.lower())
    except mongoengine.DoesNotExist:
        s = add_sample(sample_name, product_name)
    return s


def add_variable(variable_name, product_name):
    p = valid_product(product_name)
    v = data_model.Variable()
    v.name = variable_name.lower()
    v.product = p.to_dbref()
    v.save()
    return v


def valid_variable(variable_name, product_name):
    try:
        v = data_model.Variable.objects().get(name=variable_name.lower())
    except mongoengine.DoesNotExist:
        v = add_variable(variable_name, product_name)
    return v


def add_datatable(datatable_name, product_name):
    p = valid_product(product_name)
    dt = data_model.DataTable()
    dt.name = datatable_name.lower()
    dt.product = p.to_dbref()
    dt.save()
    return dt


def valid_datatable(datatable_name, product_name):
    try:
        dt = data_model.DataTable.objects().get(name=datatable_name.lower())
    except mongoengine.DoesNotExist:
        dt = add_datatable(datatable_name, product_name)
    return dt


def add_user(user_name, product_name):
    p = valid_product(product_name)
    u = data_model.User()
    u.name = user_name.lower()
    u.products.append(p.to_dbref())
    u.save()
    return u


def valid_user(user_name, product_name):
    try:
        u = data_model.User.objects().get(name=user_name.lower())
    except mongoengine.DoesNotExist:
        u = add_user(user_name, product_name)
    # TODO check if user exists for given product. if not add.
    return u


def add_variable_sample_references(sample_name, variable_name, product_name):
    s = valid_sample(sample_name, product_name)
    v = valid_variable(variable_name, product_name)
    # XXX Right now Sample.variables is a list of strings so the validated
    # variable name is all that we can store.
    s.variables.append(v.name)
    s.save()
    v.samples.append(s.to_dbref())
    v.save()


def load_usa_sample_variables():
    # TODO Right now, if you run this after the database has already been created
    # the lists within the documents end up full of duplicates...
    sv = pandas.read_csv("sample_variables.csv")
    sv.apply(
        lambda x: add_variable_sample_references(
            x.sample_name, x.variable_mnemonic, "usa"
        ),
        axis=1,
    )


def n_extracts_by_sample_variables():
    # Get collection of extract ids, and for each sample in the variable
    # see how many share extract ids
    report = {}
    for v in data_model.Variable.objects():
        extracts = set(v.extracts)
        for s in v.samples:
            report[f"{s.name}, {v.name}"] = len(extracts ^ set(s.extracts))
    return report


def n_extracts_by_collection(Collection):
    # Probably should first verify that the document has extracts...
    result = {d.name: len(d.extracts) for d in Collection.objects()}
    return result


def extract_report():
    report = {}
    collections = [
        data_model.DataTable,
        data_model.Sample,
        data_model.Variable,
        data_model.User,
    ]
    for c in collections:
        report[c._meta["collection"]] = n_extracts_by_collection(c)
    report["sample_variables"] = n_extracts_by_sample_variables()
    return json.dumps(report)


class ExtractRequestMessage:
    # XXX: Could probably make this a base class and then create
    # NhgisExtractRequestMessage and UsaExtractRequestMessage child classes...
    def __init__(self, message):
        self.message = json.loads(message)
        self.load_info(self.message)

    def load_info(self, message_dict):
        self.product = message_dict["product"]
        self.user = message_dict["user"]
        if self.product == "nhgis":
            self.load_nhgis_extract(message_dict)
        elif self.product == "usa":
            self.load_usa_extract(message_dict)
        else:
            raise NotImplementedError(f"{self.product} is not a support product.")

    def load_nhgis_extract(self, message_dict):
        self.data_tables = message_dict["data_tables"]

    def load_usa_extract(self, message_dict):
        self.samples = message_dict["samples"]
        self.variables = message_dict["variables"]

    def save(self):
        # XXX These two save methods have a lot in commong.
        # Adding all of the add_* and valid_* methods to this
        # class will remove a lot of redundant querying and remove
        # some repetition in this code.
        if self.product == "nhgis":
            self.save_nhgis()
        elif self.product == "usa":
            self.save_usa()
        else:
            raise NotImplementedError(f"{self.product} is not a support product.")

    def save_nhgis(self):
        # Is nhgis in our Product collection? if not, add it
        p = valid_product(self.product)

        # is the user in our User collection? if not, add them
        u = valid_user(self.user, self.product)

        # are the DataTables in our collection? if not, add it
        dts = []
        for dt in self.data_tables:
            dt = valid_datatable(dt, self.product)
            dts.append(dt)

        er = data_model.ExtractRequest()
        er.user_id = u.id
        er.product = p.to_dbref()
        er.datatables = [dt.to_dbref() for dt in dts]
        er.save()
        u.extracts.append(er.to_dbref())
        u.save()
        for dt in dts:
            dt.extracts.append(er.id)
            dt.save()

    def save_usa(self):
        # Is usa in our Product collection? if not, add it
        p = valid_product(self.product)

        # is the user in our User collection? if not, add them
        u = valid_user(self.user, self.product)

        er = data_model.ExtractRequest()
        er.user_id = u.id
        er.product = p.to_dbref()
        # are the Samples and Variables in our collections? if not, add it
        samples = []
        variables = []
        for s in self.samples:
            s = valid_sample(s, self.product)
            samples.append(s)
        for v in self.variables:
            v = valid_variable(v, self.product)
            variables.append(v)
        er.samples = [s.to_dbref() for s in samples]
        er.variables = [v.to_dbref() for v in variables]
        er.save()
        u.extracts.append(er.to_dbref())
        u.save()
        # Drop the ExtractRequest id onto the Sample and Variable
        # Documents for easy querying. I'm still not sure if
        # I like this model, but it definitely achieves the
        # defined report easily.
        # Have to do this after ExtractRequest Document has been saved
        # so that it actually has an ID.
        for s in samples:
            s.extracts.append(er.id)
            s.save()
        for v in variables:
            v.extracts.append(er.id)
            v.save()
