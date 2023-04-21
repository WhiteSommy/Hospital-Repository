import logging
import os
from flask import Flask, flash, redirect, render_template, request, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_required, current_user, login_user, logout_user

from models import db, User, Appointment, Prescription, login

'''
Initialization of the flask application
'''
application = app = Flask(__name__)
app.secret_key = "secret"


'''
Setting up the database config 
'''
database_name = os.environ['RDS_DB_NAME']
database_username = os.environ['RDS_USERNAME']
database_password = os.environ['RDS_PASSWORD']


app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql+pymysql://{}:{}@{}/{}'.format(
    database_username, database_password, f"{os.environ['RDS_HOSTNAME']}:{os.environ['RDS_PORT']}", database_name)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

'''
initialize the data base connection
and the login service
'''
db.init_app(app)
login.init_app(app)
login.login_view = 'login'


'''
Create the database tables as defined in models.py
'''
@app.before_first_request
def create_all():
    db.create_all()



# =================================================#
# ============== UNIVERSAL ROUTE ==================#

@app.route('/')
@app.route('/index')
@login_required
def index():
    '''
    Home page view
    '''
    return render_template("index.html")


@app.route('/forgetpassword', methods=['GET', 'POST'])
def forget_password():
    '''
    Forgot password view
    '''
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm-password')

        if password != confirm_password:
            # ensure password and forgot password are the same
            flash('Password MisMatch')
            return redirect('fp.html')

        try:
            user = User.query.filter_by(email=email).first() # fetch user from db
            user.password = generate_password_hash(
                password,  method='sha256', salt_length=10)
            user.update_user() # update the user with new password
            flash('Password Updated Successfully')
            return redirect(url_for('login'))

        except Exception as e:
            db.session.rollback()
            logging.exception(e)
        finally:
            db.session.close()

    return render_template('fp.html')


# ================================================= #
# =============== ADMIN ROUTES ==================== #

@app.route('/admin', methods=['GET', 'POST'])
def admin_signup():
    '''
    The admin signup view
    '''
    if request.method == 'POST':
        # Read the posted values from the UI

        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        email = request.form.get('email')
        gender = request.form.get('gender')
        phonenumber = request.form.get('phonenumber')
        status = 'admin'
        user_password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Validate the received values
        if not all([firstname, lastname, email, user_password, phonenumber, status, confirm_password]):
            flash("Enter all required fields")
            return redirect(url_for('admin_signup'))

        if user_password != confirm_password:
            flash('Password Mismatch')
            return redirect(url_for('admin_signup'))

        # if this returns a user, then the email already exists in database
        user = User.query.filter_by(email=email).first()

        if user:
            flash("User already exist")
            return redirect(url_for('admin_signup'))

        # Hash user password
        try:

            password = generate_password_hash(
                user_password, method='sha256', salt_length=10)
            new_user = User(firstname=firstname, lastname=lastname, email=email,
                            gender=gender, phonenumber=phonenumber, password=password, status=status)
            print(new_user)
            new_user.add_user() # add user to db
            print(new_user)
            flash("Account Created Successfuly")
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            logging.exception(e)
        finally:
            db.session.close()

    return render_template("admin-signup.html")


@app.route('/admin/dashboard')
@login_required
def admindashboard():
    '''
    Admin dashboard view
    gives an overview of the number of doctors, patients and
    appointments
    '''
    if request.method == 'GET':
        if current_user.status != 'admin':
            return render_template('403.html')
        count_map = {}
        try:
            # gets the current count of doctors, patients amd appointment
            count_map['doctors'] = User.query.filter_by(status='doctor').count()
            count_map['patients'] = User.query.filter_by(status='patient').count()
            count_map['appointments'] = Appointment.query.count()
        except Exception as e:
            print("Error : ", str(e))
    return render_template("adminDashboard.html", count_map=count_map)


@app.route('/admin/doctors', methods=['GET', 'POST'])
@login_required
def doctors():
    '''
    The admin -> Doctor view
    '''

    if current_user.status != 'admin':
        return render_template('403.html')

    doctors = User.query.filter_by(status='doctor').all() # fetch all the doctors

    if request.method == 'POST':
        # this is an admin action to delete a doctor
        _id = int(request.form.get('id'))
        try:
            # deletes from the db and removes from the list of 
            # previously queried doctors
            User.query.get(_id).delete()
            doctors = list(filter(lambda x : x.id != _id, 
                                  doctors))
        except Exception as e:
            print("Error", str(e))
            pass
    return render_template("doctors.html", doctors=doctors, length=len(doctors))


@app.route('/admin/patients', methods=['GET', 'POST'])
@login_required
def patients():
    '''
    The admin -> Patient view
    '''
    if current_user.status != 'admin':
        return render_template('403.html')
    patients = User.query.filter_by(status='patient').all() # fetch all the patients

    if request.method == 'POST':
        # this is an admin action to delete a patient
        _id = int(request.form.get('id'))
        try:
            # deletes from the db and removes from the list of 
            # previously queried patients
            User.query.get(_id).delete()
            patients = list(filter(lambda x : x.id != _id, 
                                  patients))
        except Exception as e:
            print("Error", str(e))
            pass
    return render_template("patients.html", patients=patients, length=len(patients))


@app.route('/admin/appointments', methods=['GET', 'POST'])
@login_required
def allAppointments():
    '''
    The admin -> Appointment view
    '''
    if current_user.status != 'admin':
        return render_template('403.html')
    
    appointments = Appointment.query.all()   # fetch all the appointments

    if request.method == 'POST':
        # this is an admin action to remove an appointment
        _id = int(request.form.get('id'))
        try:
            # deletes from the db and removes from the list of 
            # previously queried appointements
            Appointment.query.get(_id).delete()
            appointments = list(filter(lambda x : x.id != _id, 
                                  appointments))
        except Exception as e:
            print("Error", str(e))
            pass
    return render_template("appointments.html", appointments=appointments, length=len(appointments))


# ====================================================== #
# ================= DOCTOR ROUTES ===================== #

@app.route('/doctordashboard')
@login_required
def doctordashboard():
    '''
    The doctor dashboard
    gives an overview on the number of appointments
    '''
    if request.method == 'GET':
        if current_user.status != 'doctor':
            return render_template('403.html')
    appointments = len(Appointment.query.all())
    return render_template("doctordash.html", total_appointments=appointments)


@app.route('/editdoctorprofile')
@login_required
def editdoctorprofile():
    '''
    The doctor edir profile view
    enables the doctor to edit profile
    '''
    doctor = User.query.get(current_user.id)

    firstname = request.form.get('firstname')
    lastname = request.form.get('lastname')
    email = request.form.get('email')
    phonenumber = request.form.get('phonenumber')
    gender = request.form.get('gender')
    user_password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')

    doctor.firstname = firstname
    doctor.lastname = lastname
    doctor.email = email
    doctor.phonenumber = phonenumber
    doctor.gender = gender

    if user_password == confirm_password:
        doctor.user_password = user_password

    try:
        doctor.update_user()
        flash('Profile Update Successfully')
        return render_template('editpatientprofile.html')
    except Exception as e:
        db.session.rollback()
        logging.exception(e)
    finally:
        db.session.close()
    return render_template('editdoctorprofile.html')


@app.route('/doctorappointments', methods=['GET', 'POST'])
@login_required
def doctorprofile():
    '''
    The Doctors -> Appointment view
    enables the doctor to see all his available appointments
    '''

    if current_user.status != 'doctor':
        return render_template('403.html')
    appointments = []
    appointments_query = Appointment.query.filter_by(
        doctor_id=current_user.id).all()
    for appointment in appointments_query:
        patient = User.query.get(appointment.patient_id)
        appointments.append({"appointment": appointment, "patient": patient})

    if request.method == 'POST':
        # the doctor action to delete an appointment
        _id = int(request.form.get('id'))
        try:
            # deletes from the db and removes from the list of 
            # previously queried appointements
            Appointment.query.get(_id).delete()
            appointments = list(filter(lambda x : x['appointment'].id != _id, 
                                  appointments))
        except Exception as e:
            print("Error", str(e))
            pass

    return render_template("doctorappointments.html", appointments=appointments)


@app.route('/addprescription', methods=['GET', 'POST'])
@login_required
def add_prescription():
    '''
    The Doctor's add prescription view
    enables the doctor to create a prescription for a patient
    '''
    users = User.query.filter_by(status='patient')

    if request.method == 'GET':
        if current_user.status != 'doctor':
            return render_template('403.html')
        else:
            return render_template("addprescription.html", users=users)

    if request.method == 'POST':
        # a doctor's action to create a new prescribtion
        drug = request.form.get('drug')
        quantity = request.form.get('quantity')
        condition = request.form.get('condition')
        patient_id = request.form.get('patient')
        doctor_id = current_user.id

        try:
            new_prescription = Prescription(
                drug=drug, quantity=quantity, condition=condition, patient_id=patient_id, doctor_id=doctor_id)
            new_prescription.add_prescription()
            flash("New Prescription has been added")
            redirect(url_for('add_prescription'))
        except Exception as e:
            db.session.rollback()
            logging.exception(e)
        finally:
            db.session.close()
    return render_template("addprescription.html", users=users)

# ====================================================== #
# ================= PATIENT ROUTES ===================== #


@app.route('/patientdashboard', methods=['GET', 'POST'])
@login_required
def patientdashboard():
    '''
    The patient dashboard
    gives an overview on the current appointments
    '''
    appointments_query = Appointment.query.filter_by(
    patient_id=current_user.id).all()
    appointments = []
    for appointment in appointments_query:
        doctor = User.query.get(appointment.doctor_id)
        appointments.append({"appointment": appointment, "doctor": doctor})

    if request.method == 'POST':
        # the patient action to delete an appointment
        _id = int(request.form.get('id'))
        try:
            # deletes from the db and removes from the list of 
            # previously query appointements
            Appointment.query.get(_id).delete()
            appointments = list(filter(lambda x : x['appointment'].id != _id, 
                                  appointments))
        except Exception as e:
            print("Error", str(e))
            pass
        
    return render_template('patient.html', appointments=appointments)


@app.route('/editpatientprofile', methods=['GET', 'POST'])
@login_required
def editpatientprofile():
    '''
    The patient edit profile view
    enables the patient to edit profile
    '''
    if request.method == 'POST':
        patient = User.query.get(current_user.id)

        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        email = request.form.get('email')
        phonenumber = request.form.get('phonenumber')
        gender = request.form.get('gender')
        user_password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        patient.firstname = firstname
        patient.lastname = lastname
        patient.email = email
        patient.phonenumber = phonenumber
        patient.gender = gender

        if user_password == confirm_password:
            patient.user_password = user_password

        try:
            patient.update_user()
            flash('Profile Update Successfully')
            return render_template('editpatientprofile.html')
        except Exception as e:
            db.session.rollback()
            logging.exception(e)
        finally:
            db.session.close()

    return render_template('editpatientprofile.html')


# Book Appointment

@app.route('/bookappointment', methods=['POST', 'GET'])
@login_required
def bookappointment():

    '''
    The Patient's book appointment view
    enables the patient to book an appointment with a doctor
    '''
    if request.method == 'GET':
        if current_user.status != 'patient':
            return render_template('403.html')

    doctors = User.query.filter_by(status='doctor').all()

    if request.method == 'POST':
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        gender = request.form.get('gender')
        date = request.form.get('date')
        time = request.form.get('time')
        phone_number = request.form.get('phonenumber')
        doctor_id = int(request.form.get('select-doctor'))
        patient_id = int(current_user.id)
        condition = request.form.get('injury-condition')

        if not all([firstname, lastname, date, time, phone_number, doctor_id, gender, condition]):
            # ensure all the fields are complete
            flash("Enter all required fields")
            return redirect(url_for('bookappointment'))
        try:
            appointment = Appointment(firstname=firstname, lastname=lastname, gender=gender, date=date, time=time,
                                      phone_number=phone_number, doctor_id=doctor_id, patient_id=patient_id, condition=condition)
            appointment.add_appointment()
            flash("Appointment has been booked")
            return redirect(url_for('patientdashboard'))
        except Exception as e:
            db.session.rollback()
            logging.exception(e)
        finally:
            db.session.close()

    return render_template("bookappointment.html", doctors=doctors)


@app.route('/patientappointments')
@login_required
def patientappointment():
    return render_template('patientappointment.html')


@app.route('/patientdata')
@login_required
def patientdata():
    return render_template('doctorpatientdata.html')


@app.route('/prescriptions')
@login_required
def prescription():
    prescriptions = []
    query_prescriptions = Prescription.query.filter_by(
        patient_id=current_user.id)
    for prescription in query_prescriptions:
        doctor = User.query.get(prescription.doctor_id)
        prescriptions.append({'prescription': prescription, 'doctor': doctor})
    return render_template('prescription.html', prescriptions=prescriptions)


@app.route('/patientdetails')
@login_required
def patientdetails():
    return render_template('doctorpatientdetails.html')


# ========================================================= #
# ================== AUTHENTICATION ======================= #

@app.route('/login', methods=['POST', 'GET'])
def login():
    '''
    The login view for all users
    '''
    if request.method == 'POST':

        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        print(user)
        # check if the user actually exists
        # take the user-supplied password, hash it, and compare it to the hashed password in the database
        if not user or not check_password_hash(user.password, password):
            flash('Please check your login details and try again.')
            # if the user doesn't exist or password is wrong, reload the page
            return redirect(url_for('login'))
        if user is not None and check_password_hash(user.password, password):
            login_user(user)
            # if the above check passes, then we know the user has the right credentials
            if user.status == 'patient':
                return redirect(url_for('patientdashboard'))
            elif user.status == 'doctor':
                return redirect(url_for('doctordashboard'))
            elif user.status == 'admin':
                return redirect(url_for('admindashboard'))

    return render_template("login.html")


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    '''
    The signup view for the both the doctors and the patients
    '''

    if request.method == 'POST':
        # Read the posted values from the UI
        print("Posting...")

        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        email = request.form.get('email')
        phonenumber = request.form.get('phonenumber')
        status = request.form.get('status')
        gender = request.form.get('gender')
        user_password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Validate the received values
        if not all([firstname, lastname, email, gender, user_password, phonenumber, status, confirm_password]):
            print("There is an error")
            flash("Enter all required fields")
            return redirect(url_for('signup'))

        if user_password != confirm_password:
            print("Password not mathcin")
            flash('Password Mismatch')
            return redirect(url_for('signup'))

        # if this returns a user, then the email already exists in database
        user = User.query.filter_by(email=email).first()

        if user:
            print("User exists already")
            flash("User already exist")
            return redirect(url_for('signup'))

        # Hash user password
        try:

            password = generate_password_hash(
                user_password, method='sha256', salt_length=10)
            new_user = User(firstname=firstname, lastname=lastname, email=email, gender=gender,
                            phonenumber=phonenumber, password=password, status=status)
            new_user.add_user()
            flash("Account Created Successfuly")
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            logging.exception(e)
        finally:
            db.session.close()

    return render_template("register.html")


@ app.route('/logout')
def logout():
    '''
    The logout handler
    '''
    logout_user()
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
