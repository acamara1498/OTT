"""
This module executes the Flask application.
"""

import sqlite3
from sqlite3 import Error
from flask import Flask, render_template, json, request, session
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from sqlite3 import Error
from db_init import create_connection

app = Flask(__name__, template_folder="static/templates")
app.secret_key = "DooLouGulu"
app.config['SESSION_TYPE'] = 'redis'
Session(app)


# Establish connection
conn = create_connection("server/users.db")

def get_preferences(email):
    """
    Given a user's email address, return their preferences.
    email (string): Email address of a user.

    return: A dictionary of preferences.
    """
    c = conn.cursor()
    # Extract the data
    activity = c.execute("SELECT activity FROM prefs WHERE email = ?", (email, )).fetchone()[0]
    price = c.execute("SELECT price FROM prefs WHERE email = ?", (email, )).fetchone()[0]
    rating = c.execute("SELECT rating FROM prefs WHERE email = ?", (email, )).fetchone()[0]
    latitude = c.execute("SELECT latitude FROM prefs WHERE email = ?", (email, )).fetchone()[0]
    longitude = c.execute("SELECT longitude FROM prefs WHERE email = ?", (email, )).fetchone()[0]

    c.close()
    return {"activity": activity, "price": price, "rating": rating, "lat": latitude, "long": longitude}


@app.route("/")
def main():
    if "name" in session:
        return render_template("dashboard.html", name=session["name"], prefs=get_preferences(session["email"]), recent_update=False)
    else:
        return render_template("index.html")

@app.route("/signup")
def sign_up():
    if "name" in session:
        return render_template("dashboard.html", name=session["name"], prefs=get_preferences(session["email"]), recent_update=False)
    else:
        return render_template("signup.html")


@app.route("/register", methods=["POST", "GET"])
def register():
    if "name" in session:
        return render_template("dashboard.html", name=session["name"], prefs=get_preferences(session["email"]), recent_update=False)
    else:
        if request.method == "POST":
            c =  conn.cursor()
            try:
                _name = request.form["inputName"]
                _email = request.form["inputEmail"]
                _password = request.form["inputPassword"]

                # Validate the input
                if _name and _email and _password:
                    hashed_password = generate_password_hash(_password)
                    statement = c.execute("SELECT email FROM users")
                    for row in statement.fetchall():
                        if _email in row[0]:
                            c.close()
                            return render_template("signup.html", error_msg="A user with this email address already exists. Please use another or sign in above.")
                    c.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (_name, _email, hashed_password))
                    c.execute("INSERT INTO prefs (email, activity, price, rating, latitude, longitude) VALUES (?, ?, ?, ?, ?, ?)", (_email, "bakery", 3, 3.0, 40.807835, -73.963957))
                    conn.commit()
                    c.close()
                    session["name"] = _name
                    session["email"] = _email
                    return render_template("dashboard.html", name=session["name"], prefs=get_preferences(session["email"]), recent_update=False)
                else:
                    c.close()
                    return render_template("signup.html", error_msg="Please complete all required fields.")

            except Exception as e:
                return json.dumps({'error': str(e)})
            finally:
                c.close()
        else:
            return render_template("signup.html")

@app.route('/login', methods=["POST", "GET"])
def login():
    if "name" in session:
        return render_template("dashboard.html", name=session["name"], prefs=get_preferences(session["email"]), recent_update=False)
    else:
        if request.method == "POST":
            c = conn.cursor()
            try:
                _email = request.form["inputEmail"]
                _password = request.form["inputPassword"]

                # Validate the input
                if _email and _password:
                    statement = c.execute("SELECT email FROM users")
                    for row in statement.fetchall():
                        if _email in row[0]:
                            pas = c.execute("SELECT password FROM users WHERE email = ?", (_email, ))
                            for words in pas.fetchone():
                                if check_password_hash(words, _password):
                                    _name = c.execute("SELECT name FROM users WHERE email = ?", (_email, )).fetchone()[0]
                                    session["name"] = _name
                                    session["email"] = _email
                                    return render_template("dashboard.html", name=session["name"], prefs=get_preferences(session["email"]), recent_update=False)
                    c.close()
                    return render_template("login.html", error_msg="We were unable to find a match for these credentials. Please try again.")
                else:
                    render_template("login.html", error_msg="Please input valid credentials.")

            except Exception as e:
                return json.dumps({'error': str(e)})
            finally:
                c.close()
        else:
            return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("name", None)
    return render_template("index.html")

@app.route("/pref", methods=["POST", "GET"])
def log_prefs():
    if request.method == "POST":
        c =  conn.cursor()
        try:
            # _activity_type = request.form["activity_type"]
            # _price_pref = request.form["price_pref"]
            # _rating_pref = request.form["rating_ref"]
            # _lat_location = request.form["lat_location"]
            # _long_location = request.form["long_location"]
            _activity_type = request.form.get("activity_type", None)
            _price_pref = request.form.get("price_pref", None)
            _rating_pref = request.form.get("rating_pref", None)
            _lat_location = request.form.get("lat_location", None)
            _long_location = request.form.get("long_location", None)

            _email = session["email"]

            #return json.dumps({'error': str(_activity_type) + str(_price_pref) + str(_rating_pref) + str(_lat_location) + str(_long_location)})

            # Validate the input
            if _activity_type and _price_pref and _rating_pref and  _lat_location and _long_location:
                c.execute("UPDATE prefs SET activity = ?, price = ?, rating = ?, latitude = ?, longitude = ? WHERE email = ?", (_activity_type, _price_pref, _rating_pref, _lat_location, _long_location, _email))
                conn.commit()
                c.close()
                return render_template("dashboard.html", name=session["name"], prefs=get_preferences(session["email"]), recent_update=True)
            else:
                c.close()
                return render_template("dashboard.html", name=session["name"], prefs=get_preferences(session["email"]), recent_update=False)

        except Exception as e:
            return json.dumps({'error': str(e)})
        finally:
            c.close()
    else:
        return render_template("dashboard.html", name=session["name"], prefs=get_preferences(session["email"]), recent_update=False)

if __name__ == "__main__":
    app.run(debug=True, use_reloader=True, port=5002)
