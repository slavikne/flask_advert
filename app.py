import atexit
import os
from flask import Flask, jsonify, request
from flask.views import MethodView
from sqlalchemy import create_engine, Column, Integer, String, DateTime, func, ForeignKey, select
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql.functions import user



app = Flask("app")
engine = create_engine('postgresql://user_flask:123456@127.0.0.1:5432/flask_advert')
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()
atexit.register(lambda: engine.dispose())


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    registration_time = Column(DateTime, server_default=func.now())

class Advert(Base):
    __tablename__ = 'adverts'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    create_time = Column(DateTime, server_default=func.now())
    user_id = Column(Integer, ForeignKey('users.id'))
    author = relationship("User")

Base.metadata.create_all(engine)


class UserView(MethodView):

    def get(self, user_id: int):
        with Session() as session:
            query_user = session.query(User.id, User.email, User.name).filter(User.id == user_id).first()
            return jsonify({
                'íd': query_user.id,
                'email': query_user.email,
                'name': query_user.name
            })

    def post(self):
        json_data = request.json
        with Session() as session:
            user = User(name=json_data['name'], email=json_data['email'], password=json_data['password'])
            session.add(user)
            session.commit()
            return jsonify({
                'íd': user.id,
                'registration_time': user.registration_time.isoformat()
            })


class AdvertView(MethodView):

    def get(self, advert_id: int):
        with Session() as session:
            query_advert=session.query(Advert.id, Advert.title, Advert.description).filter(Advert.id == advert_id).first()
            return jsonify({
                'íd': query_advert.id,
                'title': query_advert.title,
                'description': query_advert.description
            })


    def post(self):
        json_data = request.json
        with Session() as session:
            advert = Advert(title=json_data['title'], description=json_data['description'], user_id=json_data['user_id'])
            session.add(advert)
            session.commit()
            return jsonify({
                'íd': advert.id,
                'title': advert.title,
                'description': advert.description,
                'create_time': advert.create_time.isoformat(),
                'user_id': advert.user_id
            })

    def delete(self, advert_id: int):
        with Session() as session:
            query_advert = session.query(Advert).filter(Advert.id == advert_id).first()
            session.delete(query_advert)
            session.commit()
            return jsonify({
                'status': '200 OK'
            })

    def patch(self, advert_id: int):
        json_data = request.json
        with Session() as session:
            edit_advert = session.query(Advert).filter(Advert.id == advert_id).\
                update({Advert.title:json_data['title']}, synchronize_session = 'fetch')
            session.commit()
            return jsonify({
                'status': '200 OK'
            })


app.add_url_rule('/users/', view_func=UserView.as_view('create_user'), methods=['POST'])
app.add_url_rule("/user/<int:user_id>/", view_func=UserView.as_view("get_user"), methods=["GET"])
app.add_url_rule('/adverts/', view_func=AdvertView.as_view('create_advert'), methods=['POST'])
app.add_url_rule("/advert/<int:advert_id>/", view_func=AdvertView.as_view("get_del_patch_advert"), methods=["GET", "DELETE", "PATCH"])

app.run(
    host='0.0.0.0',
    port=5000
)
