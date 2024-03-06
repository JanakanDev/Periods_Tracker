from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)
app.secret_key = '5t5t5t'  # Change this to a secure value
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    periods = db.relationship('Period', backref='user', lazy=True)

class Period(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_date = db.Column(db.String(20), nullable=False)
    start_time = db.Column(db.String(10), nullable=False)
    end_time = db.Column(db.String(10), nullable=False)
    symptoms = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

def calculate_period_gap(start_date_1, start_date_2):
    start_date_1 = datetime.datetime.strptime(start_date_1, "%Y-%m-%d")
    start_date_2 = datetime.datetime.strptime(start_date_2, "%Y-%m-%d")
    period_gap = start_date_2 - start_date_1
    return period_gap.days

@app.route('/')
def index():
    if 'username' in session:
        with app.app_context():
            periods = Period.query.filter_by(user_id=session['user_id']).all()
        if len(periods) > 1:
            period_gaps = []
            for i in range(1, len(periods)):
                gap = calculate_period_gap(periods[i-1].start_date, periods[i].start_date)
                period_gaps.append(gap)
            avg_period_gap = sum(period_gaps) / len(period_gaps)
        else:
            avg_period_gap = None
        return render_template('home.html', periods=periods, avg_period_gap=avg_period_gap)
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['username'] = username
            session['user_id'] = user.id
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User(username=username, password=password)
        with app.app_context():
            db.session.add(user)
            db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/add_period', methods=['POST'])
def add_period():
    if 'username' in session:
        start_date = request.form['start_date']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        symptoms = request.form['symptoms']

        period = Period(start_date=start_date, start_time=start_time, end_time=end_time, symptoms=symptoms, user_id=session['user_id'])
        with app.app_context():
            db.session.add(period)
            db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
