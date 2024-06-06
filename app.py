from flask import Flask, flash, render_template, request, jsonify, session
import random
import firebase_admin
from firebase_admin import credentials, auth
import sendgrid
from sendgrid.helpers.mail import Mail
from flask import Flask, request, render_template, redirect, url_for
import bcrypt
import os


app = Flask(__name__)
app.secret_key = os.urandom(24).hex()



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    email = request.form['email']
    if email.endswith('@ensia.edu.dz'):
        # Extract surname and name from the email
        parts = email.split('@')[0].split('.')
        surname, name = parts[0], parts[1]

        # Save details in session
        session['email'] = email
        session['name'] = name.upper()  
        session['surname'] = surname.upper() 

        # Redirect to the next page
        return redirect(url_for('form'))
    else:
        flash('You should use your ENSIA email. Please try again.')
        return redirect(url_for('index'))
    

@app.route('/form')
def form():
    return render_template('form.html')

@app.route('/results')
def results():
    email = session.get('email')
    name = session.get('name')
    surname = session.get('surname')


    return render_template('results.html')




if __name__ == '__main__':
    app.run(debug=True)
