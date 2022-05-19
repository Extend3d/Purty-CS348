
from flask_sqlalchemy import SQLAlchemy

def init(app):
    global db_orm
    db_orm = SQLAlchemy(app)
    db_orm.create_all()

    global Location
    class Location(db_orm.Model):
        location_id = db_orm.Column('location_id', db_orm.Integer, primary_key = True)
        address = db_orm.Column(db_orm.String(400))

        def __init__(self, address):
            self.address = address
    
    global User
    class User(db_orm.Model):
        user_id = db_orm.Column('user_id', db_orm.Integer, primary_key = True)
        name = db_orm.Column(db_orm.String(40))
        email = db_orm.Column(db_orm.String(40))
        age = db_orm.Column(db_orm.Integer)

        def __init__(self, name, email, age):
            self.name = name
            self.email = email
            self.age = age
        
    global Party
    class Party(db_orm.Model):
        party_id = db_orm.Column('party_id', db_orm.Integer, primary_key = True)
        name = db_orm.Column(db_orm.String(40))
        date = db_orm.Column(db_orm.String(40))
        time = db_orm.Column(db_orm.String(40))
        description = db_orm.Column(db_orm.String(400))
        location_id = db_orm.Column(db_orm.Integer)
        invited_cnt = db_orm.Column(db_orm.Integer)
        coming_cnt = db_orm.Column(db_orm.Integer)
        likes_cnt = db_orm.Column(db_orm.Integer)

        def __init__(self, name, date, time, description, location_id, invited_cnt, coming_cnt, likes_cnt):
            self.name = name
            self.date = date
            self.time = time
            self.description = description
            self.location_id = location_id
            self.invited_cnt = invited_cnt
            self.coming_cnt = coming_cnt
            self.likes_cnt = likes_cnt


