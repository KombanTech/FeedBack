from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
import bcrypt

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a random secret key

# MySQL configuration
db_config = {
    'host': 'localhost',
    'user': 'root',  # Replace with your MySQL username
    'password': 'komban',  # Replace with your MySQL password
    'database': 'feedback_db'
}

# Home route
@app.route('/')
def home():
    return render_template('index.html')

# Student feedback form
@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        data = {
            'reg_number': request.form['regNumber'],
            'student_name': request.form['studentName'],
            'department': request.form['department'],
            'semester': request.form['semester'],
            'subject': request.form['subject'],
            'cat_exam': request.form['cat'],
            'course_content': request.form['q1'],
            'instructor_rating': request.form['q2'],
            'material_helpfulness': request.form['q3'],
            'recommendation': request.form['q4'],
            'overall_experience': request.form['q5'],
        }

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        cursor.execute('''INSERT INTO feedback (reg_number, student_name, department, semester, subject, cat_exam,
                                                  course_content, instructor_rating, material_helpfulness,
                                                  recommendation, overall_experience)
                          VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                       (data['reg_number'], data['student_name'], data['department'], data['semester'],
                        data['subject'], data['cat_exam'], data['course_content'], data['instructor_rating'],
                        data['material_helpfulness'], data['recommendation'], data['overall_experience']))

        conn.commit()
        cursor.close()
        conn.close()

    #    flash('Feedback submitted successfully!', 'success')
        return redirect(url_for('home'))

    return render_template('feedback.html')

# Admin login
@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        staff_id = request.form['staff_id']
        password = request.form['password']

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute('SELECT password FROM admin_login WHERE staff_id = %s', (staff_id,))
        result = cursor.fetchone()

        if result:
            stored_password_hash = result[0]
            if bcrypt.checkpw(password.encode('utf-8'), stored_password_hash.encode('utf-8')):
                session['logged_in'] = True
               # flash("Logged in successfully!", 'success')
                return redirect(url_for('admin_dashboard'))

        flash("Invalid credentials, please try again.", 'danger')
        return redirect(url_for('admin_login'))

    return render_template('admin_login.html')

# Admin dashboard
@app.route('/admin', methods=['GET', 'POST'])
def admin_dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('admin_login'))

    search_query = request.args.get('search')
    filter_by = request.args.get('filter')

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    if search_query and filter_by:
        query = f"SELECT * FROM feedback WHERE {filter_by} LIKE %s"
        cursor.execute(query, ('%' + search_query + '%',))
    else:
        cursor.execute('SELECT * FROM feedback')

    feedbacks = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('admin_dashboard.html', feedbacks=feedbacks)

# Create admin
@app.route('/create_admin', methods=['POST'])
def create_admin():
    staff_id = request.form['staff_id']
    password = request.form['password']

    if not staff_id or not password:
        #flash('Staff ID and Password are required!', 'danger')
        return redirect(url_for('admin_dashboard'))

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Check if the staff ID already exists
    cursor.execute('SELECT * FROM admin_login WHERE staff_id = %s', (staff_id,))
    if cursor.fetchone():
        #flash('Staff ID already exists!', 'danger')
        cursor.close()
        conn.close()
        return redirect(url_for('admin_dashboard'))

    # Create a new admin
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    cursor.execute('INSERT INTO admin_login (staff_id, password) VALUES (%s, %s)', (staff_id, hashed_password))
    conn.commit()
    cursor.close()
    conn.close()

   # flash('Admin created successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

# Delete feedback
@app.route('/delete_feedback', methods=['POST'])
def delete_feedback():
    feedback_id = request.form.get('feedback_id')

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM feedback WHERE id = %s', (feedback_id,))
    conn.commit()
    cursor.close()
    conn.close()

   # flash('Feedback deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

# Logout
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('logged_in', None)
    #flash('Logged out successfully!', 'success')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
