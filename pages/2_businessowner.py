# imports and etc
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

# IMPORTS FOR PDF MAKING
from reportlab.lib.pagesizes import A4 
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image 
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from io import BytesIO

# END OF PDF IMPORTS

#costom css
st.markdown(
"""

 <style>
[data-testid="stSidebar"]{
    background: linear-gradient(#FFCC00, #4CAF50, #FFEB3B);
   
}

#register-btn button { background-color: red; }


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

    /* Target the form submit button */
    div.stForm submit_button > button {
        background-color: #1E3A8A; /* Your dark blue */
        color: white;
        border-radius: 10px;
        height: 3em;
        width: 100%;
        border: none;
        transition: 0.3s;
    }
    
    /* Change color on hover */
    div.stForm submit_button > button:hover {
        background-color: #3B82F6; /* Lighter blue */
        color: white;
        border: none;
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
    st.session_state.email = ""

# Sidebar Navigation
st.sidebar.image("bridge gap tra.jpg", width=200)
st.sidebar.title("Navigation")

# Conditional menu
if not st.session_state.logged_in:
    menu = st.sidebar.radio("Menu", ["Login", "Register"])
else:
    menu = st.sidebar.radio("Menu", ["Dashboard"])

# REGISTRATION FORM
if menu == "Register":
    st.subheader("Register to access your Role Dashboard.")

    with st.form("registration_form", clear_on_submit=True):
        full_name = st.text_input("Full Name")
        email = st.text_input("Email Address")
        phone = st.text_input("Phone Number")
        organization = st.text_input("Mtaa (Optional)")
        role = st.selectbox("Role", ["Business Owner", "Shopkeeper", "Entreprenuer","Donor", "Partner", "Volunteer", "Community Member"])
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
    # Create 3 columns with ratios (adjust ratios for different image sizes)
    col1, col2, col3 = st.columns([0.5, 0.2, 0.5])
    
    with col2:
        st.image("bm_logo_edited.png", width=300)
    st.subheader("LOGIN TO THE SYSTEM.\n- Home of Entrepreneurs\n- BIASHARA YAKO MKONONI MWAKO")
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
                    st.session_state.email = email.lower().strip() 
                    
                    st.success(f"Welcome {st.session_state.user_name}! You are logged in as {st.session_state.role}.")
                    st.rerun() # Refresh to update the menu/dashboard
                else:
                    st.error("Profile not found. Please contact support.")

            except Exception as e:
                # This catches wrong passwords or non-existent emails
                st.error("Umekosea email au password.")


    st.subheader("Community connect\n- The Digital hub that equips and connects grassroots Entreprenuers, NGOs and CBO from both Rural and Urban with tools, knowledge, and networks to build sustainable Businesses and Transform communities.")
# Sample data (Replace with your actual data)


# DASHBOARD ROLE-BASED VIEWS
if st.session_state.logged_in and menu == "Dashboard":
    st.subheader(f"Welcome, {st.session_state.user_name}!")
    st.write(f"You are logged in as **{st.session_state.role}**.")

    role = st.session_state.role
    # end imports and etc
    if role == "Business Owner":
            #Donors sidebar
            menu_business_owner = st.sidebar.radio("Business Owner Links", [
                "🏠 Business Owner Dashboard.",
                "📤 Pakia bidhaa/Import(Excel).",
                "📋 List ya Bidhaa Ulizosajili.",
                "👥 Assign Shopkeepers.",
                "Angalia duka",
                "Sajili Duka",
                "Matumizi"
            ])
    
            # Add more donor-related content
            # You can add content or visuals for the donor reports here
            # Example donor data
    
            if menu_business_owner == "🏠 Business Owner Dashboard.":
                st.subheader("🏠 Business Owner Dashboard")
          
            # Start csv/excell upload
    
            elif menu_business_owner=="📤 Pakia bidhaa/Import(Excel).":
                 st.subheader("📤 Pakia Bidhaa kwa Excel (Bulk Import)")
                 st.write("Pakia file la Excel lenye bidhaa zako zote.")
                 
                 # 1. File Uploader
                 uploaded_file = st.file_uploader("Chagua file la Excel (.xlsx)", type=["xlsx"])
                 
                 if uploaded_file is not None:
                     try:
                         # 2. Read the Excel file
                         df = pd.read_excel(uploaded_file)
                         
                         st.write("Hakiki data zako hapa chini:")
                         st.dataframe(df.head()) # Show first 5 rows to the user
                 
                         if st.button("Anza Kupakia Sasa (Start Upload)"):
                             # 3. Add the Owner's ID to every row automatically
                             # This ensures the items belong to this specific Business Owner
                             df['user_id'] = st.session_state.user_id
                             
                             # 4. Convert the DataFrame to a list of dictionaries for Supabase
                             data_to_insert = df.to_dict(orient="records")
                             
                             # 5. Execute the Bulk Insert
                             conn.table("inventory_items").insert(data_to_insert).execute()
                             
                             st.success(f"Hongera! Bidhaa {len(data_to_insert)} zimeingizwa kwenye kanzidata yako.")
                             st.rerun()
                 
                     except Exception as e:
                         st.error(f"Kuna tatizo kwenye file lako: {e}")
    
            # End of csv/excell items uploads
    
            
            # startsView registerd 
            elif menu_business_owner == "📋 List ya Bidhaa Ulizosajili.":
                 st.subheader("📋 Orodha ya Bidhaa Zako (Your Item Catalog)")
                 
                 if "user_id" in st.session_state:
                     try:
                         # 1. FETCH data for the logged-in user
                         res = conn.table("inventory_items").select("*").eq("user_id", st.session_state.user_id).execute()
                         
                         if res.data:
                             df_items = pd.DataFrame(res.data)
                             
                             # Professional Summary Metrics
                             m1, m2 = st.columns(2)
                             m1.metric("Total Items", len(df_items))
                             inventory_value = (df_items['buying_price'] * df_items['current_stock']).sum()
                             m2.metric("Inventory Value", f"Tsh {inventory_value:,.0f}")
             
                             # Display Table
                             st.dataframe(
                                 df_items[["item_name", "category", "buying_price", "selling_price", "current_stock", "unit_measure"]], 
                                 use_container_width=True, 
                                 hide_index=True
                             )
             
                             # --- 2. UPDATE & DELETE LOGIC ---
                             st.divider()
                             st.markdown("### 🛠️ Manage Selected Item")
                             
                             # Dropdown to select which item to modify
                             selected_name = st.selectbox("Chagua bidhaa kurekebisha au kufuta", df_items["item_name"].tolist())
                             
                             # Fetch specific data for the selected item using its index
                             item_data = df_items[df_items["item_name"] == selected_name].iloc[0]
             
                             col_a, col_b = st.columns(2)
                             
                             # UPDATE SECTION
                             with col_a:
                                 with st.expander(f"✏️ Update Prices for {selected_name}"):
                                     with st.form("up_form"):
                                         up_buy = st.number_input("New Buy Price", value=float(item_data['buying_price']), step=100.0)
                                         up_sell = st.number_input("New Sell Price", value=float(item_data['selling_price']), step=100.0)
                                         
                                         if st.form_submit_button("Hifadhi Marekebisho"):
                                             conn.table("inventory_items")\
                                                 .update({"buying_price": up_buy, "selling_price": up_sell})\
                                                 .eq("id", item_data['id'])\
                                                 .execute()
                                             st.success("Marekebisho yamefanikiwa!")
                                             st.rerun()
                             
                             # DELETE SECTION
                             #with col_b:
                                 #st.write("Danger Zone/Kuwa Makini Hapa")
                                 #if st.button(f"🗑️ Delete {selected_name}"):
                                     # Direct delete based on unique ID
                                     #try:
                                         #conn.table("inventory_items").delete().eq("id", item_data['id']).execute()
                                         #st.success(f"{selected_name} imefutwa!")
                                         #st.rerun()
                                     #except Exception as e:
                                         #st.error(f"Futa imeshindikana: {e}")
                                         
                         else:
                             st.info("Bado hujaasajili bidhaa yoyote.")
                     except Exception as e:
                         st.error(f"Database Error: {e}")
                 else:
                     st.warning("Tafadhali ingia (Login) kwanza.")
    
            # End view registerd
         
    
            # Start shopkeeper assignment
            elif menu_business_owner == "👥 Assign Shopkeepers.":
                 st.subheader("🏢 Business & Shop Management")
             
                 # LOGIC 1: Verify the Business exists for this owner
                 biz_res = conn.table("businesses").select("id, business_name").eq("owner_id", st.session_state.user_id).execute()
             
                 if not biz_res.data:
                     # If no business, they MUST create one first
                     st.warning("Hatua ya 1: Sajili Biashara yako kwanza.")
                     with st.form("create_biz"):
                         biz_name = st.text_input("Jina la Biashara (e.g. ASE Group)")
                         if st.form_submit_button("Sajili Biashara"):
                             try:
                                 conn.table("businesses").insert({
                                     "owner_id": st.session_state.user_id,
                                     "business_name": biz_name
                                 }).execute()
                                 st.success("Biashara imesajiliwa!")
                                 st.rerun()
                             except Exception as e:
                                 st.error(f"Error: {e}")
                 else:
                     # LOGIC 2: Business exists, now manage Shops and Assignments
                     business_id = biz_res.data[0]['id']
                     st.info(f"Biashara: **{biz_res.data[0]['business_name']}**")
             
                     # PART A: Create a Shop
                     with st.expander("➕ Ongeza Duka (Add Shop)"):
                         with st.form("create_shop"):
                             shop_name = st.text_input("Jina la Duka (e.g. Shop A)")
                             loc = st.text_input("Mahali")
                             if st.form_submit_button("Hifadhi Duka"):
                                 try:
                                     conn.table("shops").insert({
                                         "business_id": business_id,
                                         "owner_id": st.session_state.user_id,
                                         "shop_name": shop_name,
                                         "location": loc
                                     }).execute()
                                     st.success("Duka limeundwa!")
                                     st.rerun()
                                 except Exception as e:
                                     st.error(f"Error: {e}")
             
                     # PART B: Assign Shopkeeper (Only if shops exist)
                     st.divider()
                     shops_res = conn.table("shops").select("id, shop_name").eq("owner_id", st.session_state.user_id).execute()
                     
                     if shops_res.data:
                         st.subheader("Assign Shopkeeper")
                         shop_options = {s['shop_name']: s['id'] for s in shops_res.data}
                         
                         with st.form("assign_sk"):
                             sel_shop = st.selectbox("Chagua Duka", list(shop_options.keys()))
                             sk_email = st.text_input("Email ya Shopkeeper").lower().strip()
                             if st.form_submit_button("Panga Shopkeeper"):
                                 try:
                                     conn.table("shop_assignments").insert({
                                         "shop_id": shop_options[sel_shop],
                                         "shopkeeper_email": sk_email
                                     }).execute()
                                     st.success(f"Umezipangia {sk_email} duka la {sel_shop}")
                                 except Exception as e:
                                     st.error(f"Error: {e}")
                     else:
                         st.info("Ongeza duka kwanza ili upange wafanyakazi.")
             
            # End Assign shopkeeper 
            
            elif menu_business_owner == "Angalia duka":
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
if st.sidebar.button("Logout"):
    conn.client.auth.sign_out()
    st.session_state.logged_in = False
    st.session_state.clear()
    st.switch_page("modified_dashboard.py")
    st.success("You have been logged out successful.")
