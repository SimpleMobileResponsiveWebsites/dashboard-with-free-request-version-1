import streamlit as st
import pandas as pd
import requests

# Set the GitHub repository URL and file path
repo_url = "https://github.com/your-username/your-repo"
file_path = "data/your-data.csv"

# Fetch the data from the GitHub repository
@st.cache_data
def load_github_data(url):
    response = requests.get(url)
    response.raise_for_status()
    return pd.read_csv(response.content)

github_data = load_github_data(f"{repo_url}/raw/main/{file_path}")

# Sidebar for data upload
st.sidebar.header("Upload Data")
uploaded_file = st.sidebar.file_uploader(
    "Upload a file (CSV, JSON, XML, etc.):",
    type=None
)

# Main interface
st.title("Data Visualization Dashboard")

if uploaded_file is not None:
    file_extension = uploaded_file.name.split('.')[-1].lower()
    try:
        if file_extension == "csv":
            uploaded_data = pd.read_csv(uploaded_file)
        elif file_extension == "json":
            uploaded_data = pd.read_json(uploaded_file)
        elif file_extension == "xml":
            uploaded_data = pd.read_xml(uploaded_file)
        else:
            uploaded_data = pd.read_excel(uploaded_file)
        st.write("Uploaded Data Preview:")
        st.dataframe(uploaded_data)
    except Exception as e:
        st.error(f"Error loading file: {e}")
        uploaded_data = None
else:
    uploaded_data = None

# Allow user to select columns and rows
if uploaded_data is not None:
    col1, col2 = st.columns(2)
    with col1:
        x_axis = st.selectbox("Select X-axis", uploaded_data.columns)
    with col2:
        y_axis = st.selectbox("Select Y-axis", uploaded_data.columns)

    # Display the data based on user selection
    st.subheader("Data Visualization")
    st.line_chart(uploaded_data, x=x_axis, y=y_axis)

# Display the default GitHub data
st.subheader("Default GitHub Data")
st.dataframe(github_data)
