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
    if role == "Community Member":
        #This is side bar
        menu = st.sidebar.radio("Karibu Chagua viunganishi", [
            "🏠 Home",
            "📚 Learning Materials",
            "👥 Community Stories",
            "💰 MATUMIZI/MADENI",
            "🏭 TAARIFA ZA UZALISHAJI",
            "📝 REGISTER ITEMS",
            "👁️ MY REGISTERED ITEMS",
            "📥 Stock In (Manunuzi)",
            "📤 Stock Out (Mauzo)",
            "📊 Daily Report"
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
                 category = st.selectbox("Kundi (Category)", ["Material ya sabuni", "Sabuni ya mche", "Vifaa", "Sabuni ya maji", "Zingine"])
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
                 
                 # We get the registered price from the database
                 registered_price = float(current_item['selling_price'])
         
                 with st.form("stock_out_form", clear_on_submit=True):
                     available = current_item['current_stock']
                     st.info(f"Kiasi kilichopo (Available Stock): {available}") 
                     
                     qty = st.number_input("Kiasi unachouza (Quantity Out)", min_value=1, step=1)
                     s_price = st.number_input("Bei ya kuuzia (Selling Price)", value=registered_price, step=100.0)
                     
                     submitted = st.form_submit_button("Hifadhi Mauzo")
         
                     if submitted:
                         # 1. NEW CHECK: Price Alert
                         if s_price < registered_price:
                             st.warning(f"⚠️ Tahadhari: Umeuza bidhaa hii chini ya bei iliyopangwa (Tsh {registered_price:,.0f}).")
         
                         # 2. Check if stock is available
                         if available <= 0:
                             st.error(f"Samahani, bidhaa ya '{selected_name}' imekwisha kabisa (Out of Stock).")
                         
                         # 3. Check if user is trying to sell more than they have
                         elif qty > available:
                             st.error(f"Huna stock ya kutosha! Unajaribu kuuza {qty} wakati zilizopo ni {available} pekee.")
                         
                         # 4. Proceed to save
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
                                 # We use st.rerun() if you want the "Available Stock" info box to update immediately
                             except Exception as e:
                                 st.error(f"Hitilafu: {e}")
             else:
                 st.info("Sajili bidhaa kwanza ili uweze kuuza.")



        # End Sales form
        # Start daily reports
        elif menu == "📊 Daily Report":
             st.title("📅 Daily Business Summary")
             
             today_date = datetime.now().strftime("%Y-%m-%d")
             st.info(f"Showing report for: **{today_date}**")
         
             if "user_id" in st.session_state:
                 try:
                     # 1. Fetch transactions + JOIN with inventory_items to get registered selling_price
                     res = conn.table("inventory_transactions") \
                         .select("transaction_date, type, quantity, price_per_unit, total_value, inventory_items(item_name, selling_price)") \
                         .eq("user_id", st.session_state.user_id) \
                         .gte("transaction_date", f"{today_date}T00:00:00") \
                         .lte("transaction_date", f"{today_date}T23:59:59") \
                         .execute()
         
                     if res.data:
                         df = pd.DataFrame(res.data)
                         
                         # Extract joined data
                         df['Item Name'] = df['inventory_items'].apply(lambda x: x['item_name'])
                         df['Reg Price'] = df['inventory_items'].apply(lambda x: x['selling_price'])
                         
                         # 2. Calculate Loss per transaction (Only for Sales/STOCK_OUT)
                         # Loss = (Registered Price - Actual Sold Price) * Quantity
                         def calculate_loss(row):
                             if row['type'] == 'STOCK_OUT' and row['price_per_unit'] < row['Reg Price']:
                                 return (row['Reg Price'] - row['price_per_unit']) * row['quantity']
                             return 0
         
                         df['Loss'] = df.apply(calculate_loss, axis=1)
         
                         # Summary Data
                         report_df = df[['transaction_date', 'Item Name', 'type', 'quantity', 'price_per_unit', 'total_value', 'Loss']].copy()
                         report_df['transaction_date'] = pd.to_datetime(report_df['transaction_date']).dt.strftime('%H:%M')
                         report_df.columns = ['Time', 'Item', 'Type', 'Qty', 'Unit Price', 'Total', 'Price Loss']
         
                         # 3. Calculate Summary Metrics
                         purchases = report_df[report_df['Type'] == 'STOCK_IN']['Total'].sum()
                         sales = report_df[report_df['Type'] == 'STOCK_OUT']['Total'].sum()
                         total_loss = report_df['Price Loss'].sum()
                         net = sales - purchases
         
                         m1, m2, m3, m4 = st.columns(4)
                         m1.metric("Purchases (Manunuzi)", f"Tsh {purchases:,.0f}")
                         m2.metric("Sales (Mauzo)", f"Tsh {sales:,.0f}")
                         m3.metric("Total Price Loss (Discounts)", f"Tsh {total_loss:,.0f}", delta=f"-{total_loss:,.0f}", delta_color="inverse")
                         m4.metric("Net Flow", f"Tsh {net:,.0f}")
         
                         if total_loss > 0:
                             st.warning(f"⚠️ Leo umepoteza jumla ya Tsh {total_loss:,.0f} kwa kuuza chini ya bei elekezi (Discounts).")
         
                         st.dataframe(report_df, use_container_width=True, hide_index=True)
         
                         # --- 4. PDF GENERATION ---
                         
                         
                         st.divider()
                         if st.button("📑 Je unataka PDF Report?"):
                             try:
                                 buf = BytesIO()
                                 doc = SimpleDocTemplate(buf, pagesize=A4)
                                 elements = []
                                 styles = getSampleStyleSheet() 
                                 title_style = ParagraphStyle('T', parent=styles['Title'], fontSize=18, textColor=colors.HexColor("#1E3A8A"))
                                 cell_style = ParagraphStyle('C', parent=styles['Normal'], fontSize=8, leading=10)
                                 logo = Image("bm_logo_edited.png", width=2*inch, height=1*inch)
                                 logo.hAlign = 'CENTER'
                                 elements.append(logo)
                                 elements.append(Paragraph(f"...", title_style))
                                 elements.append(Paragraph(f"Ripoti ya siku na: {st.session_state.user_name}", title_style))
                                 elements.append(Paragraph(f"Date: {today_date}", styles['Normal']))
                                 elements.append(Spacer(1, 15))
                         
                                 # FIX 2: Wrap headers in Paragraph()
                                 pdf_data = [[Paragraph(str(col), cell_style) for col in report_df.columns.tolist()]]
                                 
                                 # FIX 3: Wrap row data in Paragraph()
                                 for _, row in report_df.iterrows():
                                     pdf_data.append([Paragraph(str(x), cell_style) for x in row.values])
                                 
                                 # FIX 4: Wrap Summary Row items in Paragraph()
                                 pdf_data.append([
                                     Paragraph("TOTAL", cell_style), "", "", "", "", 
                                     Paragraph(f"Tsh {sales:,.0f}", cell_style), 
                                     Paragraph(f"Loss: {total_loss:,.0f}", cell_style)
                                 ])
                         
                                 t = Table(pdf_data, colWidths=[0.6*inch, 1.6*inch, 1.0*inch, 0.5*inch, 0.9*inch, 1.1*inch, 1.1*inch])
                                 t.setStyle(TableStyle([
                                     ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
                                     ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                     ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                                     ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
                                     ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                                     ('VALIGN', (0, 0), (-1, -1), 'TOP'), # FIX 5: Keep text at top of tall cells
                                 ]))
                                 
                                 elements.append(t)
                                # 6. SIGNATURE/FOOTER SECTION
                                 sub_style = ParagraphStyle('SubStyle', parent=styles['Normal'], fontSize=10, textColor=colors.grey)
                                 elements.append(Spacer(1, 30))
                                 elements.append(Paragraph("__________________________", sub_style))
                                 elements.append(Paragraph("Signature & Official Stamp", sub_style))
                                 elements.append(Spacer(1, 15))
                                 elements.append(Paragraph("<i>This is a computer-generated report by BM-SYSTEM.</i>", sub_style))
                                 elements.append(Paragraph("<i>Weka Kumbukumbu. Jenga Biashara. Kua Sasa .</i>", sub_style))
                                 doc.build(elements)
                                 st.download_button("📥 Sasa Download Daily PDF", data=buf.getvalue(), file_name=f"Daily_Report_{today_date}.pdf", mime="application/pdf")
                             except Exception as pdf_err:
                                 st.error(f"PDF Error: {pdf_err}")
                     else:
                         st.warning("Hakuna miamala iliyofanyika leo.")
                 except Exception as e:
                     st.error(f"Error: {e}")
                         
         
                         # --- End PDF GENERATION ---
                  # End Pdf generator



        # End daily reports

      

                 
                                            # MATUMIZI/MAREJESHO/MADENI
        elif menu=="💰 MATUMIZI/MADENI":
                    st.title("💰💳💸 MATUMIZI/MAREJESHO/MADENI")
                    st.markdown("MATUMIZI/MAREJESHO/MADENI NA MWENENDO WA BIASHARA YAKO")
                    st.divider()
                    # --- DYNAMIC TIME FILTER ---
                    # This allows the user to choose how they want to see the charts and numbers
                    filter_muda = st.radio(
                        "Chagua Mpangilio wa Muda (Select Timeframe):",
                        ["💳 Matumizi", "📊 Ripoti/Matumizi", "💸 Marejesho", "💰 Madeni", "💡 Ushauri"],
                        horizontal=True
                    )
                    
                    st.divider()
                    # --- LOGIC SEPARATION ---
                    # We will use the selected filter to aggregate our financial numbers
                    if filter_muda == "💳 Matumizi":
                        st.header("💳 Rekodi Matumizi (Add Expenditure)")
                        with st.form("expenditure_form"):
                            category = st.selectbox("Aina ya Matumizi", ["Stock", "Rent", "Salaries", "Utilities", "Other"])
                            amount = st.number_input("Kiasi (Amount)", min_value=0.0)
                            description = st.text_area("Maelezo (Description)")
                            date = st.date_input("Tarehe")
                            
                            submitted = st.form_submit_button("Hifadhi")
                            
                            if submitted:
                                # Assuming user ID is stored in session state after login
                                user_id = st.session_state.get("user_id")
                                
                                data = {
                                    "user_id": user_id,
                                    "category": category,
                                    "amount": amount,
                                    "description": description,
                                    "transaction_date": str(date)
                                }
                                
                                try:
                                    conn.table("expenditure").insert(data).execute()
                                    st.success("Matumizi yamehifadhiwa kikamilifu!")
                                except Exception as e:
                                    st.error(f"Hitilafu: {e}")

          
                        # Ripoti ya siku ina malizika
                        
                        
                    elif filter_muda == "💸 Marejesho":
                        st.subheader("💸 Marejesho")
                    elif filter_muda == "📊 Ripoti/Matumizi":
                        st.header("📊 Ripoti ya Matumizi")
                        # Example: Admins see all, Staff see only theirs
                        user_role = st.session_state.get("role")
                        user_id = st.session_state.get("user_id")
                        
                        if user_role == "admin":
                            # Fetch all records
                            response = conn.table("expenditure").select("*").execute()
                        else:
                            # Fetch only current user's records
                            response = conn.table("expenditure").select("transaction_date, category, amount, description").eq("user_id", user_id).execute()
                            # 1. Fetch the data
                            response = conn.table("expenditure").select("category, amount, description").eq("user_id", user_id).execute()
                            
                            if response.data:
                                # 2. Convert to DataFrame
                                df = pd.DataFrame(response.data)
                                
                                # 3. Calculate Total
                                total_matumizi = df["amount"].sum()
                                
                                # 4. Display the Total at the top using a metric for visibility
                                st.metric(label="Jumla ya Matumizi (Total)", value=f"TSh {total_matumizi:,.2f}")
                                
                                # 5. Display the Table with nice headers
                                st.write("### Orodha ya Matumizi")
                                display_df = df.rename(columns={
                                    "category": "Aina",
                                    "amount": "Kiasi",
                                    "description": "Maelezo"
                                })
                                st.dataframe(display_df, use_container_width=True)
                                
                            else:
                                st.info("Hakuna matumizi yaliyopatikana.")

                        
                        
                    else:
                        st.subheader("💰 Madeni")
        # End of Matumizi/MAREJESHO NA MADENI
        elif menu=="🏭 TAARIFA ZA UZALISHAJI": 
                    st.title("🏭 TAARIFA ZA UZALISHAJI")
                    st.markdown("Taarifa za uzalishaji, usambazaji na madeni unayodai")
                    st.divider()
                    # --- DYNAMIC TIME FILTER ---
                    # This allows the user to choose how they want to see the charts and numbers
                    filter_muda = st.radio(
                        "Chagua Mpangilio ",
                        ["🏭 FOMU YA UZALISHAJI", "🚚 USAMBAZAJI BIDHAA", "💸 MADENI", "📊 REPORTS YA UZALISHAJI"],
                        horizontal=True
                    )
                    
                    st.divider()
                    # --- LOGIC SEPARATION ---
                    # We will use the selected filter to aggregate our financial numbers
                    if filter_muda == "🏭 FOMU YA UZALISHAJI":
                        st.subheader("🏭 FOMU YA UZALISHAJI")
                        # Ripoti ya UZALISHAJI inaanza 
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
          
                        # Ripoti ya UZALISHAJI ina malizika
                        
                        
                    elif filter_muda == "🚚 USAMBAZAJI BIDHAA":
                        st.subheader("🚚 USAMBAZAJI BIDHAA")
                    elif filter_muda == "💸 MADENI":
                        st.subheader("💸 MADENI")
                        
                        
                    else:
                        st.subheader("📊 REPORTS ZA UZALISHAJI")
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
                                           elements.append(Paragraph("<i>This is a computer-generated report from Bridge gap transparency system.</i>", sub_style))
                                       
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
             
                             
            # Mwisho taarifa za uzalishaji 
            



# LOGOUT
if st.sidebar.button("Logout"):
    conn.client.auth.sign_out()
    st.session_state.logged_in = False
    st.session_state.clear()
    st.switch_page("modified_dashboard.py")
    st.success("You have been logged out successful.")
