from flask import Flask, render_template, request, jsonify
from flask_mail import Mail, Message
import random
import os

app = Flask(__name__)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = os.getenv("account_email")
app.config['MAIL_PASSWORD'] = os.getenv("account_pwd")      

mail = Mail(app)


def generate_verification_code():
    return str(random.randint(100000, 999999))

verification_codes = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send_verification_email', methods=['POST'])
def send_verification_email():
    email = request.form['email']
    verification_code = generate_verification_code()
    verification_codes[email] = verification_code

    # Send email
    msg = Message('Email Verification', recipients=[email])
    msg.body = f'Your verification code is: {verification_code}'
    mail.send(msg)

    return jsonify({'message': 'Verification code sent successfully'})

@app.route('/verify_email', methods=['POST'])
def verify_email():
    email = request.form['email']
    code = request.form['code']
    if email in verification_codes and verification_codes[email] == code:
        return jsonify({'verified': True})
    else:
        return jsonify({'verified': False})
@app.route('/Form')
def show_form():
    return render_template('form.html')

"""@app.route('/form2.html')
def show_form_2():
    return render_template('form2.html')"""

@app.route('/submit', methods=['POST'])
def process_form():
    gender = request.form['question1']
    specialty = request.form['question2']
    hours_studying = int(request.form['question3'])

    output = f"You are a {gender}, studying in the {specialty} specialty , you spend {hours_studying} hours studying per week."
    return output

if __name__ == '__main__':
    app.run(debug=True)
