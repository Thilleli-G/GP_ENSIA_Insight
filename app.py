import subprocess
from flask import Flask, flash, render_template, request, jsonify, session, redirect, url_for
from sklearn.ensemble import RandomForestRegressor
from sklearn.neighbors import NearestNeighbors
import joblib
import numpy as np
import pandas as pd
import shap
from flask import Flask, flash, render_template, request, jsonify, session
import random
from firebase_admin import credentials, auth
import sendgrid
from sendgrid.helpers.mail import Mail
from flask import Flask, request, render_template, redirect, url_for
import bcrypt
import os

if os.getenv("CUSTOM_BUILD_SCRIPT"):
    subprocess.call(["bash", os.getenv("CUSTOM_BUILD_SCRIPT")])
    
# Load the pre-trained models and feature names
rf_regressor = joblib.load('rf_regressor_model.pkl')
knn_model = joblib.load('knn_model.joblib')
feature_names = joblib.load('feature_names.pkl')

app = Flask(__name__)
app.secret_key = os.urandom(24).hex()


# Define function to process form data and make predictions
def process_form_data(form_data):
    # Convert form data to DataFrame
    new_instance = pd.DataFrame(form_data, index=[0])

    # Predict target variables using Random Forest regressor
    predicted_results = rf_regressor.predict(new_instance)

    # Get SHAP values for the "average" target variable only
    explainer = shap.Explainer(rf_regressor, pd.DataFrame(new_instance, columns=feature_names))
    shap_values = explainer.shap_values(pd.DataFrame(new_instance, columns=feature_names))
    average_index = list(new_instance.columns).index("Average")
    shap_values_average = shap_values[average_index]
    average_shap_values = np.mean(np.abs(shap_values_average), axis=0)
    top_three_indices = np.argsort(average_shap_values)[::-1][:3]

    # Predict nearest neighbors' averages using KNN model
    nearest_neighbors_avg = find_nearest_neighbors_average(new_instance.values)

    # Categorize overall performance based on predicted average
    overall_performance = categorize_performance(predicted_results[0, average_index])

    return predicted_results, top_three_indices, nearest_neighbors_avg, overall_performance

# Define function to categorize overall performance
def categorize_performance(average_value):
    if 10 <= average_value < 12:
        return "Moderate"
    elif 12 <= average_value < 15:
        return "Good"
    elif average_value >= 15:
        return "Strong"

# Define function to find nearest neighbors' averages
def find_nearest_neighbors_average(new_instance):
    distances, indices = knn_model.kneighbors(new_instance)
    nearest_neighbor_indices = indices[0]
    nearest_neighbors_average = target_variables.iloc[nearest_neighbor_indices, :]['Average'].tolist()
    return nearest_neighbors_average

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    email = request.form['email']
    if email.endswith('@ensia.edu.dz'):
        # Extract surname and name from the email
        parts = email.split('@')[0].split('.')
        surname, name = parts[0], parts[1]

        # Save details in session
        session['email'] = email
        session['name'] = name.upper()  
        session['surname'] = surname.upper() 

        # Redirect to the form
        return redirect(url_for('form'))
    else:
        flash('You should use your ENSIA email. Please try again.')
        return redirect(url_for('index'))

@app.route('/form')
def form():
    return render_template('form.html')

@app.route('/results', methods=['POST'])
def results():
    form_data = request.form.to_dict()

    # Process form data and make predictions
    predicted_results, top_three_indices, nearest_neighbors_avg, overall_performance = process_form_data(form_data)
# Generate recommendations based on the three most influential features
    recommendations = generate_recommendations(top_three_indices)
    
    def generate_recommendations(top_three_indices):
       recommendations = {}
    # Map feature indices to recommendations
    recommendations_mapping = {
    2: "Try to study in a different environment.",
    3: "Try to study within groups to share ideas.",
    4: "Use a planner or schedule to organize your study sessions and tasks.",
    5: "Identify and address any challenges or obstacles in your academic journey.",
    13: "Ensure that your learning experience meets your expectations and needs.",
    14: "Explore extracurricular activities that align with your interests and goals.",
    15: "Maintain a high level of motivation and dedication to your academic pursuits.",
    16: "Continue to explore and develop your interest in the field of Artificial Intelligence.",
    17: "Seek constructive feedback from others to enhance your learning and development.",
    18: "Prioritize sufficient sleep to support cognitive function and overall well-being.",
    19: "Adopt effective stress management techniques to cope with academic challenges.",
    20: "Continue to improve your English proficiency for academic and professional success.",
    21: "Enhance your programming skills through practice and learning opportunities.",
    22: "Deepen your understanding of computer science principles and concepts.",
    23: "Strengthen your mathematical abilities to excel in related coursework.",
    24: "Explore additional resources such as books to supplement your learning.",
    25: "Attend lectures regularly and actively engage with the course material.",
    26: "Utilize online documents for supplementary learning and reference purposes.",
    27: "Take advantage of online tutorials to enhance your understanding of course topics.",
    28: "Consider enrolling in private courses or workshops for specialized learning.",
    29: "Watch educational videos on platforms like YouTube to supplement your studies.",
    30: "Ensure adequate study hours to effectively cover course material and assignments."
}

    # Generate recommendations based on the three most influential features
    for index in top_three_indices:
        recommendations[index] = recommendations_mapping.get(index, "No recommendation available.")

    return recommendations

    return render_template('results.html', predicted_results=predicted_results, 
                           top_three_indices=top_three_indices, nearest_neighbors_avg=nearest_neighbors_avg,
                           overall_performance=overall_performance)
    

if __name__ == '__main__':
    app.run(debug=True)
