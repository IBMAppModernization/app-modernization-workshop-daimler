# -*- coding: utf-8 -*-
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import json
import os
import requests
from dotenv import load_dotenv
from flask import Flask, request, session, render_template, flash

app = Flask(__name__)

app.config.update(dict(
    DEBUG=True,
    SECRET_KEY=os.environ.get('SECRET_KEY', 'development key')
))

strings = {
    "gender": ['Female', 'Male'],
    "Partner": ['Yes', 'No'],
    "Dependents": ['No', 'Yes'],
    "PhoneService": ['No', 'Yes'],
    "MultipleLines": ['No phone service', 'No', 'Yes'],
    "InternetService": ['DSL', 'Fiber optic', 'No'],
    "OnlineSecurity": ['No', 'Yes', 'No internet service'],
    "OnlineBackup": ['Yes', 'No', 'No internet service'],
    "DeviceProtection": ['No', 'Yes', 'No internet service'],
    "TechSupport": ['No', 'Yes', 'No internet service'],
    "StreamingTV": ['No', 'Yes', 'No internet service'],
    "StreamingMovies": ['No', 'Yes', 'No internet service'],
    "Contract": ['Month-to-month', 'One year', 'Two year'],
    "PaperlessBilling": ['Yes', 'No'],
    "PaymentMethod": ['Electronic check',
                      'Mailed check',
                      'Bank transfer (automatic)',
                      'Credit card (automatic)']
}

# min, max, default value
floats = {
    "MonthlyCharges": [0, 1000, 100],
    "TotalCharges": [0, 50000, 1000]
}

# min, max, default value
ints = {
    "SeniorCitizen": [0, 1, 0],
    "tenure": [0, 100, 2]
}


def generate_input_lines():
    result = f'<table>'

    counter = 0
    for k in floats.keys():
        minn, maxx, vall = floats[k]
        if (counter % 2 == 0):
            result += f'<tr>'
        result += f'<td>{k}'
        result += f'<input type="number" class="form-control" min="{minn}" max="{maxx}" step="1" name="{k}" id="{k}" value="{vall}" required (this.value)">'
        result += f'</td>'
        if (counter % 2 == 1):
            result += f'</tr>'
        counter = counter + 1

    counter = 0
    for k in ints.keys():
        minn, maxx, vall = ints[k]
        if (counter % 2 == 0):
            result += f'<tr>'
        result += f'<td>{k}'
        result += f'<input type="number" class="form-control" min="{minn}" max="{maxx}" step="1" name="{k}" id="{k}" value="{vall}" required (this.value)">'
        result += f'</td>'
        if (counter % 2 == 1):
            result += f'</tr>'
        counter = counter + 1

    counter = 0
    for k in strings.keys():
        if (counter % 2 == 0):
            result += f'<tr>'
        result += f'<td>{k}'
        result += f'<select class="form-control" name="{k}">'
        for value in strings[k]:
            result += f'<option value="{value}" selected>{value}</option>'
        result += f'</select>'
        result += f'</td>'
        if (counter % 2 == 1):
            result += f'</tr>'
        counter = counter + 1

    result += f'</table>'

    return result


app.jinja_env.globals.update(generate_input_lines=generate_input_lines)


class churnForm():

    @app.route('/', methods=['GET', 'POST'])
    def index():

        if request.method == 'POST':
            ID = 999

            session['ID'] = ID
            data = {}

            for k, v in request.form.items():
                data[k] = v
                session[k] = v

            scoring_href = os.environ.get('URL')
            mltoken = os.environ.get('TOKEN')

            if not (scoring_href and mltoken):
                raise EnvironmentError('Env vars URL and TOKEN are required.')

            data = {"fields": ["gender","SeniorCitizen","Partner","Dependents","tenure","PhoneService","MultipleLines","InternetService","OnlineSecurity","OnlineBackup","DeviceProtection","TechSupport","StreamingTV","StreamingMovies","Contract","PaperlessBilling","PaymentMethod","MonthlyCharges","TotalCharges"],"values": [["Female",0,"No","No",1,"No","No phone service","DSL","No","No","No","No","No","No","Month-to-month","No","Bank transfer (automatic)",25.25,25.25]]}
            payload_scoring = {"input_data": [data]}
            #payload_scoring = {"args": {"input_data": [data]}}
            print("Payload is: ")
            print(payload_scoring)
            header_online = {
                'Cache-Control': 'no-cache',
                'Content-Type': 'application/json',
                'Authorization': 'Bearer' + mltoken}
            print(header_online)
            response_scoring = requests.post(
                scoring_href,
                verify=False,
                json=payload_scoring,
                headers=header_online)
            result = response_scoring.text
            print("Result is ", result)
            result_json = json.loads(result)
            print(result_json)
            #churn_risk = result_json["result"]["predictions"][0].lower()

            churn_risk = result_json["predictions"]["values"][0]
            print(churn_risk)
            #no_percent = result_json["result"]["probabilities"][0][0] * 100
            #no_percent = result_json["probabilities"][0][0] * 100
            #yes_percent = result_json["result"]["probabilities"][0][1] * 100
            #yes_percent = result_json["probabilities"][0][1] * 100
            no_percent = 50
            yes_percent = 20
            flash('Percentage of this customer leaving is: %.0f%%'
                  % yes_percent)
            return render_template(
                'score.html',
                result=result_json,
                churn_risk=churn_risk,
                yes_percent=yes_percent,
                no_percent=no_percent,
                response_scoring=response_scoring)

        else:
            return render_template('input.html')


load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
port = os.environ.get('PORT', '5000')
host = os.environ.get('HOST', '0.0.0.0')
if __name__ == "__main__":
    app.run(host=host, port=int(port))
