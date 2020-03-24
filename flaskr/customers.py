from flask import (Blueprint, flash, redirect, render_template, request, url_for, Flask)

from flaskr.db import get_db

app = Flask(__name__)

bp = Blueprint('customers', __name__)


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
            areas = volunteer['areas']
            return redirect(url_for('customers.matching', areas=areas))

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
            error = 'You still have an outstanding request in our database. If you want to ammend your existing request, inform your helper once he contacts you or wait for 3 days to submit a new request.'

        if error is None:
            db.execute(
                'INSERT INTO customer (neighborhood, email, phone, preference, assistancetype, payment, served) VALUES (?, ?, ?, ?, ?, ?, ?)'
                (customer['neighborhood'], customer['email'], customer['phone'], customer['preference'], assistance_type, customer['payment'], 0)
            )
            return redirect(url_for('customers.confirm'))

        flash(error)

    return render_template('customers/request.html')


@bp.route('/confirm', methods=('GET', 'POST'))
def confirm():
    return render_template('customers/confirm.html')


@bp.route('/match/<areas>', methods=['GET', 'POST'])
def matching(areas):
    neighborhoods = areas.split('+')
    db = get_db()

    for neighborhood in neighborhoods:
        customer = db.execute(
            'SELECT * FROM customer WHERE neighborhood = ?', (neighborhood,)
        ).fetchone()
        if customer is not None:
            if customer['served'] == 0:
                break
            else:
                customer = None

    if customer is None:
        result = 'Currently, there are no people in need in your areas. We really appreciate your help, thank you!!'
        return render_template('customers/agree.html', result=result, hit="We didn't find a match for you", match = 0)

    type_of_assistance = customer['assistancetype']
    cust_neighborhood = customer['neighborhood']
    email = customer['email']
    phone = customer['phone']
    preference = customer['preference']
    if preference == 0:
        preference = 'Phone'
    else:
        preference = 'Email'
    result = [type_of_assistance, cust_neighborhood, email, phone, preference]

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
