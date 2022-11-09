from flask import Flask,request, url_for, redirect, render_template, jsonify
import pandas as pd
import pickle
import numpy as np

app = Flask(__name__)

model = pickle.load(open('model.pkl', 'rb'))
cols = ['country','amount', '3D_secured', 'card', 'weekday', 'hour']

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/predict',methods=['POST'])
def predict():
    int_features = [x for x in request.form.values()]
    final = np.array(int_features)
    input_data = pd.DataFrame([final], columns = cols)    
    return render_template('home.html',pred='Best possible PSP is: {}'.format(model.predict(input_data)))

@app.route('/predict_api',methods=['POST'])
def predict_api():
    data = request.get_json(force=True)
    input_data = pd.DataFrame([data])
    output = model.predict(input_data)
    return jsonify(output)

if __name__ == '__main__':
    app.run(debug=True)
