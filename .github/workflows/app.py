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
