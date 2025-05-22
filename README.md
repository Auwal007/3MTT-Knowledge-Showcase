# 🌾 Crop Yield Prediction – 3MTT Knowledge Showcase (May 2025 - Edition)


## **Project Creator**

**Name**: Muhammad Adam Isma'il

**3MTT ID**: FE/23/74562980

**3MTT Learning Track**: Data Science

**Cohort** 3

**Location**: Jos, Plateau State.


## Project Live Demo

https://harvestmaxai.up.railway.app/
---
This repository presents an AI-powered solution developed for the **3MTT Knowledge Showcase – May Edition**, under the **AI-Powered Solutions** category. It uses machine learning **(AI)** to **predict crop yields** based on key agricultural parameters, showcasing how AI can address **food insecurity in Nigeria** through improved planning, resource allocation, and farmer decision-making.

👉 **[Click here to try the deployed AI model](https://harvestmaxai.up.railway.app/)**


---

---

## 🌾 Project Description

This project implements a machine learning model to predict crop yield. It includes a trained model and a web application built with Flask to provide a user interface for making predictions.

The goal is to demonstrate the application of AI in agriculture for better planning, resource management, and increased farming efficiency.

---

## AI in Agriculture and Nigerian Food Security

Food insecurity is a significant challenge in Nigeria. Factors such as climate change, pests, diseases, and inefficient farming practices contribute to unpredictable and often low crop yields which negatively affect farmers and our National food security as whole.

Artificial Intelligence, particularly through tools like crop yield prediction models, offers a powerful approach to address these issues. By providing more accurate forecasts of how much food will be produced, AI enables:

- **Improved Planning**: Farmers, policymakers, and supply chain stakeholders can make better-informed decisions regarding planting, harvesting, storage, and distribution.  
- **Optimized Resource Allocation**: Understanding potential yields helps optimize the use of water, fertilizers, and pesticides.  
- **Early Warning Systems**: Predicting potential low yields allows for proactive measures to mitigate food shortages and stabilize prices.  
- **Enhanced Farmer Decision-Making**: Farmers can receive data-driven insights to choose the best crops, planting times, and techniques for their specific conditions.  

👉 **[Click here to try the deployed AI model on Streamlit](https://harvestmaxai.up.railway.app/)**


> ⚠️ **Note**: This is a demo project. A real-world robust crop yield prediction system would require significantly more detailed data, including:
> - Soil Data (type, nutrients)
> - More detailed local Weather and Climate Data (temperature, rainfall, humidity)
> - Agricultural Management Practices
> - Crop-Specific and Biological Factors
> - And many more data

This demo serves as a **proof-of-concept** for the valuable role AI can play in building a more food-secure future for Nigeria.

<!-- ---

## 🎯 3MTT Knowledge Showcase (May Edition) Context

- **Category**: AI-Powered Solutions  
- **Objective**: Build and showcase a project utilizing AI to solve a real-world problem  
- **Submission**: Hosted on GitHub. A demo video (link to be added) demonstrates the problem, solution, and AI in action. -->

---

## 📁 Files in this Repository


- **`app.py`**: Flask based backend web application for the prediction interface. 
- **`model`**: Directory that contains;
  - `crop yield.pkl`: Trained machine learning AI model file  
- **`Templetes`**: A directory containing the HTML files of the AI web App
- **`Static`**: A directory that contains the Javascript and CSS files of the AI APP
- **`requirements.txt`**: Python dependencies required to  run the program
- **`data/`**: Contains the scraped data and data acquisition script  
  - `data/script.py`: Python script to scrape data from [USDA IPAD](https://ipad.fas.usda.gov/)
  - `data/full_nigeria_crop_yield_data.csv`: The raw uncleaned scrapped data.
  -  `data/temp.csv`: The dataset which contains tempreture fata.
  -  `data/rainfall.csv`: The datase which contains rainfall data.

---

## 📊 Data Acquisition and Cleaning

- The Main Nigerian crop yield data was obtained by scraping publicly available information from the **USDA Foreign Agricultural Service (FAS) - IPAD**: [https://ipad.fas.usda.gov/](https://ipad.fas.usda.gov/)
- Then Rainfall and Temperature data Integrated from rainfall.csv and temp.csv, respectively. Gotten from weather agencies.

### Steps:
1. **Data Scraping**:
   - Used `selenium` to extract yield, area, and production data e.t.c.
2. **Data Loading**: Loading of crop yield, rainfall, and temperature datasets.
3. **Data Cleaning**:
   - Handled missing values (imputation/removal)
   - Converted data types (e.g., strings to floats/integers)
   - Resolved inconsistencies and formatting issues
   - Transformed/aggregated features for model input
   - And many other cleanings.
4. **Data Merging**: Combining crop yield data with corresponding rainfall and temperature data based on state.
5. **Feature Engineering**: Creation of new features.
6. **Model Training and Evaluation**: Using processed data to train a RandomForestRegressor and evaluate its performance.
---

## 🚀 How to Run the Flask Application

👉 **[Click here to try the deployed AI model on Streamlit](harvestmaxai.up.railway.app)**

If you prefer to run on you local computer, follow the below steps.

```bash
# Clone the repository
git clone https://github.com/Auwal007/3MTT-Knowledge-Showcase.git
cd 3MTT-Knowledge-Showcase

# Install dependencies
pip install -r requirements.txt

# Run the Flask app
python app.py
```
- Once the application starts, open your web browser and navigate to http://127.0.0.1:5000 (or the port indicated in your terminal).

---

**🔢 Data Required for Prediction**

The model requires the following inputs:

1. **Crop**: (Categorical) e.g., Corn, Rice, Wheat (selected from a dropdown)
2. **State**: (Categorical) Region or State (selected from a dropdown, auto-fills rainfall and temperature)
3. **Area**: (Numerical) Cultivated area (in hectares)
4. **Year**: (Numerical) Year for prediction
5. **Average Annual Rainfall (mm)**: (Numerical) Auto-filled based on state selection, but can be manually adjusted.
6. **Average Annual Temperature (°C)**: (Numerical) Auto-filled based on state selection, but can be manually adjusted

---

🙏 Acknowledgements

**3MTT Initiative**


Made with ❤️ to showcase how AI can drive sustainable agriculture and help combat food insecurity.
