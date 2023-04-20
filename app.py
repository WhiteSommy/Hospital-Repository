import logging
from flask import Flask, flash, redirect, render_template, request, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_required, current_user, login_user, logout_user

from models import db, User, Appointment, Prescription, login

app = Flask(__name__)
app.secret_key = "secret"


database_name = 'hospitalmanagement'
database_username = 'root'
database_password = 'godon2009'


app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql+pymysql://{}:{}@{}/{}'.format(
    database_username, database_password, '127.0.0.1', database_name)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


db.init_app(app)
login.init_app(app)
login.login_view = 'login'


@app.before_first_request
def create_all():
    db.create_all()


# =================================================#
# ============== UNIVERSAL ROUTE ==================#

@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template("index.html")


@app.route('/forgetpassword', methods=['GET', 'POST'])
def forget_password():

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm-password')

        if password != confirm_password:
            flash('Password MisMatch')
            return redirect('fp.html')

        try:
            user = User.query.filter_by(email=email).first()
            user.password = generate_password_hash(
                password,  method='sha256', salt_length=10)
            user.update_user()
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
            new_user.add_user()
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
    if request.method == 'GET':
        if current_user.status != 'admin':
            return render_template('403.html')
    return render_template("adminDashboard.html")


@app.route('/admin/doctors')
@login_required
def doctors():
    if request.method == 'GET':
        if current_user.status != 'admin':
            return render_template('403.html')
    doctors = User.query.filter_by(status='doctor').all()
    return render_template("doctors.html", doctors=doctors, length=len(doctors))


@app.route('/admin/patients')
@login_required
def patients():
    if request.method == 'GET':
        if current_user.status != 'admin':
            return render_template('403.html')
    patients = User.query.filter_by(status='patient').all()
    return render_template("patients.html", patients=patients, length=len(patients))


@app.route('/admin/appointments')
@login_required
def allAppointments():
    if request.method == 'GET':
        if current_user.status != 'admin':
            return render_template('403.html')
    appointments = Appointment.query.all()
    return render_template("appointments.html", appointments=appointments, length=len(appointments))


# ====================================================== #
# ================= DOCTOR ROUTES ===================== #

@app.route('/doctordashboard')
@login_required
def doctordashboard():
    if request.method == 'GET':
        if current_user.status != 'doctor':
            return render_template('403.html')
    appointments = len(Appointment.query.all())
    return render_template("doctordash.html", total_appointments=appointments)


@app.route('/editdoctorprofile')
@login_required
def editdoctorprofile():
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


@app.route('/doctorappointments')
@login_required
def doctorprofile():
    if request.method == 'GET':
        if current_user.status != 'doctor':
            return render_template('403.html')

    appointments = []
    appointments_query = Appointment.query.filter_by(
        doctor_id=current_user.id).all()
    for appointment in appointments_query:
        patient = User.query.get(appointment.patient_id)
        appointments.append({"appointment": appointment, "patient": patient})
    return render_template("doctorappointments.html", appointments=appointments)


@app.route('/addprescription', methods=['GET', 'POST'])
@login_required
def add_prescription():
    users = User.query.filter_by(status='patient')

    if request.method == 'GET':
        if current_user.status != 'doctor':
            return render_template('403.html')
        else:
            return render_template("addprescription.html", users=users)

    if request.method == 'POST':
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


@app.route('/patientdashboard')
@login_required
def patientdashboard():
    appointments_query = Appointment.query.filter_by(
        patient_id=current_user.id).all()
    appointments = []
    for appointment in appointments_query:
        doctor = User.query.get(appointment.doctor_id)
        appointments.append({"appointment": appointment, "doctor": doctor})
    return render_template('patient.html', appointments=appointments)


@app.route('/editpatientprofile', methods=['GET', 'POST'])
@login_required
def editpatientprofile():

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

    if request.method == 'POST':
        # Read the posted values from the UI

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
            flash("Enter all required fields")
            return redirect(url_for('signup'))

        if user_password != confirm_password:
            flash('Password Mismatch')
            return redirect(url_for('signup'))

        # if this returns a user, then the email already exists in database
        user = User.query.filter_by(email=email).first()

        if user:
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
    logout_user()
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
