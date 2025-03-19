import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from datetime import datetime
import hashlib

#costom css
st.markdown(
"""

 <style>
[data-testid="stSidebar"]{
    background: linear-gradient(135deg, #4CAF50, #FFEB3B);
   
}
[data-testid="stSidebarRadio"]{
    background-color:#061fab;
    color:white;
}
    /* Sidebar title */
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] h4 {
        color: white; /* Blue for headers */
    }

    [data-testid="stSidebar"] .css-16idsys,
    /* Sidebar radio button labels */
    [data-testid="stSidebar"].element-container label {
        color: white; /* Green for navigation text */
        font-weight: bold;
    }

    [data-testid="stSidebar"].element-container label:hover {
        color: orange; /* orange on hover */
        font-weight: bold;
    }

        /* Entire page background gradient */
    .stApp {
        background: linear-gradient(to right, #FFCC00, #06ab71);
        color: black;
    }


 </style>
""",
unsafe_allow_html=True
)



# Encrypt password
def encrypt_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Check credentials
def check_credentials(email, password):
    try:
        # Load all registrations
        df = pd.read_csv("registrations.csv")

        # Normalize emails to lower case to avoid mismatch due to case
        df['Email'] = df['Email'].str.strip().str.lower()
        email = email.strip().lower()

        # Find the matching email
        user_row = df[df['Email'] == email]

        # Debugging - check what rows are found
        # st.write("User row found:", user_row)

        if not user_row.empty:
            encrypted_input_password = encrypt_password(password)
            stored_password = user_row.iloc[0]['Encrypted Password']

            # Debugging - compare passwords
            # st.write("Encrypted input:", encrypted_input_password)
            # st.write("Stored password:", stored_password)

            if encrypted_input_password == stored_password:
                full_name = user_row.iloc[0]['Full Name']
                role = user_row.iloc[0]['Role']
                return True, full_name, role
            else:
                return False, None, None
        else:
            return False, None, None
    except FileNotFoundError:
        st.error("Registrations file not found.")
        return False, None, None


# Session state
if 'logged_in' not in st.session_state: 
    st.session_state.logged_in = False
    st.session_state.user_name = ""
    st.session_state.role = ""

# Sidebar Navigation
st.sidebar.image("ase_logo.jpg", width=200)
st.sidebar.title("Navigation")

# Conditional menu
if not st.session_state.logged_in:
    menu = st.sidebar.radio("Menu", ["Login", "Register"])
else:
    menu = st.sidebar.radio("Menu", ["Dashboard", "Logout"])

# REGISTRATION FORM
if menu == "Register":
    st.subheader("Register for ASE Dashboard")

    with st.form("registration_form", clear_on_submit=True):
        full_name = st.text_input("Full Name")
        email = st.text_input("Email Address")
        phone = st.text_input("Phone Number")
        organization = st.text_input("Organization (Optional)")
        role = st.selectbox("Role", ["Donor", "Volunteer", "Partner", "Community Member"])
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")

        submitted = st.form_submit_button("Register")

        if submitted:
            if not full_name or not email or not phone or not password:
                st.warning("Please fill in all required fields.")
            elif password != confirm_password:
                st.error("Passwords do not match.")
            else:
                encrypted_password = encrypt_password(password)

                user_data = {
                    "Full Name": full_name,
                    "Email": email,
                    "Phone": phone,
                    "Organization": organization,
                    "Role": role,
                    "Encrypted Password": encrypted_password,
                    "Registration Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }

                try:
                    df_existing = pd.read_csv("registrations.csv")
                    df_new = pd.DataFrame([user_data])
                    df_combined = pd.concat([df_existing, df_new], ignore_index=True)
                    df_combined.to_csv("registrations.csv", index=False)
                except FileNotFoundError:
                    df_new = pd.DataFrame([user_data])
                    df_new.to_csv("registrations.csv", index=False)

                st.success(f"Registration successful! You can now log in.")

# LOGIN FORM
if menu == "Login" and not st.session_state.logged_in:
    st.subheader("Login to ASE Dashboard")

    with st.form("login_form"):
        email = st.text_input("Email Address")
        password = st.text_input("Password", type="password")
        login_submit = st.form_submit_button("Login")

        if login_submit:
            success, name, role = check_credentials(email, password)
            if success:
                st.session_state.logged_in = True
                st.session_state.user_name = name
                st.session_state.role = role
                st.success(f"Welcome {name}! You are logged in as {role}.")
            else:
                st.error("Invalid email or password.")

# Sample data (Replace with your actual data)


# DASHBOARD ROLE-BASED VIEWS
if st.session_state.logged_in and menu == "Dashboard":
    st.subheader(f"Welcome, {st.session_state.user_name}!")
    st.write(f"You are logged in as **{st.session_state.role}**.")

    role = st.session_state.role

    # Donor Dashboard
    if role == "Donor":
        st.header("Donor Dashboard")
        st.info("Thank you for your contributions!")
        st.write("Here you can view donor reports, funding impact, and financial transparency.")
        # Add more donor-related content
        # You can add content or visuals for the donor reports here
        # Example donor data
        donor_data = {
        "Donor": ["Alice", "Bob", "Charlie"],
        "Amount": [500,1000, 1500], 
        "Project": ["Sunflower Farming", "Beekeeping", "Sunflower Farming"]
        }

        df = pd.DataFrame(donor_data)

        # Sample data (Replace with your actual data)
       

        # Display the donor report
        updates = [
        {"date": "2025-03-01", "update": "Successfully planted sunflowers on 5 acres."},
        {"date": "2025-03-10", "update": "Started beekeeping training for 30 women."}
        ]
        st.write("### Project Updates")
        data = {
        'Village': ['Hydom', 'Dongobesh', 'Mbulu'],
        'Farmers': [20, 15, 5],
        'Acres': [50, 30, 10],
        'Yield (kg)': [1500, 750, 300]
        }

        df = pd.DataFrame(data)

        for update in updates:
            st.write(f"**{update['date']}**: {update['update']}")
            #Displaying a bar chart
            st.subheader('Farmers Per Village')
            st.bar_chart(df.set_index('Village')['Farmers'])
            #Displaying a line chart for acres
            st.subheader('Acres Under Cultivation')
            st.line_chart(df.set_index('Village')['Acres'])
            #Displaying a pie chart for total yield
            st.subheader('Total Yield (kg)')
            fig, ax = plt.subplots()
            ax.pie(df['Yield (kg)'], labels=df['Village'], autopct='%1.1f%%')
            st.pyplot(fig)


        st.dataframe(df)

        



        st.subheader("Community Stories")
        # You can add content for community stories here
        stories = [
        {"name": "Jane Doe", "story": "The beekeeping project has transformed my life..."},
        {"name": "Mary Smith", "story": "With the sunflower farming project, I can now support my family..."}
        ]

        
        for story in stories:
            st.write(f"**{story['name']}**: {story['story']}")


        st.subheader("Impact Metrics")
        # You can add visualizations for impact metrics here
        # Example metrics
        metrics = {
        "Women Empowered": 200,
        "Acres Farmed": 30,
        "Briquettes Produced": 5000
        }

        # Display metrics
        for metric, value in metrics.items():
            st.write(f"**{metric}**: {value}")
        
        # Optional: Add a chart for visualizing impact
        fig, ax = plt.subplots()
        ax.bar(metrics.keys(), metrics.values())
        st.pyplot(fig)

    # Volunteer Dashboard
    elif role == "Volunteer":
        st.header("Volunteer Dashboard")
        st.info("Thanks for your dedication!")
        st.write("Access volunteer tasks, schedules, and community events here.")
        # Add volunteer-related content

    # Partner Dashboard
    elif role == "Partner":
        st.header("Partner Dashboard")
        st.info("Collaborating for greater impact!")
        st.write("View partnership opportunities, joint projects, and reports here.")
        # Add partner-related content

    # Community Member Dashboard
    elif role == "Community Member":
        st.header("Community Member Dashboard")
        st.info("Empowering our communities!")
        st.write("Explore community stories, learning materials, and resources.")
        # Add community member content

# LOGOUT
if st.session_state.logged_in and menu == "Logout":
    st.session_state.logged_in = False
    st.session_state.user_name = ""
    st.session_state.role = ""
    st.success("You have been logged out.")

def donor_dashboard():
    st.header("Donor Dashboard")
    st.info("Thank you for your contributions!")
    
    donor_menu = st.sidebar.selectbox("Donor Menu", ["Overview", "Donor Reports", "Impact Metrics"])
    
    if donor_menu == "Overview":
        st.subheader("Donor Overview")
        st.write("Here is your donor dashboard overview.")
        
    elif donor_menu == "Donor Reports":
        st.subheader("Your Donor Reports")
        st.write("Display donation reports here.")
        
    elif donor_menu == "Impact Metrics":
        st.subheader("Impact Metrics")
        st.write("Impact metrics graphs and analytics.")

def volunteer_dashboard():
    st.header("Volunteer Dashboard")
    volunteer_menu = st.sidebar.selectbox("Volunteer Menu", ["Overview", "Tasks", "Events"])
    
    if volunteer_menu == "Overview":
        st.subheader("Volunteer Overview")
        
    elif volunteer_menu == "Tasks":
        st.subheader("Volunteer Tasks")
        
    elif volunteer_menu == "Events":
        st.subheader("Community Events")

def partner_dashboard():
    st.header("Partner Dashboard")
    st.write("Welcome, Partner! Collaborate with us here.")

def community_dashboard():
    st.header("Community Member Dashboard")
    st.write("Explore community stories and updates.")

