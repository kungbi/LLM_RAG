import streamlit as st

# import pyodbc

# Initialize Streamlit app
st.title("SQL Server Database Configuration")


# Function to create a new database configuration
def create_new_config(hostname, port, username, password, database_name):
    return {
        "hostname": hostname,
        "port": port,
        "username": username,
        "password": password,
        "database_name": database_name,
    }


# Initialize session state for database configurations
if "db_configs" not in st.session_state:
    st.session_state.db_configs = []

# Input fields for a new database configuration
hostname = st.text_input("Hostname", key="hostname")
port = st.text_input("Port", value=1433, key="port")
username = st.text_input("Username", key="username")
password = st.text_input("Password", type="password", key="password")
database_name = st.text_input("Database Name", key="database_name")

# Add new configuration button
if st.button("Add Configuration"):
    new_config = create_new_config(hostname, port, username, password, database_name)
    st.session_state.db_configs.append(new_config)
    st.success("Configuration added successfully!")

# Display current configurations
st.write("Current Configurations:")
for idx, config in enumerate(st.session_state.db_configs):
    st.write(f"Configuration {idx+1}: {config}")

    # Option to test connection for each configuration
    if st.button(f"Test Connection {idx+1}"):
        connection_string = f"DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={config['hostname']},{config['port']};DATABASE={config['database_name']};UID={config['username']};PWD={config['password']};TrustServerCertificate=yes;"
        try:
            conn = pyodbc.connect(connection_string)
            st.success(
                f"Connected to SQL Server successfully for configuration {idx+1}!"
            )
        except Exception as e:
            st.error(f"Failed to connect to SQL Server for configuration {idx+1}: {e}")

    # Option to delete each configuration
    if st.button(f"Delete Configuration {idx+1}"):
        del st.session_state.db_configs[idx]
        st.success(f"Configuration {idx+1} deleted successfully!")
        st.experimental_rerun()  # Refresh the page to update the list
