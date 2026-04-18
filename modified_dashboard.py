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
    st.subheader("Login to BM-SYSTEM Dashboard\n- Home of Entrepreneurs\n- BIASHARA YAKO MKONONI MWAKO")
    # Create 3 columns with ratios (adjust ratios for different image sizes)
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.image("bridge gap tra.jpg")
    
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
            "All Production Records",
            "Register Items",
            "My registered items",
            "Stock In (Manunuzi)",
            "Stock Out (Mauzo)",
            "Daily Report"
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
        # Register item starts
        elif menu == "Register Items":
             st.subheader("🆕 Register New Business Item")
             
             with st.form("item_reg_form", clear_on_submit=True):
                 item_name = st.text_input("Jina la Bidhaa (Item Name)")
                 category = st.selectbox("Kundi (Category)", ["Chakula", "Mavazi", "Vifaa", "Sabuni", "Zingine"])
                 unit = st.selectbox("Kipimo (Unit)", ["pcs", "kg", "ltr", "box"])
                 
                 col1, col2 = st.columns(2)
                 b_price = col1.number_input("Bei ya Kununua (Buying Price)", min_value=0.0, step=100.0)
                 s_price = col2.number_input("Bei ya Kuuzia (Selling Price)", min_value=0.0, step=100.0)
                 
                 initial_stock = st.number_input("Stock ya sasa (Initial Stock)", min_value=0, step=1)
                 
                 submitted = st.form_submit_button("Sajili Bidhaa")
                 
                 if submitted:
                     if not item_name:
                         st.error("Tafadhali weka jina la bidhaa.")
                     else:
                         try:
                             new_item = {
                                 "user_id": st.session_state.user_id,
                                 "item_name": item_name,
                                 "category": category,
                                 "unit_measure": unit,
                                 "buying_price": b_price,
                                 "selling_price": s_price,
                                 "current_stock": initial_stock
                             }
                             
                             conn.table("inventory_items").insert(new_item).execute()
                             st.success(f"Hongera! {item_name} imesajiliwa vyema.")
                         except Exception as e:
                             st.error(f"Hitilafu: {e}")
        # End register items
        # startsView registerd 
        elif menu == "My registered items":
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

        # Start Stockin                                                                 
        elif menu == "Stock In (Manunuzi)":
             st.subheader("📥 Ingiza Bidhaa (Stock In / Purchase)")
         
             # 1. Fetch current items
             res = conn.table("inventory_items").select("id, item_name, current_stock, buying_price").eq("user_id", st.session_state.user_id).execute()
             
             if res.data:
                 item_options = {item['item_name']: item for item in res.data}
                 
                 # --- SELECT BOX OUTSIDE THE FORM ---
                 # This allows the price to update instantly when the item changes
                 selected_name = st.selectbox("Chagua Bidhaa unayotaka kuongeza stock", list(item_options.keys()))
                 
                 # Get the data for the item the user just picked
                 current_item = item_options[selected_name]
                 
                 # 2. Form for the numbers
                 with st.form("stock_in_form", clear_on_submit=True):
                     st.info(f"Stock ya sasa hivi: {current_item['current_stock']}")
                     
                     qty = st.number_input("Kiasi unachonunua", min_value=1, step=1, value=1)
                     
                     # The price now automatically defaults to the selected item's buying price
                     p_price = st.number_input(
                         "Bei ya kununulia (kwa kila moja)", 
                         value=float(current_item['buying_price']), 
                         step=100.0
                     )
                     
                     submitted = st.form_submit_button("Hifadhi Ununuzi")
         
                     if submitted:
                         try:
                             # Record the buy in transactions table
                             conn.table("inventory_transactions").insert({
                                 "user_id": st.session_state.user_id,
                                 "item_id": current_item['id'],
                                 "type": "STOCK_IN",
                                 "quantity": qty,
                                 "price_per_unit": p_price
                             }).execute()
                             
                             # Calculate and update new stock
                             new_stock = current_item['current_stock'] + qty
                             conn.table("inventory_items").update({"current_stock": new_stock}).eq("id", current_item['id']).execute()
                             
                             st.success(f"Umefanikiwa! Umeongeza {qty} za {selected_name}. Stock mpya: {new_stock}")
                             # Note: We don't use rerun here so the message stays visible
                         except Exception as e:
                             st.error(f"Hitilafu: {e}")
             else:
                 st.info("Bado huna bidhaa. Tafadhali nenda 'Register Items' kwanza.")



        # End stock In
     
     
        # Start Sales                  
        elif menu == "Stock Out (Mauzo)":
             st.subheader("📤 Uza Bidhaa (Stock Out / Sales)")
         
             res = conn.table("inventory_items").select("id, item_name, current_stock, selling_price").eq("user_id", st.session_state.user_id).execute()
             
             if res.data:
                 item_options = {item['item_name']: item for item in res.data}
                 selected_name = st.selectbox("Chagua Bidhaa unayouza", list(item_options.keys()))
                 current_item = item_options[selected_name]
                 
                 with st.form("stock_out_form", clear_on_submit=True):
                     available = current_item['current_stock']
                     st.info(f"Kiasi kilichopo (Available Stock): {available}")
                     
                     # Removed 'max_value' so the user can type any number
                     qty = st.number_input("Kiasi unachouza (Quantity Out)", min_value=1, step=1)
                     s_price = st.number_input("Bei ya kuuzia (Selling Price)", value=float(current_item['selling_price']), step=100.0)
                     
                     submitted = st.form_submit_button("Hifadhi Mauzo")
         
                     if submitted:
                         # 1. Check if stock is available
                         if available <= 0:
                             st.error(f"Samahani, bidhaa ya '{selected_name}' imekwisha kabisa (Out of Stock).")
                         
                         # 2. Check if the user is trying to sell more than they have
                         elif qty > available:
                             st.error(f"Huna stock ya kutosha! Unajaribu kuuza {qty} wakati zilizopo ni {available} pekee.")
                         
                         # 3. If everything is okay, proceed to save
                         else:
                             try:
                                 # Record Sale
                                 conn.table("inventory_transactions").insert({
                                     "user_id": st.session_state.user_id,
                                     "item_id": current_item['id'],
                                     "type": "STOCK_OUT",
                                     "quantity": qty,
                                     "price_per_unit": s_price
                                 }).execute()
                                 
                                 # Subtract from Inventory
                                 new_stock = available - qty
                                 conn.table("inventory_items").update({"current_stock": new_stock}).eq("id", current_item['id']).execute()
                                 
                                 st.success(f"Mauzo yamehifadhiwa! Stock iliyobaki: {new_stock}")
                             except Exception as e:
                                 st.error(f"Hitilafu: {e}")
             else:
                 st.info("Sajili bidhaa kwanza ili uweze kuuza.")


        # End Sales form
        # Start daily reports
        elif menu == "Daily Report":
             st.title("📅 Daily Business Summary")
             
             # 1. Setup Dates
             today_date = datetime.now().strftime("%Y-%m-%d")
             st.info(f"Showing report for: **{today_date}**")
         
             if "user_id" in st.session_state:
                 try:
                     # 2. Fetch all transactions for today with a JOIN to get item names
                     res = conn.table("inventory_transactions") \
                         .select("transaction_date, type, quantity, price_per_unit, total_value, inventory_items(item_name)") \
                         .eq("user_id", st.session_state.user_id) \
                         .gte("transaction_date", f"{today_date}T00:00:00") \
                         .lte("transaction_date", f"{today_date}T23:59:59") \
                         .execute()
         
                     if res.data:
                         # 3. Process Data
                         df = pd.DataFrame(res.data)
                         df['Item Name'] = df['inventory_items'].apply(lambda x: x['item_name'])
                         
                         # Cleanup for display
                         report_df = df[['transaction_date', 'Item Name', 'type', 'quantity', 'price_per_unit', 'total_value']].copy()
                         report_df['transaction_date'] = pd.to_datetime(report_df['transaction_date']).dt.strftime('%H:%M')
                         report_df.columns = ['Time', 'Item', 'Type', 'Qty', 'Unit Price', 'Total']
         
                         # 4. Calculate Summary Metrics
                         purchases = report_df[report_df['Type'] == 'STOCK_IN']['Total'].sum()
                         sales = report_df[report_df['Type'] == 'STOCK_OUT']['Total'].sum()
                         net = sales - purchases
         
                         m1, m2, m3 = st.columns(3)
                         m1.metric("Purchases (In)", f"Tsh {purchases:,.0f}")
                         m2.metric("Sales (Out)", f"Tsh {sales:,.0f}")
                         m3.metric("Net Flow", f"Tsh {net:,.0f}", delta=f"{net:,.0f}")
         
                         st.dataframe(report_df, use_container_width=True, hide_index=True)
         
                         # --- 5. INTERNAL PDF GENERATION LOGIC ---
                         st.divider()
                         if st.button("📑 Je unataka PDF Report?"):
                             try:
                                 buf = BytesIO()
                                 doc = SimpleDocTemplate(buf, pagesize=A4)
                                 elements = []
                                 styles = getSampleStyleSheet()
                                 
                                 # PDF Styles
                                 title_style = ParagraphStyle('T', parent=styles['Title'], fontSize=18, textColor=colors.HexColor("#1E3A8A"))
                                 cell_style = ParagraphStyle('C', parent=styles['Normal'], fontSize=8)
                                 
                                 # PDF Content
                                 elements.append(Paragraph(f" DAILY BUSINESS REPORT: {st.session_state.user_name}", title_style))
                                 elements.append(Paragraph(f"Date: {today_date}", styles['Normal']))
                                 elements.append(Spacer(1, 15))
         
                                 # Prepare Table Data
                                 pdf_data = [report_df.columns.tolist()]
                                 for _, row in report_df.iterrows():
                                     pdf_data.append([str(x) for x in row.values])
                                 
                                 # Add Summary Row to PDF
                                 pdf_data.append(["TOTAL", "", "", "", "", f"Tsh {sales - purchases:,.0f}"])
         
                                 # Build Table
                                 t = Table(pdf_data, colWidths=[0.8*inch, 1.5*inch, 1*inch, 0.6*inch, 1*inch, 1.2*inch])
                                 t.setStyle(TableStyle([
                                     ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
                                     ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                     ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                                     ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
                                     ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                                 ]))
                                 
                                 elements.append(t)
                                 doc.build(elements)
                                 
                                 st.download_button(
                                     label="📥 Sasa Download Daily PDF",
                                     data=buf.getvalue(),
                                     file_name=f"Daily_Report_{today_date}.pdf",
                                     mime="application/pdf"
                                 )
                             except Exception as pdf_err:
                                 st.error(f"PDF Error: {pdf_err}")
         
                     else:
                         st.warning("Hakuna miamala iliyofanyika leo.")
                         
                 except Exception as e:
                     st.error(f"Error: {e}")


        # End daily reports

        elif menu == "All Production Records":
         
            st.subheader("📊 All Your Production Entries")
                    
            if "user_id" in st.session_state:
                try:
                    response = conn.table("production_records") \
                        .select("created_at, zone, product_name, unit_price, quantity, total_earnings, comments") \
                        .eq("user_id", st.session_state.user_id) \
                        .order("created_at", desc=True) \
                        .execute()
        
                    # ONLY RUN THIS IF DATA EXISTS
                    if response.data:
                        prod_df = pd.DataFrame(response.data)
        
                        # --- START OF PDF GENERATION LOGIC ---
                        def create_pdf(df):
                               buf = BytesIO()
                               # Professional A4 setup with clean margins
                               doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=20, bottomMargin=30)
                               elements = []
                               styles = getSampleStyleSheet()
                               
                               # 1. PROFESSIONAL STYLES
                               title_style = ParagraphStyle('TitleStyle', parent=styles['Title'], fontSize=18, textColor=colors.HexColor("#1E3A8A"), alignment=1)
                               cell_style = ParagraphStyle('CellStyle', parent=styles['Normal'], fontSize=8, leading=10)
                               header_cell_style = ParagraphStyle('HeaderCellStyle', parent=styles['Normal'], fontSize=9, textColor=colors.whitesmoke, fontName='Helvetica-Bold', alignment=1)
                               sub_style = ParagraphStyle('SubStyle', parent=styles['Normal'], fontSize=10, textColor=colors.grey)
                           
                               # 2. LOGO & TITLE SECTION
                               try:
                                   # Integrated your specific logo filename
                                   logo = Image("bridge gap tra.jpg", width=1.4*inch, height=0.7*inch)
                                   # Table to hold Logo and Title side-by-side
                                   header_table = Table([[logo, Paragraph("ASE PRODUCTION REPORT", title_style)]], colWidths=[1.5*inch, 4*inch])
                                   header_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
                                   elements.append(header_table)
                               except:
                                   elements.append(Paragraph("ASE PRODUCTION REPORT", title_style))
                               
                               elements.append(Spacer(1, 10))
                               elements.append(Paragraph(f"<b>Entrepreneur:</b> {st.session_state.user_name}", sub_style))
                               elements.append(Paragraph(f"<b>Report Date:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}", sub_style))
                               elements.append(Spacer(1, 20))
                           
                               # 3. DATA PREPARATION (Ensuring proper wrapping)
                               headers = [Paragraph(f"<b>{col}</b>", header_cell_style) for col in df.columns.tolist()]
                               data = [headers]
                               
                               # Add regular data rows
                               for _, row in df.iterrows():
                                   data.append([Paragraph(str(val), cell_style) for val in row.values])
                               
                               # 4. INVOICE-STYLE TOTALS ROW
                               try:
                                   # We assume: Col 4 is Qty, Col 5 is Total (counting starts at 0)
                                   # We use .iloc to pick columns by their position
                                   qty_values = pd.to_numeric(df.iloc[:, 4].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
                                   total_values = pd.to_numeric(df.iloc[:, 5].astype(str).str.replace('Tsh', '').str.replace(',', ''), errors='coerce').fillna(0)
                                   
                                   total_qty = qty_values.sum()
                                   total_money = total_values.sum()
                                   
                                   footer = [
                                       Paragraph("<b>JUMLA / TOTAL</b>", cell_style),
                                       Paragraph("", cell_style),
                                       Paragraph("", cell_style),
                                       Paragraph("", cell_style),
                                       Paragraph(f"<b>{total_qty:,.0f}</b>", cell_style),
                                       Paragraph(f"<b>Tsh {total_money:,.2f}</b>", cell_style),
                                       Paragraph("", cell_style)
                                   ]
                                   data.append(footer)
                               except Exception as e:
                                   # If it still fails, it will tell us which part of the math is wrong
                                   data.append([Paragraph(f"<b>Calculation Error: {str(e)}</b>", cell_style)] + [""]*6)




                           
                               # 5. TABLE CONSTRUCTION & PRO STYLING
                               # Widths assigned for A4: Total ~7.3 inches
                               col_widths = [0.8*inch, 0.9*inch, 1.1*inch, 0.6*inch, 0.5*inch, 1.0*inch, 2.4*inch]
                               t = Table(data, colWidths=col_widths, repeatRows=1)
                               
                               t.setStyle(TableStyle([
                                   # Header Styling
                                   ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
                                   ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                   ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                                   
                                   # Body Styling
                                   ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                                   ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.whitesmoke, colors.white]), # Zebra strips except last row
                                   
                                   # Summary/Total Row Styling
                                   ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#D1D5DB")), # Light grey footer
                                   ('LINEABOVE', (0, -1), (-1, -1), 1.5, colors.HexColor("#1E3A8A")), # Bold line above total
                                   ('ALIGN', (4, -1), (5, -1), 'CENTER'), # Center the total numbers
                               ]))
                               
                               elements.append(t)
                               
                               # 6. SIGNATURE/FOOTER SECTION
                               elements.append(Spacer(1, 30))
                               elements.append(Paragraph("__________________________", sub_style))
                               elements.append(Paragraph("Signature & Official Stamp", sub_style))
                               elements.append(Spacer(1, 15))
                               elements.append(Paragraph("<i>This is a computer-generated report from ASE Dashboard.</i>", sub_style))
                           
                               # 7. BUILD
                               doc.build(elements)
                               return buf.getvalue()



                        # --- END OF PDF GENERATION LOGIC ---
        
                        # Now display the table
                        st.dataframe(prod_df, use_container_width=True, hide_index=True)
        
                        # Show the button only because prod_df DEFINITELY exists here
                        pdf_data = create_pdf(prod_df)
                        st.download_button(
                            label="📑 Download PDF Report",
                            data=pdf_data,
                            file_name="Production_Report.pdf",
                            mime="application/pdf"
                        )
                    else:
                        st.info("Bado hujaingiza taarifa zozote za uzalishaji.")
                        
                except Exception as e:
                    st.error(f"Error fetching data: {e}")
                 # END OF PDF GENERATOR

                 
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



