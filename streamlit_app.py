import requests
import streamlit as st
from neo4j_database import Neo4jDatabase  # Your Neo4j integration

# Streamlit sidebar for API key input
st.sidebar.title("API Settings")
API_KEY = st.sidebar.text_input("Enter your Hugging Face API Key:", type="password")

# Available models
MODEL_OPTIONS = {
    "ClinicalBERT": "emilyalsentzer/Bio_ClinicalBERT",
    "BioBERT": "dmis-lab/biobert-base-cased-v1.1",
    "BlueBERT": "bionlp/bluebert_pubmed_mimic_uncased_L-12_H-768_A-12",
    "PubMedBERT": "microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract"
}

# Select a model from the dropdown menu
selected_model = st.sidebar.selectbox("Select a model:", list(MODEL_OPTIONS.keys()))

# Function to query Hugging Face API
def get_disease_from_huggingface_api(symptom, model):
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    payload = {
        "inputs": symptom,
    }
    api_url = f"https://api-inference.huggingface.co/models/{model}"
    response = requests.post(api_url, headers=headers, json=payload)
    
    if response.status_code == 200:
        return response.json()  # Assuming the API returns JSON
    else:
        st.error(f"API request failed with status code: {response.status_code}")
        return None

# Streamlit app layout
st.title("Disease Symptom Finder")

# User input for symptom
symptom_input = st.text_input("Enter a symptom:")

# Search button
if st.button("Search"):
    if symptom_input:
        if API_KEY:
            # Query the graph database (as per your existing logic)
            results = db.get_disease_info(symptom_input)

            # If no result from the database, query the Hugging Face API
            if not results:
                api_results = get_disease_from_huggingface_api(symptom_input, MODEL_OPTIONS[selected_model])
                if api_results:
                    st.write("API Results:")
                    for item in api_results:
                        st.write(f"Disease: {item.get('disease', 'N/A')}")
                        st.write(f"Medicines: {', '.join(item.get('medicines', []))}")
                else:
                    st.write("No disease found for the given symptom.")
            else:
                for item in results:
                    st.write(f"Disease: {item['disease']}")
                    st.write(f"Medicines: {', '.join(item['medicines'])}")
        else:
            st.error("Please enter your Hugging Face API key in the sidebar.")
    else:
        st.error("Please enter a symptom.")

# Close the database connection on exit
db.close()
