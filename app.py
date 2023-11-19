from flask import Flask, request, jsonify
import mysql.connector
from flask_cors import CORS

import pickle

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecret'

scaler = pickle.load(open('scaler.pkl', 'rb'))
model = pickle.load(open('svm_model.pkl', 'rb'))

app = Flask(__name__, template_folder='templates')
CORS(app)

app.config['PROPAGATE_EXCEPTIONS'] = True

mysql_config = {
    'host': "frwahxxknm9kwy6c.cbetxkdyhwsb.us-east-1.rds.amazonaws.com",
    'user': "j6qbx3bgjysst4jr",
    'password': "mcbsdk2s27ldf37t",
    'database': "nkw2tiuvgv6ufu1z",
    'port': 3306,
}
mysql = mysql.connector.connect(**mysql_config)

@app.route('/', methods=['GET', 'POST'])
def home():
    prediction = -1
    if request.method == 'POST':
        data = request.json
        cursor = mysql.cursor()
        pregs = int(data.get('pregs'))
        gluc = int(data.get('gluc'))
        bp = int(data.get('bp'))
        skin = int(data.get('skin'))
        insulin = float(data.get('insulin'))
        bmi = float(data.get('bmi'))
        func = float(data.get('func'))
        age = int(data.get('age'))

        input_features = [[pregs, gluc, bp, skin, insulin, bmi, func, age]]
        # print(input_features)
        prediction = model.predict(scaler.transform(input_features))
        # print(prediction)

        prediction_value = prediction[0].item()

        insert_query = """
        INSERT INTO diabetes_patient_data (pregs, gluc, bp, skin, insulin, bmi, func, age, result)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        data = (pregs, gluc, bp, skin, insulin, bmi, func, age, prediction_value)

        cursor.execute(insert_query, data)
        mysql.commit()
        cursor.close()

        if prediction_value == 0:
            return jsonify(message='It is unlikely for the patient to have diabetes!', prediction_value=prediction_value)
        else:
            return jsonify(message='It is highly likely that the patient already has or will have diabetes!', prediction_value=prediction_value)
     
        
    return "Diabetes Disease Detection"

if __name__ == '__main__':
    app.run(debug=True)