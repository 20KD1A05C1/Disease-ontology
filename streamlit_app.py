import streamlit as st
from neo4j import GraphDatabase

# Neo4j connection setup
class Neo4jDatabase:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        if self.driver:
            self.driver.close()

    def get_disease_info(self, symptom):
        query = """
        MATCH (s:Symptom {name: $symptom})-[:INDICATES]->(d:Disease)
        OPTIONAL MATCH (d)-[:TREATED_BY]->(m:Medicine)
        RETURN d.name AS disease, COLLECT(m.name) AS medicines
        """
        with self.driver.session() as session:
            result = session.run(query, symptom=symptom)
            return [{"disease": record["disease"], "medicines": record["medicines"]} for record in result]

# Streamlit app layout
st.title("Disease Ontology: Symptom to Disease Finder")

# Taking Neo4j credentials from Streamlit secrets
uri = st.secrets["neo4j"]["uri"]
username = st.secrets["neo4j"]["username"]
password = st.secrets["neo4j"]["password"]

# Initialize Neo4j connection
db = Neo4jDatabase(uri, username, password)

# User input for symptoms
symptom_input = st.text_input("Enter a symptom:")

if st.button("Search"):
    if symptom_input:
        # Query the Neo4j database
        symptom_input =symptom_input.lower()
        results = db.get_disease_info(symptom_input)
        
        if results:
            st.write(f"Diseases related to '{symptom_input}':")
            for item in results:
                st.write(f"Disease: {item['disease']}")
                st.write(f"Medicines: {', '.join(item['medicines']) if item['medicines'] else 'No medicines available'}")
        else:
            st.write("No disease found for the given symptom.")
    else:
        st.write("Please enter a symptom.")

# Close the Neo4j connection
db.close()
