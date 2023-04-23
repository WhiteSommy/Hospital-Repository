from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_login import LoginManager


login = LoginManager()
db = SQLAlchemy()



class User(UserMixin, db.Model):
    '''
    The User Model
    Defines all the users in the systems
        -> admins
        -> doctors
        -> patients
    '''
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(100))
    lastname = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    phonenumber = db.Column(db.String(100))
    gender = db.Column(db.String(50))
    password = db.Column(db.String(1000))
    status = db.Column(db.String(50)) # this is the fields that is used to differentiate between the different type of users

    def __init__(self, firstname, lastname, email, password, phonenumber, gender, status):
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.phonenumber = phonenumber
        self.gender = gender
        self.password = password
        self.status = status

    def add_user(self):
        '''
        Adds a user to the db
        '''
        db.session.add(self)
        db.session.commit()

    def update_user(self):
        '''
        updates a user row
        '''
        db.session.commit()

    def delete(self):
        '''
        removes a user from the database
        '''
        db.session.delete(self)
        db.session.commit()


@login.user_loader
def load_user(id):
    '''
    A callback to load the user data each session
    '''
    return User.query.get(int(id))


class Appointment(db.Model):
    '''
    The Appointment model
    Defines the appointment between the doctors and patients
    '''
    __tablename__ = "appointment"

    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(100))
    lastname = db.Column(db.String(100))
    gender = db.Column(db.String(50))
    date = db.Column(db.String(50))
    time = db.Column(db.String(50))
    phone_number = db.Column(db.String(20))
    doctor_id = db.Column(db.Integer())
    patient_id = db.Column(db.Integer())
    condition = db.Column(db.String(50))

    def __init__(self, firstname, lastname, gender, date, time, phone_number, doctor_id, patient_id, condition):

        self.firstname = firstname
        self.lastname = lastname
        self.gender = gender
        self.date = date
        self.time = time
        self.phone_number = phone_number
        self.doctor_id = doctor_id
        self.patient_id = patient_id
        self.condition = condition

    def add_appointment(self):
        '''
        add appointment to the db
        '''
        db.session.add(self)
        db.session.commit()

    def delete(self):
        '''
        remove appointment from the db
        '''
        db.session.delete(self)
        db.session.commit()


class Prescription(db.Model):
    '''
    The Prescription model
    Defines the prescription given to patients by doctors
    '''
    __tablename__ = 'prescription'
    id = db.Column(db.Integer, primary_key=True)
    drug = db.Column(db.String(100))
    quantity = db.Column(db.String(100))
    condition = db.Column(db.String(100))
    patient_id = db.Column(db.Integer())
    doctor_id = db.Column(db.Integer())

    def __init__(self, drug, quantity, condition, patient_id, doctor_id) -> None:
        self.drug = drug
        self.quantity = quantity
        self.condition = condition
        self.patient_id = patient_id
        self.doctor_id = doctor_id

    def add_prescription(self):
        '''
        Add prescription to the db
        '''
        db.session.add(self)
        db.session.commit()
