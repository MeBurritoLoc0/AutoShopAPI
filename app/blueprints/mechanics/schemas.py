from ...extensions import ma
from ...models import Mechanic

class MechanicSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Mechanic
        load_instance = True
        include_fk = True
        include_relationships = False

mechanic_schema = MechanicSchema()
mechanics_schema = MechanicSchema(many=True)
