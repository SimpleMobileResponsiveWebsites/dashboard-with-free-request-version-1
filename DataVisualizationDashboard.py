import streamlit as st
import pandas as pd
import requests
from io import StringIO


# Fetch the data from GitHub
@st.cache_data
def load_github_data(repo_url, file_path):
    """Fetches CSV data from a GitHub repository."""
    # Strip trailing and leading slashes to avoid malformed URLs
    repo_url = repo_url.rstrip("/")  # Remove trailing slashes
    file_path = file_path.lstrip("/")  # Ensure path is clean
    
    # Correctly build the full URL for accessing raw file
    url = f"{repo_url}/raw/main/{file_path}"

    try:
        # Fetch the data from the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise HTTP errors if failed
        return pd.read_csv(StringIO(response.text))  # Read CSV content
    except requests.exceptions.HTTPError as http_err:
        st.error(f"HTTP error occurred: {http_err} (Status code: {response.status_code})")
    except Exception as err:
        st.error(f"An unexpected error occurred: {err}")
    return None


# Load data from an uploaded file
@st.cache_data
def load_uploaded_data(uploaded_file):
    """Loads data from an uploaded file."""
    try:
        # Handle file formats
        file_extension = uploaded_file.name.split(".")[-1].lower()
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

    # Input fields for custom GitHub repo URL and file path
    custom_repo_url = st.sidebar.text_input(
        "Enter GitHub Repository URL", "https://github.com/"
    )
    custom_file_path = st.sidebar.text_input(
        "Enter File Path", "data/your-data.csv"
    )

    # Option to use custom GitHub repository data
    use_custom_github_data = st.sidebar.checkbox(
        "Fetch Data from Custom GitHub URL", value=False
    )

    # Upload file option
    st.sidebar.header("Upload Data")
    uploaded_file = st.sidebar.file_uploader(
        "Upload a file (CSV, JSON, XML, Excel):", type=["csv", "json", "xml", "xls", "xlsx"]
    )

    # Logic to load data
    github_data = None
    uploaded_data = None

    # If the user wants to fetch data from GitHub
    if use_custom_github_data:
        # Ensure proper repo_url structure without trailing slashes
        st.sidebar.text(f"Repo URL: {custom_repo_url}")
        st.sidebar.text(f"File Path: {custom_file_path}")
        github_data = load_github_data(custom_repo_url, custom_file_path)
        
        if github_data is not None:
            st.subheader("Custom GitHub Data Preview")
            st.dataframe(github_data)
        else:
            st.error("Failed to load data from the provided GitHub URL and file path.")
    
    # Handle uploaded data
    if uploaded_file is not None:
        uploaded_data = load_uploaded_data(uploaded_file)
        if uploaded_data is not None:
            st.subheader("Uploaded Data Preview")
            st.dataframe(uploaded_data)
        else:
            st.error("Failed to load uploaded file.")

    # Set the active dataset
    active_data = uploaded_data if uploaded_data is not None else github_data

    # If data is available, allow visualization
    if active_data is not None:
        st.subheader("Data Visualization")
        col1, col2 = st.columns(2)
        with col1:
            x_axis = st.selectbox("Select X-axis", active_data.columns, key="x_axis")
        with col2:
            y_axis = st.selectbox("Select Y-axis", active_data.columns, key="y_axis")

        if x_axis and y_axis:
            st.line_chart(active_data[[x_axis, y_axis]].set_index(x_axis))
    else:
        st.info("Please upload a file or use a valid GitHub repository link.")

# Run the application
if __name__ == "__main__":
    main()
