import streamlit as st
import pandas as pd
import requests
from io import StringIO

# Constants
GITHUB_REPO_URL = "https://github.com/your-username/your-repo"
DEFAULT_FILE_PATH = "data/your-data.csv"

# Fetch the data from GitHub
@st.cache_data
def load_github_data(repo_url, file_path):
    """Fetches CSV data from a GitHub repository."""
    url = f"{repo_url}/raw/main/{file_path}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return pd.read_csv(StringIO(response.text))
    except requests.exceptions.HTTPError as http_err:
        st.error(f"HTTP error occurred: {http_err} (Status code: {response.status_code})")
    except Exception as err:
        st.error(f"An error occurred: {err}")
    return None

# Load data from an uploaded file
@st.cache_data
def load_uploaded_data(uploaded_file):
    """Loads data from an uploaded file."""
    try:
        file_extension = uploaded_file.name.split('.')[-1].lower()
        if file_extension == "csv":
            return pd.read_csv(uploaded_file)
        elif file_extension == "json":
            return pd.read_json(uploaded_file)
        elif file_extension == "xml":
            return pd.read_xml(uploaded_file)
        elif file_extension in ["xls", "xlsx"]:
            return pd.read_excel(uploaded_file)
        else:
            st.error("Unsupported file format. Please upload CSV, JSON, XML, or Excel files.")
    except Exception as e:
        st.error(f"Error loading file: {e}")
    return None

# Main application
def main():
    st.title("Data Visualization Dashboard")

    # Sidebar for data selection
    st.sidebar.header("Data Source")
    use_github_data = st.sidebar.checkbox("Use Default GitHub Data", value=True)

    if use_github_data:
        st.sidebar.text(f"Repo URL: {GITHUB_REPO_URL}")
        st.sidebar.text(f"File Path: {DEFAULT_FILE_PATH}")
        github_data = load_github_data(GITHUB_REPO_URL, DEFAULT_FILE_PATH)
        if github_data is not None:
            st.subheader("Default GitHub Data Preview")
            st.dataframe(github_data)
    else:
        github_data = None

    # Upload file option
    st.sidebar.header("Upload Data")
    uploaded_file = st.sidebar.file_uploader("Upload a file (CSV, JSON, XML, Excel):", type=["csv", "json", "xml", "xls", "xlsx"])

    if uploaded_file is not None:
        uploaded_data = load_uploaded_data(uploaded_file)
        if uploaded_data is not None:
            st.subheader("Uploaded Data Preview")
            st.dataframe(uploaded_data)
        else:
            st.error("Failed to load uploaded file.")
    else:
        uploaded_data = None

    # Determine which dataset to use
    active_data = uploaded_data if uploaded_data is not None else github_data

    if active_data is not None:
        # Data selection for visualization
        st.subheader("Data Visualization")
        col1, col2 = st.columns(2)
        with col1:
            x_axis = st.selectbox("Select X-axis", active_data.columns, key="x_axis")
        with col2:
            y_axis = st.selectbox("Select Y-axis", active_data.columns, key="y_axis")

        # Render visualization
        if x_axis and y_axis:
            st.line_chart(active_data[[x_axis, y_axis]].set_index(x_axis))
    else:
        st.info("Please upload a file or use the default GitHub data.")

# Run the app
if __name__ == "__main__":
    main()
