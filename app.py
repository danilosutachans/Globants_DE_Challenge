from flask import Flask, request, jsonify
from models import db, Department, Job, Employee
import pandas as pd
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db'
db.init_app(app)

@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    file = request.files['file']
    table_name = request.form['table']
    df = pd.read_csv(file)
    
    if table_name == 'departments':
        df.to_sql('department', con=db.engine, if_exists='append', index=False)
    elif table_name == 'jobs':
        df.to_sql('job', con=db.engine, if_exists='append', index=False)
    elif table_name == 'employees':
        df['hire_date'] = pd.to_datetime(df['datetime'])
        df.drop(columns=['datetime'], inplace=True)
        df.to_sql('employee', con=db.engine, if_exists='append', index=False)
    
    return jsonify({"message": "Data uploaded successfully"}), 201

@app.route('/batch_insert', methods=['POST'])
def batch_insert():
    data = request.get_json()
    table_name = data['table']
    rows = data['rows']
    
    if table_name == 'departments':
        db.session.bulk_insert_mappings(Department, rows)
    elif table_name == 'jobs':
        db.session.bulk_insert_mappings(Job, rows)
    elif table_name == 'employees':
        for row in rows:
            row['hire_date'] = datetime.strptime(row['hire_date'], '%Y-%m-%dT%H:%M:%SZ')
        db.session.bulk_insert_mappings(Employee, rows)
    
    db.session.commit()
    return jsonify({"message": "Batch insert successful"}), 201

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

@app.route('/metrics/hired_per_quarter', methods=['GET'])
def hired_per_quarter():
    query = """
    SELECT d.name as department, j.title as job,
           SUM(CASE WHEN strftime('%m', e.hire_date) BETWEEN '01' AND '03' THEN 1 ELSE 0 END) as Q1,
           SUM(CASE WHEN strftime('%m', e.hire_date) BETWEEN '04' AND '06' THEN 1 ELSE 0 END) as Q2,
           SUM(CASE WHEN strftime('%m', e.hire_date) BETWEEN '07' AND '09' THEN 1 ELSE 0 END) as Q3,
           SUM(CASE WHEN strftime('%m', e.hire_date) BETWEEN '10' AND '12' THEN 1 ELSE 0 END) as Q4
    FROM employee e
    JOIN department d ON e.department_id = d.id
    JOIN job j ON e.job_id = j.id
    WHERE strftime('%Y', e.hire_date) = '2021'
    GROUP BY d.name, j.title
    ORDER BY d.name, j.title
    """
    result = db.session.execute(query).fetchall()
    return jsonify([dict(row) for row in result])

@app.route('/metrics/departments_above_mean', methods=['GET'])
def departments_above_mean():
    query = """
    WITH hires_per_department AS (
        SELECT d.id, d.name, COUNT(e.id) as hired
        FROM employee e
        JOIN department d ON e.department_id = d.id
        WHERE strftime('%Y', e.hire_date) = '2021'
        GROUP BY d.id, d.name
    ),
    mean_hires AS (
        SELECT AVG(hired) as mean_hired
        FROM hires_per_department
    )
    SELECT hpd.id, hpd.name as department, hpd.hired
    FROM hires_per_department hpd, mean_hires mh
    WHERE hpd.hired > mh.mean_hired
    ORDER BY hpd.hired DESC
    """
    result = db.session.execute(query).fetchall()
    return jsonify([dict(row) for row in result])
