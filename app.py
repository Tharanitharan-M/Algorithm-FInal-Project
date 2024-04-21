import time

from flask import Flask, render_template, request, redirect, url_for, session, send_file
from flask_mysqldb import MySQL
from cryptography.fernet import Fernet, InvalidToken
from geopy.geocoders import Nominatim
from math import radians, sin, cos, sqrt, atan2
import pandas as pd
import geopandas
import networkx as nx
import osmnx as ox
import numpy as np
import traceback
import logging


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

from math import radians, sin, cos, sqrt, atan2
from flask import jsonify

@app.route('/search_doctors', methods=['GET', 'POST'])
def search_doctors():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        doctor_type = request.form.get('doctor_type')

        # Get patient's latitude and longitude from MySQL
        cur = mysql.connection.cursor()
        cur.execute("SELECT lat, lng FROM users WHERE username = %s", (session['username'],))
        patient = cur.fetchone()
        cur.close()

        if patient:
            # Get all doctors of the selected type from MySQL
            cur = mysql.connection.cursor()
            cur.execute("SELECT name, specialization, availability, ratings, Latitude, Longitude FROM doctors WHERE specialization = %s",
                        (doctor_type,))
            doctors = cur.fetchall()
            cur.close()

            if doctors:
                # Calculate distance between patient and each doctor using Haversine formula
                ranked_doctors = []
                for doctor in doctors:
                    doctor_name, specialization, availability, ratings, lat, lng = doctor
                    distance = calculate_distance(patient[0], patient[1], lat, lng)
                    ranked_doctors.append({
                        'name': doctor_name,
                        'specialization': specialization,
                        'availability': availability,
                        'distance': distance,
                        'ratings': ratings
                    })

                # Rank doctors based on distance
                ranked_doctors.sort(key=lambda x: x['distance'])
                # print(ranked_doctors)
                # Display the ranked list of doctors
                return render_template('search_doctors.html', doctors=ranked_doctors)
            else:
                return "No doctors found for the selected type."
        else:
            return "Patient not found."

    return render_template('search_doctors.html')


def calculate_distance(lat1, lon1, lat2, lon2):
    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    radius = 3959  # Radius of the Earth in miles
    distance = radius * c

    return round(distance,2)


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

def get_nearest_node(g, lat, log):
    try:
        node = ox.nearest_nodes(g, log, lat)
        return node
    except Exception as e:
        logging.error(traceback.format_exc())


def find_routes(g, source, target, weight='travel_time'):
    routes = []
    travel_time = []
    try:
        route = nx.dijkstra_path(g, source=source, target=target, weight=weight)
        routes.append(route)
        travel_time.append(nx.shortest_path_length(g, source, target, weight=weight))
    except Exception as e:
        travel_time.append(np.inf)
        routes.append(np.nan)
        logging.warning("No route found for " + str(target))
    return routes, travel_time


def plot_one_route(g, route, filepath, saveFig=False):
    fig, ax = ox.plot_graph_route(g, route, route_linewidth=6, node_size=2, save=saveFig, filepath=filepath)

@app.route('/navigation/<doctor_name>', methods=['GET'])
def navigation(doctor_name):
    # Your navigation logic here
    # Example code for path calculation and image generation
    place = "Portland, Maine"
    filepath = "./portland_map.graphml"
    city_graph = ox.load_graphml(filepath)

    # Get patient's latitude and longitude from MySQL
    cur = mysql.connection.cursor()
    cur.execute("SELECT lat, lng FROM users WHERE username = %s", (session['username'],))
    from decimal import Decimal

    # Assuming you have fetched the data using cur.fetchone()
    lat_decimal, lng_decimal = cur.fetchone()

    # Convert Decimal objects to floats
    lat_float = float(lat_decimal)
    lng_float = float(lng_decimal)

    # Now you have lat_float and lng_float as floats
    source_loc = (lat_float, lng_float)
    cur.close()

    # Get doctor's latitude and longitude from MySQL
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT Latitude, Longitude FROM doctors WHERE name = %s",
        (doctor_name,))
    # Assuming you have fetched the data using cur.fetchone()
    lat_decimal, lng_decimal = cur.fetchone()

    # Convert Decimal objects to floats
    lat_float = float(lat_decimal)
    lng_float = float(lng_decimal)

    # Now you have lat_float and lng_float as floats
    target_loc = (lat_float, lng_float)
    cur.close()
    print(target_loc, source_loc,sep="\n")
    source = get_nearest_node(city_graph, source_loc[0], source_loc[1])  # Patient location
    target = get_nearest_node(city_graph, target_loc[0], target_loc[1])  # Doctor's location

    routes, travel_time = find_routes(city_graph, source, target)
    plot_one_route(city_graph, routes[np.argmin(travel_time)], saveFig=True, filepath="static/route.png")

    timestamp = int(time.time())  # Get current timestamp
    return render_template('navigation.html', doctor_name=doctor_name, timestamp=timestamp)


@app.route('/get_image')
def get_image():
    return send_file("static/route.png", mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)
