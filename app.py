import os
import joblib
import pandas as pd
from flask import Flask, render_template, request, flash, redirect, url_for, jsonify # Added jsonify
import traceback

print("--- Script started ---")

# --- Initialize Flask App ---
app = Flask(__name__)
app.secret_key = os.urandom(24)
print("--- Flask app initialized ---")

# --- Predefined Climate Data ---
RAIN_DATA = {
    'Bayelsa': 2625, 'Cross River': 2599, 'Akwa Ibom': 2487, 'Abia': 2439,
    'Imo': 2345, 'Rivers': 2251, 'Ebonyi': 1963, 'Anambra': 1935,
    'Delta': 1871, 'Enugu': 1834, 'Ogun': 1626, 'Lagos': 1520,
    'FCT': 1481, 'Taraba': 1411, 'Ekiti': 1409, 'Ondo': 1383,
    'Oyo': 1328, 'Osun': 1309, 'Kaduna': 1309, 'Kwara': 1287,
    'Plateau': 1268, 'Kogi': 1229, 'Nasarawa': 1228, 'Benue': 1210,
    'Niger': 1196, 'Bauchi': 1111, 'Kano': 1000, 'Zamfara': 891,
    'Adamawa': 858, 'Yobe': 759, 'Jigawa': 758, 'Kebbi': 758,
    'Sokoto': 626, 'Borno': 562, 'Katsina': 559, 'Gombe': 314,
    'Abuja': 840, 'Edo': 2000 
}

TEMP_DATA = {
    'Abia': 25, 'Adamawa': 30, 'Akwa Ibom': 25, 'Anambra': 26,
    'Bauchi': 28, 'Bayelsa': 26, 'Benue': 27, 'Borno': 31,
    'Cross River': 26, 'Delta': 26, 'Ebonyi': 26, 'Edo': 25,
    'Ekiti': 23, 'Enugu': 26, 'Gombe': 30, 'Imo': 26,
    'Jigawa': 32, 'Kaduna': 29, 'Kano': 32, 'Katsina': 31,
    'Kebbi': 33, 'Kogi': 30, 'Kwara': 29, 'Lagos': 27,
    'Nasarawa': 28, 'Niger': 30, 'Ogun': 27, 'Ondo': 28,
    'Osun': 27, 'Oyo': 28, 'Plateau': 24, 'Rivers': 27,
    'Sokoto': 33, 'Taraba': 31, 'Yobe': 32, 'Zamfara': 33,
    'Abuja': 31
}

# --- Load the ML Model ---
MODEL_DIR = os.path.join(os.path.dirname(__file__), 'model')
MODEL_FILE_PATH = os.path.join(MODEL_DIR, 'crop_yield_model.pkl')
print(f"--- Attempting to load model from: {MODEL_FILE_PATH} ---")

loaded_model = None
known_crops = []
known_states = [] # This will be populated from your model

def load_model_and_categories():
    global loaded_model, known_crops, known_states
    print("--- Entering load_model_and_categories function ---")
    try:
        if os.path.exists(MODEL_FILE_PATH):
            loaded_model = joblib.load(MODEL_FILE_PATH)
            print(f"--- Model '{MODEL_FILE_PATH}' loaded successfully. ---")

            if hasattr(loaded_model, 'named_steps') and 'preprocessor' in loaded_model.named_steps:
                preprocessor = loaded_model.named_steps['preprocessor']
                if hasattr(preprocessor, 'named_transformers_') and 'cat' in preprocessor.named_transformers_:
                    encoder = preprocessor.named_transformers_['cat']
                    if len(encoder.categories_) > 0:
                        # Assuming 'Crop' is the first categorical feature
                        # and 'State' is the second. Adjust if necessary.
                        # For now, we will prioritize states from TEMP_DATA keys for the dropdown,
                        # but the model's known_states are still important for validation if they differ.
                        known_crops = list(encoder.categories_[0])
                        print(f"--- Known crops (from model): {known_crops} ---")
                    if len(encoder.categories_) > 1:
                        model_states = list(encoder.categories_[1])
                        print(f"--- Known states (from model): {model_states} ---")
                        # You might want to reconcile model_states with your RAIN_DATA/TEMP_DATA keys
                        # For the datalist, it's better to use states for which you have climate data.
                        # For validation, the model's known states are key.
                        global known_states # Ensure we are modifying the global
                        known_states = model_states # Store model's known states for validation
                else:
                    print("--- Error: 'cat' transformer not found. ---")
            else:
                print("--- Error: 'preprocessor' step not found or model not a pipeline. ---")
        else:
            print(f"--- Error: Model file '{MODEL_FILE_PATH}' NOT FOUND. ---")
    except Exception as e:
        print(f"--- CRITICAL ERROR loading model or extracting categories: {e} ---")
        traceback.print_exc()
        loaded_model = None
    print("--- Exiting load_model_and_categories function ---")

print("--- Calling load_model_and_categories ---")
load_model_and_categories()
print("--- Returned from load_model_and_categories ---")
if loaded_model:
    print("--- Model appears to be loaded. ---")
else:
    print("--- MODEL IS NOT LOADED. Check previous messages. ---")


# --- Flask Routes ---

@app.route('/get_climate_data/<state_name>')
def get_climate_data(state_name):
    rainfall = RAIN_DATA.get(state_name)
    temperature = TEMP_DATA.get(state_name)
    # It's good to check if the state_name is in your model's known_states too,
    # but for auto-fill, we prioritize RAIN_DATA and TEMP_DATA.
    # The main form validation will catch unsupported states for the model.
    return jsonify({'rainfall': rainfall, 'temperature': temperature})


@app.route('/', methods=['GET', 'POST'])
def index():
    print("--- Index route accessed ---")
    prediction_result = None
    form_data = request.form.to_dict() if request.method == 'POST' else {} # Use to_dict for easier handling

    current_year_for_template = pd.Timestamp.now().year

    # Use states from your climate data for the dropdown suggestions, ensure they are sorted.
    # This provides a better user experience for the auto-fill feature.
    # The model validation will still use `known_states` from the model itself.
    display_states = sorted(list(set(RAIN_DATA.keys()) | set(TEMP_DATA.keys())))


    if request.method == 'POST':
        if not loaded_model:
            flash("Model not loaded. Cannot make predictions.", "danger")
            return render_template('index.html', prediction=prediction_result, form_data=form_data,
                                   known_crops=known_crops, display_states=display_states,
                                   current_year=current_year_for_template)
        try:
            crop = form_data.get('crop', '').strip()
            state = form_data.get('state', '').strip()
            area_str = form_data.get('area', '0')
            year_str = form_data.get('year', str(current_year_for_template))
            rainfall_str = form_data.get('rainfall', '') # Get as string
            temperature_str = form_data.get('temperature', '') # Get as string

            errors = []
            if not crop: errors.append("Crop type is required.")
            if not state: errors.append("State/Region is required.")


            # If rainfall/temperature were auto-filled, they'll be present.
            # If not (e.g., JS disabled or state not in dicts), they might be empty.
            # The model requires these, so if they are empty, we could try to fetch them
            # or raise an error. For now, let's assume JS populates them.
            # If empty, validation below will catch it.

            try:
                area = float(area_str)
                if area < 0: errors.append("Farming Area must be non-negative.")
            except ValueError:
                errors.append("Invalid input for Farming Area. Please enter a number.")

            try:
                year = int(year_str)
                if not (1900 <= year <= 2100): errors.append("Year must be between 1900 and 2100.")
            except ValueError:
                errors.append("Invalid input for Year. Please enter a whole number.")

            # Validate Rainfall and Temperature (they are now expected to be filled)
            if not rainfall_str:
                errors.append("Rainfall is required. Select a state for auto-fill or enter manually.")
            else:
                try:
                    rainfall = float(rainfall_str)
                    if rainfall < 0: errors.append("Rainfall must be non-negative.")
                except ValueError:
                    errors.append("Invalid input for Rainfall. Please enter a number.")

            if not temperature_str:
                errors.append("Temperature is required. Select a state for auto-fill or enter manually.")
            else:
                try:
                    temperature = float(temperature_str)
                except ValueError:
                    errors.append("Invalid input for Temperature. Please enter a number.")


            # --- Model Specific Validation (Known Categories from the MODEL) ---
            if known_crops and crop and crop not in known_crops: # Check against model's known_crops
                errors.append(f"Crop '{crop}' is not supported by the model. Supported: {', '.join(known_crops)}")
            if known_states and state and state not in known_states: # Check against model's known_states
                errors.append(f"State '{state}' is not supported by the model or has inconsistent data. Supported by model: {', '.join(known_states)}")


            if errors:
                for error in errors:
                    flash(error, 'warning')
                return render_template('index.html', prediction=prediction_result, form_data=form_data,
                                       known_crops=known_crops, display_states=display_states,
                                       current_year=current_year_for_template)

            # --- Create DataFrame for Prediction ---
            input_data = pd.DataFrame([{
                'Crop': crop, 'State': state, 'Area': area, 'Year': year,
                'Rainfall_mm': rainfall, # This now comes from the form (auto-filled or manual)
                'Temperature_C': temperature # This now comes from the form
            }])

            prediction = loaded_model.predict(input_data)
            prediction_result = f"{prediction[0]:.2f} tons"
            flash(f"Predicted Crop Yield: {prediction_result}", "success")
            

        except Exception as e:
            print(f"An error occurred during prediction: {e}")
            flash(f"An error occurred during prediction: {str(e)}", "danger")
            traceback.print_exc()

    return render_template('index.html', prediction=prediction_result, form_data=form_data,
                           known_crops=known_crops, display_states=display_states,
                           current_year=current_year_for_template)

if __name__ == '__main__':
    print("--- Script is being run directly (inside __main__) ---")
    port = int(os.environ.get('PORT', 5000))
    print(f"--- Attempting to run app on host 0.0.0.0 and port {port} ---")
    try:
        app.run(host='0.0.0.0', port=port, debug=True)
    except Exception as e:
        print(f"--- CRITICAL ERROR during app.run: {e} ---")
        traceback.print_exc()
else:
    print("--- Script is being imported, not run directly. ---")

print("--- Script end (should not be reached if app.run is successful) ---")