from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from cryptography.fernet import Fernet, InvalidToken
from geopy.geocoders import Nominatim
from math import radians, sin, cos, sqrt, atan2

app = Flask(__name__)
app.secret_key = 'secret_key'

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'algoproject'

mysql = MySQL(app)

# Geocoder Configuration
geolocator = Nominatim(user_agent='algoproject')

# Generate a key for encryption and decryption
key = Fernet.generate_key()
cipher_suite = Fernet(key)


# Routes
@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()

        if user:
            try:
                decrypted_password = cipher_suite.decrypt(user[2].encode()).decode()
                if password == decrypted_password:
                    session['username'] = username

                    if user[4] is not None and user[5] is not None:
                        return redirect(url_for('search_doctors'))
                    else:
                        return redirect(url_for('dashboard'))
                else:
                    return "Incorrect password"
            except InvalidToken:
                app.logger.error("InvalidToken error during password decryption for user: %s", username)
                return "Error during login. Please try again."
        else:
            return "Incorrect username or password"
    return render_template('login.html')


# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#
#         cur = mysql.connection.cursor()
#         cur.execute("SELECT * FROM users WHERE username = %s", (username,))
#         user = cur.fetchone()
#         cur.close()
#
#         if user:
#             try:
#                 decrypted_password = cipher_suite.decrypt(user[2].encode()).decode()
#                 if password == decrypted_password:
#                     session['username'] = username
#                     return redirect(url_for('dashboard'))
#                 else:
#                     return "Incorrect password"
#             except InvalidToken:
#                 app.logger.error("InvalidToken error during password decryption for user: %s", username)
#                 return "Error during login. Please try again."
#         else:
#             return "Incorrect username or password"  # Update the message to be more specific
#     return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = cipher_suite.encrypt(request.form['password'].encode()).decode()

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        existing_user = cur.fetchone()

        if existing_user:
            return "Username already taken. Please choose another username."
        else:
            cur.execute("INSERT INTO users (username, encrypted_password) VALUES (%s, %s)", (username, password))
            mysql.connection.commit()
            cur.close()

            return redirect(url_for('dashboard'))

    return render_template('signup.html')


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        address1 = request.form['address1']
        address2 = request.form['address2']
        city = request.form['city']
        state = request.form['state']
        pincode = request.form['pincode']
        health_condition = request.form['health_condition']
        insurance_plan = request.form['insurance_plan']

        # Get latitude and longitude using Geopy
        full_address = f"{address1}, {address2}, {city}, {state}, {pincode}"
        location = geolocator.geocode(full_address)
        if location:
            lat, lng = location.latitude, location.longitude
        else:
            lat, lng = None, None

        # Encrypt data before storing in MySQL
        encrypted_name = cipher_suite.encrypt(name.encode()).decode()
        encrypted_age = cipher_suite.encrypt(str(age).encode()).decode()
        encrypted_gender = cipher_suite.encrypt(gender.encode()).decode()
        encrypted_address1 = cipher_suite.encrypt(address1.encode()).decode()
        encrypted_address2 = cipher_suite.encrypt(address2.encode()).decode()
        encrypted_city = cipher_suite.encrypt(city.encode()).decode()
        encrypted_state = cipher_suite.encrypt(state.encode()).decode()
        encrypted_pincode = cipher_suite.encrypt(pincode.encode()).decode()
        encrypted_health_condition = cipher_suite.encrypt(health_condition.encode()).decode()
        encrypted_insurance_plan = cipher_suite.encrypt(insurance_plan.encode()).decode()

        cur = mysql.connection.cursor()
        cur.execute(
            "UPDATE users SET name = %s, age = %s, gender = %s, address1 = %s, address2 = %s, city = %s, state = %s, pincode = %s, lat = %s, lng = %s, health_condition = %s, insurance_plan = %s WHERE username = %s",
            (encrypted_name, encrypted_age, encrypted_gender, encrypted_address1, encrypted_address2, encrypted_city,
             encrypted_state, encrypted_pincode, lat, lng, encrypted_health_condition, encrypted_insurance_plan,
             session['username']))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('search_doctors'))
    return render_template('dashboard.html')

@app.route('/search_doctors', methods=['GET', 'POST'])
def search_doctors():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        doctor_type = request.form.get('doctor_type')

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM doctors WHERE Specialization = %s", (doctor_type,))
        doctors = cur.fetchall()
        cur.close()

        return render_template('search_doctors.html', doctors=doctors)

    return render_template('search_doctors.html')

@app.route('/decrypt_data')
def decrypt_data():
    if 'username' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE username = %s", (session['username'],))
    user = cur.fetchone()
    cur.close()

    if user:
        try:
            decrypted_user = {
                'password': cipher_suite.decrypt(user[2].encode()).decode(),
                'name': cipher_suite.decrypt(user[3].encode()).decode(),
                'age': cipher_suite.decrypt(user[4].encode()).decode(),
                'gender': cipher_suite.decrypt(user[5].encode()).decode(),
                'address1': cipher_suite.decrypt(user[6].encode()).decode(),
                'address2': cipher_suite.decrypt(user[7].encode()).decode(),
                'city': cipher_suite.decrypt(user[8].encode()).decode(),
                'state': cipher_suite.decrypt(user[9].encode()).decode(),
                'pincode': cipher_suite.decrypt(user[10].encode()).decode(),
                'lat': user[11],
                'lng': user[12],
                'health_condition': cipher_suite.decrypt(user[13].encode()).decode(),
                'insurance_plan': cipher_suite.decrypt(user[14].encode()).decode()
            }

            return render_template('decrypt_data.html', user=decrypted_user)
        except InvalidToken:
            app.logger.error("InvalidToken error during data decryption for user: %s", session['username'])
            return "Error during data decryption. Please try again."
    else:
        return "User not found"


@app.route('/sign_out', methods=['POST'])
def sign_out():
    if request.json and 'sign_out' in request.json and request.json['sign_out'] == True:
        session.clear()
        return 'Session data cleared. You have been signed out.', 200
    else:
        return 'Invalid request', 400


if __name__ == '__main__':
    app.run()
