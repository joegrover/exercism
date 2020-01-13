import mongoengine
import data_model
import json

# Connect to DB, defaults work here.
mongoengine.register_connection(alias="core", name="extract_requests")


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
    p = data_model.Product.objects(name=product_name.lower()).first()
    if p is None:
        # XXX We won't worry about bogus product names getting in right now.
        p = add_product(product_name)
    return p


def add_user(user_name, product_name):
    p = valid_product(product_name)
    u = data_model.User()
    u.name = user_name.lower()
    u.products.append(p.to_dbref())
    u.save()
    return u


def add_sample(sample_name, product_name):
    p = valid_product(product_name)
    s = data_model.Sample()
    s.name = sample_name.lower()
    s.product = p.to_dbref()


def load_usa_sample_variables():
    pass


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
        if self.product == "nhgis":
            self.save_nhgis()
        elif self.product == "usa":
            self.save_usa()
        else:
            raise NotImplementedError(f"{self.product} is not a support product.")

    def save_nhgis(self):
        # Is nhgis in our Product collection?
        add_product(self.product.lower())
        # if not, add it

        # is the user in our User collection?
        add_user(self.user, self.product)
        # if not add them

        # is the DataTable in our collect?

        # if not, add it

        # finally declare and save ExtractRequest
        pass
