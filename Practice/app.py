from decouple import config
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api
from flask_migrate import Migrate


app = Flask(__name__)
app.config[
    'SQLALCHEMY_DATABASE_URI'
] = f'postgresql://{config("DB_USER")}:{config("DB_PASS")}' \
    f'@localhost:{config("DB_PORT")}/{config("DB_NAME")}'

api = Api(app)

db = SQLAlchemy(app)

migrate = Migrate(app, db)


class BookModel(db.Model):
    __tablename__ = 'books'
    pk = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    author = db.Column(db.String, nullable=False)
    reader_pk = db.Column(db.Integer, db.ForeignKey('readers.pk'))
    reader = db.relationship('ReaderModel')

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class ReaderModel(db.Model):
    __tablename__ = 'readers'
    pk = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    books = db.relationship('BookModel', backref='book', lazy='dynamic')


class BookResource(Resource):
    def post(self):
        data = request.get_json()
        reader_pk = data.pop('reader_pk')
        new_book = BookModel(**data)
        new_book.reader_pk = reader_pk
        db.session.add(new_book)
        db.session.commit()
        return new_book.as_dict()


class ReaderResource(Resource):
    def get(self, reader_pk):
        reader = ReaderModel.query.filter_by(pk=reader_pk).first()
        books = BookModel.query.filter_by(reader_pk=reader_pk)
        return {"data": [book.as_dict() for book in reader.books]}


api.add_resource(BookResource, "/books/")
api.add_resource(ReaderResource, "/readers/<int:reader_pk>/books")


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
