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

# Sample data (Replace with your actual data)
data = {
    'Village': ['Hydom', 'Dongobesh', 'Mbulu'],
    'Farmers': [20, 15, 5],
    'Acres': [50, 30, 10],
    'Yield (kg)': [1500, 750, 300]
}

df = pd.DataFrame(data)


# Slideshow data
product_images = [
    {"file": "product1.png", "caption": "Sunflower Oil - Pure and Organic"},
    {"file": "product1.png", "caption": "Natural Beeswax Lotion"},
    {"file": "product1.png", "caption": "Handmade Soap Bars from Sunflower Oil"},
    {"file": "product1.png", "caption": "Eco-friendly Biomass Briquettes"}
]

# Initialize session state to keep track of the slide index
if 'slide_index'not in st.session_state:
    st.session_state.slide_index = 0

# Function to go to the previous slide
def previous_slide():
    if st.session_state.slide_index > 0:
        st.session_state.slide_index -= 1
    else:
        st.session_state.slide_index = len(product_images) - 1

# Function to go to the next slide
def next_slide():
    if st.session_state.slide_index < len(product_images) - 1:
        st.session_state.slide_index += 1
    else:
        st.session_state.slide_index = 0

# Title of the app
st.title('Bridge Gap Transparency')
st.header('Welcome to Bridge Gap Transparency—Connecting Impact with Integrity')

# Sidebar for navigation
st.sidebar.image("ase_logo.JPG", width=100)
st.sidebar.title("Navigation")
selection = st.sidebar.radio("Go to", ["Home", "Donor Reports", "Project Updates", "Community Stories", "Impact Metrics", "Register"])

if not st.session_state.logged_in:
    menu = st.sidebar.radio("Menu", ["Login", "Register"])
else:
    menu = st.sidebar.radio("Menu", ["Dashboard", "Logout"])




# Main content based on selection
if selection == "Donor Reports":
    st.subheader("Donor Reports")
    # You can add content or visuals for the donor reports here
    # Example donor data
    donor_data = {
    "Donor": ["Alice", "Bob", "Charlie"],
    "Amount": [500,1000, 1500], 
    "Project": ["Sunflower Farming", "Beekeeping", "Sunflower Farming"]
    }

    df = pd.DataFrame(donor_data)

    # Display the donor report
    st.dataframe(df)
    
elif selection == "Project Updates":
    #st.subheader("Project Updates")
    # You can add content for project updates here
    # Example updates
    updates = [
        {"date": "2025-03-01", "update": "Successfully planted sunflowers on 5 acres."},
        {"date": "2025-03-10", "update": "Started beekeeping training for 30 women."}
    ]

    st.write("### Project Updates")
    for update in updates:
        st.write(f"**{update['date']}**: {update['update']}")
    # Displaying a bar chart
    st.subheader('Farmers Per Village')
    st.bar_chart(df.set_index('Village')['Farmers'])
    # Displaying a line chart for acres
    st.subheader('Acres Under Cultivation')
    st.line_chart(df.set_index('Village')['Acres'])
    # Displaying a pie chart for total yield
    st.subheader('Total Yield (kg)')
    fig, ax = plt.subplots()
    ax.pie(df['Yield (kg)'], labels=df['Village'], autopct='%1.1f%%')
    st.pyplot(fig)
    

elif selection == "Community Stories":
    st.subheader("Community Stories")
    # You can add content for community stories here
    stories = [
    {"name": "Jane Doe", "story": "The beekeeping project has transformed my life..."},
    {"name": "Mary Smith", "story": "With the sunflower farming project, I can now support my family..."}
    ]

    
    for story in stories:
        st.write(f"**{story['name']}**: {story['story']}")

  
    
elif selection == "Impact Metrics":
    st.subheader("Impact Metrics")
    # You can add visualizations for impact metrics here
    # Example metrics
    metrics = {
    "Women Empowered": 200,
    "Acres Farmed": 30,
    "Briquettes Produced": 5000
    }

    # Display metrics
    st.write("### Impact Metrics")
    for metric, value in metrics.items():
        st.write(f"**{metric}**: {value}")
    
    # Optional: Add a chart for visualizing impact
    fig, ax = plt.subplots()
    ax.bar(metrics.keys(), metrics.values())
    st.pyplot(fig)


# Registration Form Section
if selection == "Register":
    st.subheader("Join Our ASE Community")

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
                # Save to CSV or Database (Here we save to CSV as an example)
                user_data = {
                    "Full Name": full_name,
                    "Email": email,
                    "Phone": phone,
                    "Organization": organization,
                    "Role": role,
                    "Password": password,
                    "Registration Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }

                # Save to CSV
                try:
                    df_existing = pd.read_csv("registrations.csv")
                    df_new = pd.DataFrame([user_data])
                    df_combined = pd.concat([df_existing, df_new], ignore_index=True)
                    df_combined.to_csv("registrations.csv", index=False)
                except FileNotFoundError:
                    df_new = pd.DataFrame([user_data])
                    df_new.to_csv("registrations.csv", index=False)

                st.success(f"Thank you {full_name}, you have successfully registered!")

# You can continue with your other sections here...
elif selection == "Home":
    st.subheader("Welcome to ASE Dashboard Home")

elif selection == "Donor Reports":
    st.subheader("Donor Reports")

elif selection == "Project Updates":
    st.subheader("Project Updates")

elif selection == "Community Stories":
    st.subheader("Community Stories")

elif selection == "Impact Metrics":
    st.subheader("Impact Metrics")


# Encrypt password using SHA-256
def encrypt_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Check credentials during login
def check_credentials(email, password):
    try:
        df = pd.read_csv("registrations.csv")
        user_row = df[df['Email'] == email]
        if not user_row.empty:
            encrypted_input_password = encrypt_password(password)
            if encrypted_input_password == user_row.iloc[0]['Encrypted Password']:
                return True, user_row.iloc[0]['Full Name'], user_row.iloc[0]['Role']
        return False, None, None
    except FileNotFoundError:
        return False, None, None

# Initialize session state variables
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_name = ""
    st.session_state.role = ""






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


# DASHBOARD AFTER LOGIN
if st.session_state.logged_in and menu == "Dashboard":
    st.subheader(f"Welcome, {st.session_state.user_name}!")
    st.write(f"You are logged in as **{st.session_state.role}**.")

    st.info("This is your ASE Dashboard. More features coming soon!")

# LOGOUT
if st.session_state.logged_in and menu == "Logout":
    st.session_state.logged_in = False
    st.session_state.user_name = ""
    st.session_state.role = ""
    st.success("You have been logged out.")

