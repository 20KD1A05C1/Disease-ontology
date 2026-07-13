import os
import re
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
        MATCH (d:Disease)-[:HAS_SYMPTOM]->(s:Symptom)
        WHERE toLower(s.name) = toLower($symptom)
        OPTIONAL MATCH (d)-[:TREATED_BY]->(m:Medicine)
        RETURN d.name AS disease, COLLECT(m.name) AS medicines
        """
        with self.driver.session() as session:
            result = session.run(query, symptom=symptom)
            return [{"disease": record["disease"], "medicines": record["medicines"]} for record in result]

def get_secret(section, key, default=""):
    try:
        return st.secrets[section][key]
    except Exception:
        return os.getenv(f"{section.upper()}_{key.upper()}", default)


def parse_symptoms(symptom_input):
    if not symptom_input:
        return []
    return [item.strip().lower() for item in re.split(r"[,;]+", symptom_input) if item.strip()]


def search_symptoms(db, symptoms):
    results = []
    for symptom in symptoms:
        results.append((symptom, db.get_disease_info(symptom)))
    return results


def main():
    # Streamlit app layout
    st.title("Disease Ontology: Symptom to Disease Finder")

    # Taking Neo4j credentials from Streamlit secrets or environment variables
    uri = get_secret("neo4j", "uri")
    username = get_secret("neo4j", "username")
    password = get_secret("neo4j", "password")

    if not uri:
        st.error("Missing Neo4j URI. Set it in Streamlit secrets or as NEO4J_URI.")
        st.stop()

    db = None
    try:
        # Initialize Neo4j connection
        db = Neo4jDatabase(uri, username, password)

        # User input for symptoms
        symptom_input = st.text_input("Enter one or more symptoms (separated by commas):")

        if st.button("Search"):
            if symptom_input:
                symptoms = parse_symptoms(symptom_input)
                if not symptoms:
                    st.write("Please enter at least one valid symptom.")
                else:
                    results_by_symptom = search_symptoms(db, symptoms)
                    for symptom, results in results_by_symptom:
                        st.subheader(f"Results for '{symptom}'")
                        if results:
                            for item in results:
                                st.write(f"Disease: {item['disease']}")
                                st.write(f"Medicines: {', '.join(item['medicines']) if item['medicines'] else 'No medicines available'}")
                        else:
                            st.write("No disease found for this symptom.")
            else:
                st.write("Please enter a symptom.")
    finally:
        if db is not None:
            db.close()


if __name__ == "__main__":
    main()
