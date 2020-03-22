from flask import (Blueprint, flash, redirect, render_template, request, url_for, Flask)

from flaskr.db import get_db

app = Flask(__name__)

bp = Blueprint('customers', __name__)


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
            error = 'Incorrect email.'

        if error is None:
            areas = volunteer['areas']
            return redirect(url_for('customers.matching', areas=areas))

        flash(error)

    return render_template('customers/validate.html')


@bp.route('/match/<areas>', methods=['GET', 'POST'])
def matching(areas):
    neighborhoods = areas.split('+')
    db = get_db()

    for neighborhood in neighborhoods:
        customer = db.execute(
            'SELECT * FROM customers WHERE neighborhood = ?', (neighborhood,)
        ).fetchone()
        if customer is not None:
            if customer['served'] == 0:
                break

    if customer is None:
        result = 'Currently, there are no people in need in your areas. We really appreciate your help, thank you!!'
        return render_template('customers/agree.html', result=result, hit="We didn't find a match for you", match=0)

    type_of_assistance = customer['type_of_assistance']
    cust_neighborhood = customer['neighborhood']
    email = customer['email']
    phone = customer['phone']
    preference = customer['preference']
    if preference == 0:
        preference = 'Phone'
    else:
        preference = 'Email'
    result = 'Type of assistance needed: ' + type_of_assistance + '; Neighborhood: ' + cust_neighborhood + '; Email: ' \
             + email + '; Phone: ' + phone + '; preference: ' + preference

    if request.method == 'POST':
        error = None
        try:
            agree = int(request.form['agree'])
        except:
            error = 'Please select yes or no.'

        if error is None:
            if agree == 1:
                db.execute(
                    'UPDATE customers SET served = ?'
                    ' WHERE email = ?',
                    (agree, email)
                )
                db.commit()
            return redirect(url_for('customers.direct_to', agree=agree))

        flash(error)
        return redirect(request.url)

    return render_template('customers/agree.html', result=result, hit='We found a match for you.', match=1)


@bp.route('/direct/<agree>')
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
        return redirect("http://www.sffoodfriends.com")

    return render_template('customers/redirect.html', message_one=message_one, message_two=message_two)
