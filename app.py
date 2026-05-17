from flask import Flask, render_template, request, redirect, session, send_file
import sqlite3
import os
import pandas as pd
from config import Config
from utils.calculations import calculate_progress

app = Flask(__name__)
app.config.from_object(Config)


def get_db_connection():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    if not os.path.exists('database.db'):
        conn = get_db_connection()
        with open('schema.sql', 'r') as f:
            conn.executescript(f.read())
        conn.commit()
        conn.close()


init_db()


@app.route('/')
def home():
    return redirect('/login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM users WHERE username=? AND password=?',
            (username, password)
        ).fetchone()
        conn.close()

        if user:
            session['user_id'] = user['id']
            session['role'] = user['role']

            if user['role'] == 'employee':
                return redirect('/employee')
            elif user['role'] == 'manager':
                return redirect('/manager')
            elif user['role'] == 'admin':
                return redirect('/admin')

    return render_template('login.html')


@app.route('/employee')
def employee_dashboard():
    if session.get('role') != 'employee':
        return redirect('/login')

    conn = get_db_connection()
    goals = conn.execute(
        'SELECT * FROM goals WHERE user_id=?',
        (session['user_id'],)
    ).fetchall()
    conn.close()

    return render_template('employee_dashboard.html', goals=goals)


@app.route('/create_goal', methods=['GET', 'POST'])
def create_goal():
    if session.get('role') != 'employee':
        return redirect('/login')

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        uom = request.form['uom']
        target = request.form['target']
        weightage = int(request.form['weightage'])

        conn = get_db_connection()

        existing_goals = conn.execute(
            'SELECT * FROM goals WHERE user_id=?',
            (session['user_id'],)
        ).fetchall()

        if len(existing_goals) >= 8:
            conn.close()
            return "Maximum 8 goals allowed"

        total_weightage = sum(goal['weightage'] for goal in existing_goals)

        if weightage < 10:
            conn.close()
            return "Minimum weightage is 10%"

        if total_weightage + weightage > 100:
            conn.close()
            return "Total weightage cannot exceed 100%"

        conn.execute(
            '''
            INSERT INTO goals (user_id, title, description, uom, target, weightage)
            VALUES (?, ?, ?, ?, ?, ?)
            ''',
            (session['user_id'], title, description, uom, target, weightage)
        )

        conn.commit()
        conn.close()

        return redirect('/employee')

    return render_template('create_goal.html')


@app.route('/manager')
def manager_dashboard():
    if session.get('role') != 'manager':
        return redirect('/login')

    conn = get_db_connection()
    goals = conn.execute('SELECT * FROM goals').fetchall()
    conn.close()

    return render_template('manager_dashboard.html', goals=goals)


@app.route('/approve/<int:goal_id>', methods=['POST'])
def approve_goal(goal_id):
    if session.get('role') != 'manager':
        return redirect('/login')

    comment = request.form['comment']

    conn = get_db_connection()
    conn.execute(
        'UPDATE goals SET status=?, manager_comment=? WHERE id=?',
        ('Approved', comment, goal_id)
    )
    conn.commit()
    conn.close()

    return redirect('/manager')


@app.route('/reject/<int:goal_id>', methods=['POST'])
def reject_goal(goal_id):
    if session.get('role') != 'manager':
        return redirect('/login')

    comment = request.form['comment']

    conn = get_db_connection()
    conn.execute(
        'UPDATE goals SET status=?, manager_comment=? WHERE id=?',
        ('Rejected', comment, goal_id)
    )
    conn.commit()
    conn.close()

    return redirect('/manager')


@app.route('/quarterly_update/<int:goal_id>', methods=['GET', 'POST'])
def quarterly_update(goal_id):
    if session.get('role') != 'employee':
        return redirect('/login')

    if request.method == 'POST':
        quarter = request.form['quarter']
        achievement = float(request.form['achievement'])

        conn = get_db_connection()
        goal = conn.execute(
            'SELECT * FROM goals WHERE id=?',
            (goal_id,)
        ).fetchone()

        progress = calculate_progress(
            goal['target'],
            achievement,
            goal['uom']
        )

        conn.execute(
            '''
            INSERT INTO checkins (goal_id, quarter, achievement, progress)
            VALUES (?, ?, ?, ?)
            ''',
            (goal_id, quarter, achievement, progress)
        )

        conn.commit()
        conn.close()

        return redirect('/employee')

    return render_template('quarterly_update.html', goal_id=goal_id)


@app.route('/admin')
def admin_dashboard():
    if session.get('role') != 'admin':
        return redirect('/login')

    conn = get_db_connection()
    goals = conn.execute('SELECT * FROM goals').fetchall()
    conn.close()

    return render_template('admin_dashboard.html', goals=goals)


@app.route('/reports')
def reports():
    conn = get_db_connection()
    data = conn.execute('SELECT * FROM goals').fetchall()
    conn.close()

    df = pd.DataFrame(data)
    df.to_csv('report.csv', index=False)

    return send_file('report.csv', as_attachment=True)


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


if __name__ == '__main__':
    app.run(debug=True)