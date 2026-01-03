from ...extensions import ma, db
from ...models import Customer


class CustomerSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Customer
        load_instance = True
        sqla_session = db.session

    id = ma.auto_field(dump_only=True)
    name = ma.auto_field(required=True)
    email = ma.auto_field(required=True)
    phone = ma.auto_field()
    # if you added a password column in the model:
    password = ma.auto_field(load_only=True)  # optional


customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)


class LoginSchema(ma.Schema):
    email = ma.String(required=True)
    password = ma.String(required=True)


login_schema = LoginSchema()
