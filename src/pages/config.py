import streamlit as st
from utils.db_api import DBAPI, DB_Configuration

# Initialize Streamlit app
st.title("SQL Server Database Configuration")

if "session_list" not in st.session_state:
    st.session_state.session_list = [1]

with st.sidebar:

    option = st.selectbox(
        "Select Chat",
        st.session_state.session_list,
        index=0,
        placeholder="Select chat..."
    )

    for chat in st.session_state.session_list:
        st.write(f"Chat {chat}")


current_tab = option

# 메인 영역에 현재 선택된 채팅 표시
st.write(f"Current Chat: {current_tab}")


# Initialize session state for database configurations
if f"db_api_{current_tab}" not in st.session_state:
    st.session_state[f"db_api_{current_tab}"] = DBAPI()
db_api = st.session_state[f"db_api_{current_tab}"]

# Input fields for a new database configuration
hostname = st.text_input("Hostname", value="localhost", key="hostname")
port = st.text_input("Port", value=1433, key="port")
username = st.text_input("Username", value="sa", key="username")
password = st.text_input("Password", value="dockerStrongPwd123",type="password", key="password")
database_name = st.text_input("Database Name", value="school", key="database_name")

driver_options = ["ODBC Driver 18 for SQL Server", "ODBC Driver 17 for SQL Server"]
driver = st.selectbox("ODBC Driver", driver_options, key="driver")


# Add new configuration button
if st.button("Add Configuration"):
    db_info = DB_Configuration(
        hostname=hostname,
        port=port,
        username=username,
        password=password,
        database_name=database_name,
        driver=driver,
    )
    db_api.add_configuration(db_info)
    st.toast("Configuration added successfully!")

# Display current configurations
st.write("Current Configurations:")
for idx, db_info in db_api.get_configurations():
    with st.expander(f"Configuration {idx+1}"):
        config_dict = db_info.to_dict()
        config_table = f"""
        | Key            | Value         |
        |----------------|---------------|
        | Hostname       | {config_dict['hostname']} |
        | Port           | {config_dict['port']} |
        | Username       | {config_dict['username']} |
        | Database Name  | {config_dict['database_name']} |
        | Driver         | {config_dict['driver']} |
        """
        st.markdown(config_table, unsafe_allow_html=True)

        if st.button(f"Connect this configuration {idx+1}"):

            response = db_api.test_connection(idx)

            if response["result"]:
                # st.success(
                #     f"Connected to SQL Server successfully for configuration {idx+1}!"
                # )
                st.toast(
                    f"Connected to SQL Server successfully for configuration {idx+1}!",
                    icon="😍",
                )

                db_info = DB_Configuration(
                    hostname=config_dict['hostname'],
                    port=config_dict['port'],
                    username=config_dict['username'],
                    password=config_dict['password'],
                    database_name=config_dict['database_name'],
                    driver=config_dict['driver'],
                )
                db_api.add_configuration(db_info)
                st.toast("Configuration added successfully!")

            else:
                # st.error(
                #     f"Failed to connect to SQL Server for configuration {idx+1}: {response['error']}"
                # )
                st.toast(
                    f"Failed to connect to SQL Server for configuration {idx+1}: {response['error']}",
                    icon="🥲",
                )

        # Option to test connection for each configuration
        if st.button(f"Test Connection {idx+1}"):
            response = db_api.test_connection(idx)
            if response["result"]:
                # st.success(
                #     f"Connected to SQL Server successfully for configuration {idx+1}!"
                # )
                st.toast(
                    f"Connected to SQL Server successfully for configuration {idx+1}!",
                    icon="😍",
                )
            else:
                # st.error(
                #     f"Failed to connect to SQL Server for configuration {idx+1}: {response['error']}"
                # )
                st.toast(
                    f"Failed to connect to SQL Server for configuration {idx+1}: {response['error']}",
                    icon="🥲",
                )

        # Option to delete each configuration
        if st.button(f"Delete Configuration {idx+1}"):
            db_api.delete_configuration(idx)
            st.success(f"Configuration {idx+1} deleted successfully!")
            st.rerun()
