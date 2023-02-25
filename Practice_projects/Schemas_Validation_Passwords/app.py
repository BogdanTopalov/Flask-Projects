import enum

from decouple import config
from flask import Flask, request
from flask_migrate import Migrate
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from marshmallow import Schema, fields, validate, ValidationError, validates

app = Flask(__name__)

db_user = config('DB_USER')
db_password = config('DB_PASS')
db_name = config('DB_NAME')
db_port = config('DB_PORT')

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{db_user}:{db_password}' \
                                        f'@localhost:{db_port}/{db_name}'

db = SQLAlchemy(app)
api = Api(app)

migrate = Migrate(app, db)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(
        db.String(120),
        nullable=False,
        unique=True
    )
    password = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.Text)

    # Use func.now()(=utc.now()) when saving datetime in db.
    create_on = db.Column(db.DateTime, server_default=func.now())
    updated_on = db.Column(db.DateTime, onupdate=func.now())


class ColorEnum(enum.Enum):
    pink = "pink"
    black = "black"
    white = "white"
    yellow = "yellow"


class SizeEnum(enum.Enum):
    xs = "xs"
    s = "s"
    m = "m"
    l = "l"
    xl = "xl"
    xxl = "xxl"


class Clothes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    color = db.Column(
        db.Enum(ColorEnum),
        default=ColorEnum.white,
        nullable=False
    )
    size = db.Column(
        db.Enum(SizeEnum),
        default=SizeEnum.s,
        nullable=False
    )
    photo = db.Column(db.String(255), nullable=False)
    create_on = db.Column(db.DateTime, server_default=func.now())
    updated_on = db.Column(db.DateTime, onupdate=func.now())


# Custom validation function
def validate_name(name):
    try:
        first_name, last_name = name.split()
    except ValueError:
        raise ValidationError('At least two names separated with space are required')


class BaseUserSchema(Schema):
    email = fields.Email(required=True)
    full_name = fields.String(
        required=True,
        # validate=validate.And(validate.Length(min=3, max=255), validate_name)
    )

    # Custom validation method. validate= should not be used above.
    @validates('full_name')
    def validate_name(self, name):
        if not (255 >= len(name) >= 3):
            raise ValidationError('Name length must be between 3 and 255 characters')
        try:
            first_name, last_name = name.split()
        except ValueError:
            raise ValidationError('At least two names separated with space are required')


class UserSignInSchema(BaseUserSchema):
    password = fields.String()


class SignUp(Resource):
    def post(self):
        data = request.get_json()
        schema = UserSignInSchema()
        errors = schema.validate(data)

        if not errors:
            user = User(**data)
            db.session.add(user)
            db.session.commit()
            return 201, data
        return errors


api.add_resource(SignUp, '/sign_up')


if __name__ == "__main__":
    app.run(debug=True)
