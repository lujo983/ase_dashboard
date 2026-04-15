import pandas as pd
import streamlit as st
import datetime
from datetime import datetime 
current_time=datetime.now 
import hashlib
import os
from supabase import create_client

url = st.secrets["SUPABASE_URL"]  
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)
from st_supabase_connection import SupabaseConnection
# Initialize connection
conn = st.connection("supabase", type=SupabaseConnection)

#costom css
st.markdown(
"""

 <style>
[data-testid="stSidebar"]{
    background: linear-gradient(white, #4CAF50, #FFEB3B);
   
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
st.sidebar.image("bridge gap tra.jpg", width=200)
st.sidebar.title("Navigation")

# Conditional menu
if not st.session_state.logged_in:
    menu = st.sidebar.radio("Menu", ["Login", "Register"])
else:
    menu = st.sidebar.radio("Menu", ["Dashboard", "Logout"])

# REGISTRATION FORM
if menu == "Register":
    st.subheader("Register for ASE Dashboard.")

    with st.form("registration_form", clear_on_submit=True):
        full_name = st.text_input("Full Name")
        email = st.text_input("Email Address")
        phone = st.text_input("Phone Number")
        organization = st.text_input("Mtaa (Optional)")
        role = st.selectbox("Role", ["Donor", "Volunteer", "Partner", "Community Member"])
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")

        submitted = st.form_submit_button("Register")

        # THIS SECTION MUST BE INDENTED TO MATCH THE INPUTS ABOVE
        if submitted:
            if not full_name or not email or not phone or not password:
                st.warning("Please fill in all required fields.")
            elif password != confirm_password:
                st.error("Passwords do not match.")
            else:
                try:
                    # 1. Sign up the user in Supabase Auth
                    auth_res = conn.client.auth.sign_up({
                        "email": email, 
                        "password": password
                    })
                    
                    user_id = auth_res.user.id

                    # 2. Insert profile data into your table
                    profile_data = {
                        "id": user_id,
                        "full_name": full_name,
                        "phone": phone,
                        "organization": organization,
                        "role": role
                    }
                    
                    conn.table("profiles").insert(profile_data).execute()
                    st.success("Registration successful! You can now log in.")
                    
                except Exception as e:
                    st.error(f"Registration error: {e}")



# LOGIN FORM
if menu == "Login" and not st.session_state.get("logged_in", False):
    st.subheader("Login to ASE Dashboard\n- Home of Entrepreneurs")
    
    with st.form("login_form"):
        email = st.text_input("Email Address")
        password = st.text_input("Password", type="password")
        login_submit = st.form_submit_button("Login")

        if login_submit:
            try:
                # 1. Authenticate with Supabase
                res = conn.client.auth.sign_in_with_password({
                    "email": email,
                    "password": password
                })
                
                # 2. Get the User ID from the successful login
                user_id = res.user.id
                
                # 3. Fetch the profile details (Name and Role) from your table
                profile = conn.table("profiles").select("full_name, role").eq("id", user_id).single().execute()
                
                if profile.data:
                    # 4. Save to session state
                    st.session_state.logged_in = True
                    st.session_state.user_id = user_id
                    st.session_state.user_name = profile.data["full_name"]
                    st.session_state.role = profile.data["role"]
                    
                    st.success(f"Welcome {st.session_state.user_name}! You are logged in as {st.session_state.role}.")
                    st.rerun() # Refresh to update the menu/dashboard
                else:
                    st.error("Profile not found. Please contact support.")

            except Exception as e:
                # This catches wrong passwords or non-existent emails
                st.error("Umekosea email au password.")


    st.subheader("Community connect\n- The leading digital hub that equips and connects grassroots Entreprenuers, NGOs and CBO from both Rural and Urban with tools, knowledge, and networks to build sustainable Businesses and Transform communities.")
# Sample data (Replace with your actual data)


# DASHBOARD ROLE-BASED VIEWS
if st.session_state.logged_in and menu == "Dashboard":
    st.subheader(f"Welcome, {st.session_state.user_name}!")
    st.write(f"You are logged in as **{st.session_state.role}**.")

    role = st.session_state.role
    


    # Donor Dashboard
    if role == "Donor":
        #Donors sidebar
        menu1 = st.sidebar.radio("Donors Links", [
            "Home",
            "Donor Reports",
            "Project Updates",
            "Community Stories",
            "Impact Metrics",
            "All Production Records"
        ])

        # Add more donor-related content
        # You can add content or visuals for the donor reports here
        # Example donor data

        if menu1 == "Donor Reports":
            st.subheader("Donor Reports")
            st.info("This section includes summarized reports for donors.")
            st.markdown("- Funding used in Q1\n- Women trained: 1500\n- Beehives installed: 10\n- Briquettes made: 1,200kg")

            donor_data = {
            "Donor": ["Alice", "Bob", "Charlie"],
            "Amount": [500,1000, 1500], 
            "Project": ["Sunflower Farming", "Beekeeping", "Sunflower Farming"]
            }

            df = pd.DataFrame(donor_data)

        # Sample data (Replace with your actual data)

        elif menu1=="Home":
            st.header("Donor Dashboard")
            st.info("Thank you for your contributions!")
            st.write("Here you can view\n- Donor reports\n- Funding impact\n- Financial transparency.")


        elif menu1 == "Project Updates":
            st.subheader("Project Updates")
            st.success("Recent activities in Dongobesh and Yaeda Kati:")
            st.markdown("- Sunflower pressing workshop completed\n- Organic lotion production training done\n- Mobile app 'Bridge Gap Transparency' launched")

            updates = [
            {"date": "2025-03-01", "update": "Successfully planted sunflowers on 5 acres."},
            {"date": "2025-03-10", "update": "Started beekeeping training for 30 women."}
            ]
            st.write("### Project Updates Visualization")
            data = {
            'Zone': ['Hydom', 'Dongobesh', 'Mbulu'],
            'Women': [5, 20, 15],
            'Acres': [10, 50, 30],
            'Yield (kg)': [500, 1750, 1000]
            }

            df = pd.DataFrame(data)

                
            #Displaying a bar chart
            st.subheader('Women Farmers Per Zone')
            st.bar_chart(df.set_index('Zone')['Women'])
            #Displaying a line chart for acres
            st.subheader('Acres Under Cultivation')
            st.line_chart(df.set_index('Zone')['Acres'])
            st.dataframe(df)


        elif menu1 == "Community Stories":
            # You can add content for community stories here
            st.subheader("Community Stories")
            st.markdown("**Maria from Mbulu:** 'I never thought I’d earn from making briquettes. ASE changed my life!'")
            st.markdown("**Agnes from Hydom:** 'Now I make soap and can pay school fees for my children.'")
            stories = [
            {"name": "Jane Doe", "story": "The beekeeping project has transformed my life..."},
            {"name": "Mary Smith", "story": "With the sunflower farming project, I can now support my family..."}
            ]

            
            for story in stories:
                st.write(f"**{story['name']}**: {story['story']}")

        elif menu1 == "Impact Metrics":
            st.subheader("Impacts Metrics")
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
            #fig, ax = plt.subplots()
            #ax.bar(metrics.keys(), metrics.values())
            #st.pyplot(fig)

        elif menu1 == "All Production Records":
            st.subheader("All Community Production Entries")
            try:
                prod_df = pd.read_csv("production_records.csv")
                st.dataframe(prod_df)
            except FileNotFoundError:
                st.warning("No production records found.")
            data = {
            'Village': ['Hydom', 'Dongobesh', 'Mbulu'],
            'Farmers': [5, 20, 15],
            'Acres': [10, 50, 30],
            'Yield (kg)': [500, 1750, 1000]
            }

            df = pd.DataFrame(data)
            #Displaying a pie chart for total yield
            st.subheader('Total Yield (kg)')
            #fig, ax = plt.subplots()
            #ax.pie(df['Yield (kg)'], labels=df['Village'], autopct='%1.1f%%')
            #st.pyplot(fig)

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
        #This is side bar
        menu = st.sidebar.radio("Karibu Chagua viunganishi", [
            "Home",
            "Learning Materials",
            "Community Stories",
            "Daily Production Entry Form",
            "All Production Records"
        ])
        # Add community member content
        # Community member sees daily production form


        if menu == "Home":
            st.header("Community Member Dashboard")
            st.info("Empowering our communities! Together we can make greater impacts")
            st.markdown("- Explore Community stories\n- Learning materials\n- Resources\n- Daily production reports and \n- Your Production Entries Records.")

        elif menu == "Learning Materials":
            st.subheader("Learning Materials")
            st.success("Recent Learning Materials available:")
            st.markdown("- Soap bar making\n- Liquid Soap production\n- Organic lotion production\n- Organic Skin care Cream\n- Cleaning Beeswax\n- Biomass Briquettes Production")

        elif menu == "Community Stories":
            st.subheader("Community Stories")
            st.markdown("**Maria from Mbulu:** 'I never thought I’d earn from making briquettes. ASE changed my life!'")
            st.markdown("**Agnes from Hydom:** 'Now I make soap and can pay school fees for my children.'")

        elif menu == "Daily Production Entry Form":
            # Start Daily production entry form
            st.subheader("Daily Production Entry Form")
            
            zones = ["Dongobesh", "Hydom", "Mbulu"]
            zone = st.selectbox("Chagua Kanda yako", zones)
            
            product_name = st.selectbox("Jina la Bidhaa", ["Liquid Soap", "Soap Bars", "Biomass Briquettes", "Skin Care Cream", "Lotion"])
            unit_price = st.number_input("Bei yake", min_value=0.0, step=0.01)
            quantity = st.number_input("Kiasi ulichozalisha", min_value=0, step=1)
            comments = st.text_area("Maoni, Tafadhali weka maoni yako hapa (Optional)")
            
            total_earnings = unit_price * quantity
            
            if st.button("Wasilisha Taarifa"):
                # Ensure user is logged in to get their ID
                if "user_id" in st.session_state:
                    production_data = {
                        "user_id": st.session_state.user_id,
                        "user_name": st.session_state.user_name,
                        "zone": zone,
                        "product_name": product_name,
                        "unit_price": unit_price,
                        "quantity": quantity,
                        "total_earnings": total_earnings,
                        "comments": comments
                    }
            
                    try:
                        # Insert into Supabase
                        conn.table("production_records").insert(production_data).execute()
                        st.success("Hongera! Umefanikiwa kuingiza taarifa zako kwenye kanzidata2.")
                    except Exception as e:
                        st.error(f"Imeshindikana kuhifadhi: {e}")
                else:
                    st.error("Tafadhali ingia (Login) kwanza ili kuwasilisha taarifa.")
                      
                    #End of Daily production entry form
          elif menu == "All Production Records":
             st.subheader("📊 All Your Production Entries")
             
             if "user_id" in st.session_state:
                 try:
                     # 1. Fetch data from Supabase for this specific user
                     # RLS ensures they only get their own data, but we filter by user_id to be explicit
                     response = conn.table("production_records") \
                         .select("created_at, zone, product_name, unit_price, quantity, total_earnings, comments") \
                         .eq("user_id", st.session_state.user_id) \
                         .order("created_at", desc=True) \
                         .execute()
         
                     if response.data:
                         # 2. Convert to DataFrame
                         prod_df = pd.DataFrame(response.data)
         
                         # 3. Clean up formatting for a "Pro" look 
                         prod_df.columns = ["Date", "Zone", "Product", "Price", "Qty", "Total", "Comments"]
                         prod_df["Date"] = pd.to_datetime(prod_df["Date"]).dt.strftime('%Y-%m-%d %H:%M')
         
                         # 4. Show Summary Metrics at the top
                         col1, col2, col3 = st.columns(3)
                         col1.metric("Total Entries", len(prod_df))
                         col2.metric("Total Quantity", f"{prod_df['Qty'].sum():,}")
                         col3.metric("Total Earnings", f"Tsh {prod_df['Total'].sum():,.2f}")
         
                         # 5. Display the data table with styling
                         st.dataframe(prod_df, use_container_width=True, hide_index=True)
                         
                         # 6. Option to Download as CSV (for their own records)
                         csv = prod_df.to_csv(index=False).encode('utf-8')
                         st.download_button("📥 Download Records as CSV", data=csv, file_name="my_production.csv", mime="text/csv")
                     else:
                         st.info("Bado hujaingiza taarifa zozote za uzalishaji.")
                         
                 except Exception as e:
                     st.error(f"Error fetching data: {e}")
             else:
                 st.warning("Please login to view your records.")


# LOGOUT
if st.sidebar.button("Logout"):
    conn.client.auth.sign_out()
    st.session_state.logged_in = False
    st.session_state.clear()
    st.rerun()
    st.success("You have been logged out successful.")


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



