from flask import (Blueprint, flash, redirect, render_template, request, url_for, Flask)
from flaskr.db import get_db

import PyPDF2

import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from geopy.geocoders import Nominatim
from geopy.distance import geodesic

app = Flask(__name__)

bp = Blueprint('customers', __name__)

locator = Nominatim(user_agent="SFFoodFriends")
port = 465  # For SSL
password = 'Helping123!'
sender_email = "sffoodfriends@gmail.com"

distance_weight = 0.4
gender_weight = 0.15
priority_gender_weight = 0.6
long_term_weight = 0.15
language_weight = 0.3


@bp.route('/')
def start():
    return redirect(url_for('customers.validate'))


@bp.route('/<id>')
def index(id):
    db = get_db()
    volunteer = db.execute(
        'SELECT * FROM volunteer WHERE id = ?', (id,)
    ).fetchone()
    areas = volunteer['areas']
    return redirect(url_for('customers.matching', areas=areas))


@bp.route('/validate', methods=('GET', 'POST'))
def validate():
    if request.method == 'POST':
        email = request.form['email']
        db = get_db()
        error = None
        volunteer = db.execute(
            'SELECT * FROM volunteer WHERE email = ?', (email,)
        ).fetchone()

        if volunteer is None:
            error = 'We do not have this email in our database.'
            'Please sign up or contact us on the main website.'

        if error is None:
            email = volunteer['email']
            if volunteer['conditions'] == 0:
                return redirect(url_for('customers.conditions', e_mail_vol=email))
            else:
                return redirect(url_for('customers.matching', e_mail_vol=email))

        flash(error)

    return render_template('customers/validate.html')


@bp.route('/new-request', methods=('GET', 'POST'))
def new_request():
    if request.method == 'POST':
        email = request.form['email']
        assistance_type = request.form['type']
        db = get_db()
        error = None
        customer = db.execute(
            'SELECT * FROM customer WHERE email = ?', (email,)
        ).fetchone()

        if customer is None:
            error = 'We do not have this email in our database. Please sign up or contact us on the main website.'
        elif customer['served'] == 0:
            error = 'You still have an outstanding request in our database. If you want to ammend your existing request, inform your helper once he contacts you or contact us if urgent.'

        if error is None:
            db.execute(
                'INSERT INTO customer (neighborhood, email, phone, preference, assistancetype, payment, served) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (customer['neighborhood'], customer['email'], customer['phone'], customer['preference'],
                 assistance_type, customer['payment'], 0)
            )
            return redirect(url_for('customers.confirm'))

        flash(error)

    return render_template('customers/request.html')


@bp.route('/confirm', methods=('GET', 'POST'))
def confirm():
    return render_template('customers/confirm.html')


@bp.route('/conditions/<e_mail_vol>', methods=('GET', 'POST'))
def conditions(e_mail_vol):
    if request.method == 'POST':
        db = get_db()
        error = None

        try:
            agree = int(request.form['agree'])
        except:
            error = 'You must agree to the terms and conditions to continue.'

        if error is None and agree == 1:
            db.execute(
                'UPDATE volunteer SET conditions = ?'
                ' WHERE email = ?',
                (agree, e_mail_vol)
            )
            db.commit()

            return redirect(url_for('customers.matching', e_mail_vol=e_mail_vol))

        flash(error)
        return redirect(request.url)

    return render_template('customers/conditions.html')


@bp.route('/terms-conditions')
def terms_conditions():
    pdf = PyPDF2.PdfFileReader('flaskr/static/Protocol_Volunteer.pdf')
    #response = make_response(pdf.output(dest='S').encode('latin-1'))
    #response.headers.set('Content-Disposition', 'attachment', 'terms_and_conditions' + '.pdf')
    #response.headers.set('Content-Type', 'application/pdf')
    return pdf


@bp.route('/matching/<e_mail_vol>', methods=('GET', 'POST'))
def matching(e_mail_vol):
    db = get_db()

    volunteer = db.execute(
        'SELECT * FROM volunteer WHERE email = ?', (e_mail_vol,)
    ).fetchone()

    customers = db.execute(
        'SELECT * FROM customer WHERE served = ?', (0,)
    ).fetchall()

    scores = list()
    for customer in customers:  # for every customer in the database
        customer_loc = customer['latlng'].split('+')
        volunteer_loc = volunteer['latlng'].split('+')
        # Calculate the distance between the volunteer and customer
        dist = float(geodesic(customer_loc, volunteer_loc).miles)

        if dist > 1:
            continue

        if customer['language'] is None:
            language = 0.5
        elif customer['language'] in volunteer['language'].split('+'):
            language = 1
        else:
            language = 0
        if customer['gender'] == volunteer['gender']:
            gendermatch = 1
        else:
            gendermatch = 0

        if customer['longterm'] == 1 == volunteer['longterm']:
            long_term = 1
        elif customer['longterm'] != volunteer['longterm']:
            long_term = 0
        else:
            long_term = 0.5

        if customer['priority'] == 1:
            score = (1 - dist) * distance_weight + gendermatch * priority_gender_weight + long_term * long_term_weight + language * language_weight
        else:
            score = (1 - dist) * distance_weight + gendermatch * gender_weight + long_term * long_term_weight + language * language_weight
        scores.append(score)

    if len(scores) == 0:
        result = 'Currently, there are no people in need in your area. We really appreciate your help, thank you!!'
        return render_template('customers/agree.html', result=result, hit="We didn't find a match for you", match=0)

    match_index = scores.index(max(scores))
    customer = customers[match_index]

    #    for neighborhood in neighborhoods:
    #        customer = db.execute(
    #            'SELECT * FROM customer WHERE neighborhood = ?', (neighborhood,)
    #        ).fetchone()
    #        if customer is not None:
    #            if customer['served'] == 0:
    #                break
    #            else:
    #                customer = None

    #    if customer is None:
    #        result = 'Currently, there are no people in need in your areas. We really appreciate your help, thank you!!'
    #        return render_template('customers/agree.html', result=result, hit="We didn't find a match for you", match = 0)

    name = customer['name']
    type_of_assistance = customer['assistancetype']
    neighborhood = customer['neighborhood']
    email = customer['email']
    phone = customer['phone']
    preference = customer['preference']

    if preference == 0:
        preference = 'Phone'
    else:
        preference = 'Email'
    result = [name, type_of_assistance, neighborhood, email, phone, preference]

    if request.method == 'POST':
        error = None
        try:
            agree = int(request.form['agree'])
        except:
            error = 'Please select yes or no.'

        if error is None:
            if agree == 1:
                db.execute(
                    'UPDATE customer SET served = ?'
                    ' WHERE email = ?',
                    (agree, email)
                )
                db.commit()

                name_vol = volunteer['name']
                email_vol = volunteer['email']
                phone_vol = volunteer['phone']

                name_cust = name
                assistance_cust = type_of_assistance
                phone_cust = phone
                email_cust = email
                preference_cust = preference

                message_vol = MIMEMultipart("alternative")
                message_vol["Subject"] = "SF Food Friends - Match confirmation!"
                message_vol["From"] = sender_email
                message_vol["To"] = email_vol

                message_cust = MIMEMultipart("alternative")
                message_cust["Subject"] = "SF Food Friends - You matched with a volunteer!"
                message_cust["From"] = sender_email
                message_cust["To"] = email_cust

                text_cust_email = """\
Dear {},

You just received your match!

Here you will get your volunteer’s name, email, and phone number. 
Your volunteer will contact you to coordinate your delivery. 

We want to encourage community support and trusting, lasting relationships. 
The person you are matched with is someone within your community and neighborhood. 
They might even be right next door! If you have any worries, do not hesitate to contact us.
Please remember we have your health as our top priority. 

To ensure this, follow the CDC guidelines and remember to wash your hands and wipe your delivered items upon receipt. 

CDC guidelines: https://www.cdc.gov/coronavirus/2019-ncov/prepare/prevention.html

Thank you so much for signing up!

Your volunteer!
Name: {}
Phone number: {}
Email: {}

Sincerely,
SF FoodFriends

Our phone number: (415)-636-6068



This match program is being organized by private citizens for the benefit of those in our community. 
By completing the sign up form to be matched you agree that you accept all risk and responsibility and further hold any facilitator associated with SF Food Friends harmless. 
For any additional questions, please contact SFFoodFriends@gmail.com. (415-636-6068) 

"""

                text_vol_email = """\
Dear {},

You just received your match!

Here you will get your match’s name, email, and phone number. 
Please contact your match to coordinate your delivery. 
They will have also received your information.

We want to encourage community support and trusting, lasting relationships. 
If you can, it would be great if you could remain as a point of support for the person in need. 
For example, if elderly, you can have check in calls to make sure they are okay. 

Please remember the protocol you agreed to when signing up.

You can also find the CDC guidelines here: https://www.cdc.gov/coronavirus/2019-ncov/prepare/prevention.html

Thank you so much for signing up and helping your community!

Name: {}
Type of assistance: {}
Phone number: {}
Email: {}
Contact Preference: {}

Sincerely,
SF FoodFriends

Our phone number: (415)-636-6068



This match program is being organized by private citizens for the benefit of those in our community. 
By completing the sign up form to be matched you agree that you accept all risk and responsibility and further hold any facilitator associated with SF Food Friends harmless. 
For any additional questions, please contact SFFoodFriends@gmail.com. (415-636-6068)

"""

                text_cust_email = text_cust_email.format(name_cust, name_vol, phone_vol, email_vol)
                part1 = MIMEText(text_cust_email, "plain")
                message_cust.attach(part1)

                text_vol_email = text_vol_email.format(name_vol, name_cust, assistance_cust, phone_cust, email_cust, preference_cust)
                part1 = MIMEText(text_vol_email, "plain")
                message_vol.attach(part1)

                context = ssl.create_default_context()
                with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
                    server.login(sender_email, password)

                    # Send email here
                    server.sendmail(sender_email, email_vol, message_vol.as_string())
                    server.sendmail(sender_email, email_cust, message_cust.as_string())
            return redirect(url_for('customers.direct_to', agree=agree))

        flash(error)
        return redirect(request.url)

    return render_template('customers/agree.html', result=result, hit='We found a match for you.', match=1)


@bp.route('/direct/<agree>', methods=['GET', 'POST'])
def direct_to(agree):
    agree = int(agree)
    if agree == 1:
        message_one = 'Thank you very much.'
        message_two = 'You will now be redirected to the SF Food Friends home page. ' \
                      'You can find further information there about how to interact with your friend in need'
    else:
        message_one = 'Sorry to hear that.'
        message_two = 'You will now be redirected to the SF Food Friends home page.'

    if request.method == 'POST':
        return redirect("https://sffoodfriends.wixsite.com/home")

    return render_template('customers/redirect.html', message_one=message_one, message_two=message_two)
