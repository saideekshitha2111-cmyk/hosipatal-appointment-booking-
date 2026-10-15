import streamlit as st
import pandas as pd
import os
from datetime import date, timedelta, datetime

# ---------------------------------------------------------
# FILE PATHS (CSV files ni ikkade save chestham)
# ---------------------------------------------------------
USERS_FILE = "users.csv"
HOSPITALS_FILE = "hospitals.csv"
APPOINTMENTS_FILE = "appointments.csv"
HOSPITAL_LOGINS_FILE = "hospital_logins.csv"   # NEW: hospital logins ikkada save avutayi

# ---------------------------------------------------------
# ADMIN CREDENTIALS (fixed - only ee email/password tone admin login avuthundi)
# ---------------------------------------------------------
ADMIN_EMAIL = "maddipatlarajitha4@gmail.com"
ADMIN_PASSWORD = "1234"

# ---------------------------------------------------------
# CSV FILES REVERT AVvakunda (already unte skip, lekapothe create)
# ---------------------------------------------------------
def init_files():
    if not os.path.exists(USERS_FILE):
        pd.DataFrame(columns=["name", "phone", "password"]).to_csv(USERS_FILE, index=False)

    if not os.path.exists(APPOINTMENTS_FILE):
        pd.DataFrame(columns=[
            "patient_name", "phone", "blood_group", "weight",
            "hospital", "specialist", "doctor",
            "date", "time", "payment_status", "booked_on"
        ]).to_csv(APPOINTMENTS_FILE, index=False)

    if not os.path.exists(HOSPITAL_LOGINS_FILE):
        # Add Hospital page lo admin add chesetappudu, hospital ki oka login create avutundi -> ikkada store
        pd.DataFrame(columns=["hospital", "email", "password"]).to_csv(HOSPITAL_LOGINS_FILE, index=False)

    if not os.path.exists(HOSPITALS_FILE):
        # Kurnool lo 30 sample hospitals + specialists + doctors + emergency phone
        default_hospitals = [
            ("Kurnool Government General Hospital", "General Medicine", "Dr. Ramesh Reddy", "9440100001"),
            ("Kurnool Government General Hospital", "Cardiology", "Dr. Suresh Kumar", "9440100001"),
            ("Apollo Clinic Kurnool", "Orthopedics", "Dr. Anil Varma", "9440100002"),
            ("Apollo Clinic Kurnool", "Dermatology", "Dr. Priya Sharma", "9440100002"),
            ("Santhiram Medical College Hospital", "Neurology", "Dr. Vijay Kumar", "9440100003"),
            ("Santhiram Medical College Hospital", "Pediatrics", "Dr. Lakshmi Devi", "9440100003"),
            ("Navodaya Medical College Hospital", "Gynecology", "Dr. Sunitha Rani", "9440100004"),
            ("Navodaya Medical College Hospital", "ENT", "Dr. Krishna Murthy", "9440100004"),
            ("G Pulla Reddy Hospital", "General Surgery", "Dr. Naveen Babu", "9440100005"),
            ("G Pulla Reddy Hospital", "Urology", "Dr. Mahesh Reddy", "9440100005"),
            ("Sunrise Hospital Kurnool", "Cardiology", "Dr. Ravi Teja", "9440100006"),
            ("Sunrise Hospital Kurnool", "Nephrology", "Dr. Sandhya Rani", "9440100006"),
            ("Life Care Hospital Kurnool", "General Medicine", "Dr. Prasad Rao", "9440100007"),
            ("Life Care Hospital Kurnool", "Diabetology", "Dr. Kavitha Reddy", "9440100007"),
            ("Aditya Hospital Kurnool", "Orthopedics", "Dr. Srinivas Rao", "9440100008"),
            ("Aditya Hospital Kurnool", "Pulmonology", "Dr. Manoj Kumar", "9440100008"),
            ("City Care Hospital Kurnool", "Pediatrics", "Dr. Anitha Reddy", "9440100009"),
            ("City Care Hospital Kurnool", "Dermatology", "Dr. Chandra Sekhar", "9440100009"),
            ("KIMS Kurnool", "Cardiology", "Dr. Vamsi Krishna", "9440100010"),
            ("KIMS Kurnool", "Oncology", "Dr. Padma Latha", "9440100010"),
            ("Vijaya Hospital Kurnool", "General Medicine", "Dr. Ashok Kumar", "9440100011"),
            ("Vijaya Hospital Kurnool", "Gastroenterology", "Dr. Ramya Sri", "9440100011"),
            ("Rainbow Children Hospital Kurnool", "Pediatrics", "Dr. Divya Reddy", "9440100012"),
            ("Rainbow Children Hospital Kurnool", "Neonatology", "Dr. Harika Sri", "9440100012"),
            ("Sai Krishna Hospital Kurnool", "Orthopedics", "Dr. Bhaskar Rao", "9440100013"),
            ("Sai Krishna Hospital Kurnool", "General Surgery", "Dr. Naresh Babu", "9440100013"),
            ("Prashanth Hospital Kurnool", "ENT", "Dr. Swathi Reddy", "9440100014"),
            ("Prashanth Hospital Kurnool", "Ophthalmology", "Dr. Kiran Kumar", "9440100014"),
            ("Global Hospital Kurnool", "Neurology", "Dr. Satish Chandra", "9440100015"),
            ("Global Hospital Kurnool", "Cardiology", "Dr. Deepak Reddy", "9440100015"),
        ]
        df = pd.DataFrame(default_hospitals, columns=["hospital", "specialist", "doctor", "phone"])
        df.to_csv(HOSPITALS_FILE, index=False)
    else:
        # Already unna hospitals.csv lo "phone" column ledante add cheddam (old file migration)
        try:
            existing = pd.read_csv(HOSPITALS_FILE, dtype=str)
            if "phone" not in existing.columns:
                existing["phone"] = ""
                existing.to_csv(HOSPITALS_FILE, index=False)
        except pd.errors.EmptyDataError:
            pd.DataFrame(columns=["hospital", "specialist", "doctor", "phone"]).to_csv(HOSPITALS_FILE, index=False)


init_files()


# ---------------------------------------------------------
# SAFE CSV READER (empty ga unna crash avvakunda)
# ---------------------------------------------------------
def safe_read_csv(filepath, columns, dtype=None):
    try:
        df = pd.read_csv(filepath, dtype=dtype)
        return df
    except (pd.errors.EmptyDataError, FileNotFoundError):
        df = pd.DataFrame(columns=columns)
        df.to_csv(filepath, index=False)
        return df

# ---------------------------------------------------------
# SESSION STATE (login status + auth page track cheyadaniki)
# ---------------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "phone" not in st.session_state:
    st.session_state.phone = None
if "auth_page" not in st.session_state:
    st.session_state.auth_page = "login"  # "login" / "signup" / "admin_login" / "hospital_login"
if "user_type" not in st.session_state:
    st.session_state.user_type = None  # "patient" / "admin" / "hospital"
if "hospital_name" not in st.session_state:
    st.session_state.hospital_name = None

st.set_page_config(page_title="Hospital Appointment Booking", page_icon="🏥", layout="centered")

CUSTOM_CSS = """
<style>
    .stApp {
        background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
        color: #f1f5f9;
    }
    section[data-testid="stSidebar"] {
        background-color: #0b1220;
    }
    section[data-testid="stSidebar"] * {
        color: #f1f5f9 !important;
    }
    h1, h2, h3, h4, h5, h6, p, label, span {
        color: #f1f5f9 !important;
    }
    div.stButton > button {
        background: linear-gradient(90deg, #0ea5e9, #22c55e);
        color: white;
        border-radius: 10px;
        border: none;
        padding: 0.55rem 1.2rem;
        font-weight: 600;
        box-shadow: 0 3px 8px rgba(0,0,0,0.35);
        transition: transform 0.15s ease;
    }
    div.stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 5px 12px rgba(0,0,0,0.45);
    }
    input, textarea, .stSelectbox div[data-baseweb="select"] > div {
        border-radius: 8px !important;
        background-color: #1e293b !important;
        color: #f1f5f9 !important;
    }
    div[data-baseweb="popover"], ul[role="listbox"], li[role="option"] {
        background-color: #1e293b !important;
        color: #f1f5f9 !important;
    }
    li[aria-selected="true"] {
        background-color: #0ea5e9 !important;
    }
    .hospital-card {
        background-color: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 14px;
        padding: 1rem 1.2rem;
        margin-top: 0.8rem;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }
    .hospital-card h4 {
        margin: 0 0 0.3rem 0;
    }
    .hospital-phone {
        color: #94a3b8 !important;
        font-size: 0.95rem;
        margin: 0;
    }
    .emergency-btn {
        display: block;
        text-align: center;
        text-decoration: none !important;
        border-radius: 10px;
        padding: 0.6rem 0.5rem;
        font-weight: 700;
        color: white !important;
        box-shadow: 0 3px 8px rgba(0,0,0,0.35);
    }
    .call-btn {
        background: linear-gradient(90deg, #16a34a, #22c55e);
    }
    .whatsapp-btn {
        background: linear-gradient(90deg, #128c7e, #25d366);
    }
    .emergency-btn:hover {
        opacity: 0.9;
    }
    .role-badge {
        display: inline-block;
        background: rgba(14,165,233,0.2);
        border: 1px solid rgba(14,165,233,0.5);
        padding: 0.15rem 0.6rem;
        border-radius: 999px;
        font-size: 0.8rem;
        margin-bottom: 0.5rem;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ---------------------------------------------------------
# LOGOUT BUTTON (sidebar lo, login ayyaka kanipistundi)
# ---------------------------------------------------------
def logout_button():
    if st.session_state.logged_in:
        with st.sidebar:
            role_label = {
                "admin": "Admin",
                "hospital": f"Hospital ({st.session_state.hospital_name})",
                "patient": "Patient",
            }.get(st.session_state.user_type, "")
            st.write(f"👋 Welcome, **{st.session_state.current_user}**")
            if role_label:
                st.markdown(f'<span class="role-badge">{role_label}</span>', unsafe_allow_html=True)
            if st.button("Logout"):
                st.session_state.logged_in = False
                st.session_state.current_user = None
                st.session_state.phone = None
                st.session_state.user_type = None
                st.session_state.hospital_name = None
                st.session_state.auth_page = "login"
                st.rerun()


# ---------------------------------------------------------
# LOGIN PAGE (Patient)
# ---------------------------------------------------------
def login_page():
    st.title("🏥 Hospital Appointment Booking")
    st.subheader("Login")

    name = st.text_input("Name", key="login_name")
    phone = st.text_input("Phone Number", key="login_phone")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login", use_container_width=True):
        if not name or not phone or not password:
            st.error("Deenini nindukovali (Please fill all fields).")
            return

        users = safe_read_csv(USERS_FILE, ["name", "phone", "password"], dtype=str)
        match = users[
            (users["name"].str.strip().str.lower() == name.strip().lower())
            & (users["phone"].astype(str).str.strip() == phone.strip())
            & (users["password"].astype(str) == password)
        ]

        if not match.empty:
            st.session_state.logged_in = True
            st.session_state.user_type = "patient"
            st.session_state.current_user = name.strip()
            st.session_state.phone = phone.strip()
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Name/Phone/Password thappu unnayi. Sign up chesara?")

    st.markdown("---")
    if st.button("New user? Sign Up here", use_container_width=True):
        st.session_state.auth_page = "signup"
        st.rerun()

    st.markdown("###### Hospital or Admin ah?")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🏥 Hospital Login", use_container_width=True):
            st.session_state.auth_page = "hospital_login"
            st.rerun()
    with c2:
        if st.button("🔑 Admin Login", use_container_width=True):
            st.session_state.auth_page = "admin_login"
            st.rerun()


# ---------------------------------------------------------
# SIGN UP PAGE (Patient)
# ---------------------------------------------------------
def signup_page():
    st.title("🏥 Hospital Appointment Booking")
    st.subheader("Sign Up")

    name = st.text_input("Full Name", key="signup_name")
    phone = st.text_input("Phone Number", key="signup_phone")
    password = st.text_input("Create Password", type="password", key="signup_password")

    if st.button("Sign Up", use_container_width=True):
        if not name or not phone or not password:
            st.error("Anni fields nindukovali.")
            return

        if not phone.strip().isdigit() or len(phone.strip()) != 10:
            st.error("Phone number 10 digits undali (valid number pettandi).")
            return

        users = safe_read_csv(USERS_FILE, ["name", "phone", "password"], dtype=str)

        if not users.empty and (users["phone"].astype(str).str.strip() == phone.strip()).any():
            st.error("Ee phone number tho already account undi. Login cheyandi.")
            return

        new_user = pd.DataFrame([[name.strip(), phone.strip(), password]],
                                 columns=["name", "phone", "password"])
        new_user.to_csv(USERS_FILE, mode="a", header=False, index=False)
        st.success("Sign up successful! Login page ki veltunnav...")
        st.session_state.auth_page = "login"
        st.rerun()

    st.markdown("---")
    if st.button("Already have an account? Login", use_container_width=True):
        st.session_state.auth_page = "login"
        st.rerun()


# ---------------------------------------------------------
# ADMIN LOGIN PAGE (fixed email/password - only Add Hospital access)
# ---------------------------------------------------------
def admin_login_page():
    st.title("🏥 Hospital Appointment Booking")
    st.subheader("🔑 Admin Login")
    st.caption("Ee login matrame hospitals/doctors add cheyagalada.")

    email = st.text_input("Admin Email", key="admin_email")
    password = st.text_input("Password", type="password", key="admin_password")

    if st.button("Login as Admin", use_container_width=True):
        if email.strip().lower() == ADMIN_EMAIL.lower() and password == ADMIN_PASSWORD:
            st.session_state.logged_in = True
            st.session_state.user_type = "admin"
            st.session_state.current_user = "Admin"
            st.success("Admin login successful!")
            st.rerun()
        else:
            st.error("Email/Password thappu unnayi.")

    st.markdown("---")
    if st.button("⬅ Back to Login", use_container_width=True):
        st.session_state.auth_page = "login"
        st.rerun()


# ---------------------------------------------------------
# HOSPITAL LOGIN PAGE (admin add chesinapudu create ayye credentials tho)
# ---------------------------------------------------------
def hospital_login_page():
    st.title("🏥 Hospital Appointment Booking")
    st.subheader("🏥 Hospital Login")
    st.caption("Admin mee hospital add chesinappudu icchina Email/Password tho login cheyandi.")

    email = st.text_input("Hospital Email", key="hosp_login_email")
    password = st.text_input("Password", type="password", key="hosp_login_password")

    if st.button("Login as Hospital", use_container_width=True):
        if not email or not password:
            st.error("Email/Password nindukovali.")
            return

        logins = safe_read_csv(HOSPITAL_LOGINS_FILE, ["hospital", "email", "password"], dtype=str)
        match = logins[
            (logins["email"].astype(str).str.strip().str.lower() == email.strip().lower())
            & (logins["password"].astype(str) == password)
        ]

        if not match.empty:
            st.session_state.logged_in = True
            st.session_state.user_type = "hospital"
            st.session_state.hospital_name = match.iloc[0]["hospital"]
            st.session_state.current_user = match.iloc[0]["hospital"]
            st.success("Hospital login successful!")
            st.rerun()
        else:
            st.error("Email/Password thappu unnayi. Admin ni contact cheyandi.")

    st.markdown("---")
    if st.button("⬅ Back to Login", use_container_width=True):
        st.session_state.auth_page = "login"
        st.rerun()


# ---------------------------------------------------------
# ADD HOSPITAL PAGE (Admin only)
# ---------------------------------------------------------
def add_hospital_page():
    st.header("➕ Add New Hospital / Doctor (Admin)")

    hospital = st.text_input("Hospital Name")
    specialist = st.text_input("Specialist (Eg: Cardiology, ENT, Orthopedics...)")
    doctor = st.text_input("Doctor Name")
    phone = st.text_input("Hospital Emergency Number (10 digits)", max_chars=10)

    st.markdown("##### 🔐 Hospital Login Details")
    st.caption("Ee email/password tho aa hospital 'Hospital Login' nunchi login avvachu (appointments chudataniki).")
    hosp_email = st.text_input("Hospital Login Email")
    hosp_password = st.text_input("Hospital Login Password", type="password")

    if st.button("Add Hospital", use_container_width=True):
        if not hospital or not specialist or not doctor or not phone:
            st.error("Anni fields nindukovali (phone number kuda pettandi).")
            return
        if not phone.strip().isdigit() or len(phone.strip()) != 10:
            st.error("Hospital phone number 10 digits undali.")
            return

        new_row = pd.DataFrame([[hospital.strip(), specialist.strip(), doctor.strip(), phone.strip()]],
                                columns=["hospital", "specialist", "doctor", "phone"])
        new_row.to_csv(HOSPITALS_FILE, mode="a", header=False, index=False)

        # Hospital login create cheddam - email/password icchinapudu matrame, already unte skip
        if hosp_email and hosp_password:
            if not hosp_email.strip() or "@" not in hosp_email:
                st.warning("Hospital email valid ga ledu, login create avvaledu (hospital doctor mathram add ayindi).")
            else:
                logins = safe_read_csv(HOSPITAL_LOGINS_FILE, ["hospital", "email", "password"], dtype=str)
                already_exists = False
                if not logins.empty:
                    already_exists = (
                        (logins["hospital"].str.strip().str.lower() == hospital.strip().lower())
                        | (logins["email"].str.strip().str.lower() == hosp_email.strip().lower())
                    ).any()

                if already_exists:
                    st.info("Ee hospital/email tho login already undi, kotha login create cheyaledu.")
                else:
                    new_login = pd.DataFrame([[hospital.strip(), hosp_email.strip(), hosp_password]],
                                              columns=["hospital", "email", "password"])
                    new_login.to_csv(HOSPITAL_LOGINS_FILE, mode="a", header=False, index=False)
                    st.success("Hospital login kuda create ayindi!")

        st.success(f"'{hospital}' - '{doctor}' ({specialist}) add ayindi!")
        st.rerun()

    st.markdown("---")
    st.write("### 🏥 Current Hospitals — Emergency Contact")

    hospitals_df = safe_read_csv(HOSPITALS_FILE, ["hospital", "specialist", "doctor", "phone"], dtype=str)
    if hospitals_df.empty:
        st.info("Ippatiki e hospital add cheyaledu.")
        return

    # Okko hospital ki oka card, andulo call/whatsapp emergency buttons
    unique_hospitals = hospitals_df.drop_duplicates(subset=["hospital"])[["hospital", "phone"]]
    for _, row in unique_hospitals.iterrows():
        h_name = row["hospital"]
        h_phone = str(row["phone"]).strip()
        docs = hospitals_df[hospitals_df["hospital"] == h_name][["specialist", "doctor"]]

        with st.container():
            st.markdown(f"""<div class="hospital-card">
                <h4>🏥 {h_name}</h4>
                <p class="hospital-phone">📞 {h_phone if h_phone and h_phone != 'nan' else 'Not added'}</p>
            </div>""", unsafe_allow_html=True)

            with st.expander("👨‍⚕️ Doctors & Specialists"):
                st.dataframe(docs, use_container_width=True, hide_index=True)

            if h_phone and h_phone != "nan":
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(
                        f'<a href="tel:{h_phone}" target="_blank" class="emergency-btn call-btn">📞 Call Now</a>',
                        unsafe_allow_html=True
                    )
                with c2:
                    wa_text = f"Emergency! Naaku {h_name} lo appointment kavali. Please help."
                    st.markdown(
                        f'<a href="https://wa.me/91{h_phone}?text={wa_text.replace(" ", "%20")}" '
                        f'target="_blank" class="emergency-btn whatsapp-btn">💬 WhatsApp</a>',
                        unsafe_allow_html=True
                    )
            st.markdown("<br>", unsafe_allow_html=True)


# ---------------------------------------------------------
# BOOK APPOINTMENT PAGE (Patient)
# ---------------------------------------------------------
def book_appointment_page():
    st.header("📅 Book an Appointment")

    hospitals_df = safe_read_csv(HOSPITALS_FILE, ["hospital", "specialist", "doctor", "phone"], dtype=str)

    if hospitals_df.empty:
        st.warning("Ippatiki e hospital add cheyaledu. Admin add chesetappativarake wait cheyandi.")
        return

    # ---------------- STEP 1: HOSPITAL SELECTION ----------------
    st.subheader("1️⃣ Select Hospital")
    hospital_list = sorted(hospitals_df["hospital"].unique())
    selected_hospital = st.selectbox("Select Hospital", hospital_list)

    filtered = hospitals_df[hospitals_df["hospital"] == selected_hospital]
    specialist_list = sorted(filtered["specialist"].unique())
    selected_specialist = st.selectbox("Select Specialist", specialist_list)

    filtered_doctor = filtered[filtered["specialist"] == selected_specialist]
    doctor_list = sorted(filtered_doctor["doctor"].unique())
    selected_doctor = st.selectbox("Select Doctor", doctor_list)

    # Selected hospital number (emergency contact + UPI payment kosam use avutundi)
    h_phone = str(filtered["phone"].iloc[0]).strip() if not filtered.empty else ""
    has_hospital_number = bool(h_phone) and h_phone != "nan"

    if has_hospital_number:
        st.markdown('<p class="hospital-phone">🚨 Emergency? Direct ga contact cheyandi:</p>', unsafe_allow_html=True)
        ec1, ec2 = st.columns(2)
        with ec1:
            st.markdown(
                f'<a href="tel:{h_phone}" target="_blank" class="emergency-btn call-btn">📞 Call Now</a>',
                unsafe_allow_html=True
            )
        with ec2:
            wa_text = f"Emergency! Naaku {selected_hospital} lo appointment kavali. Please help."
            st.markdown(
                f'<a href="https://wa.me/91{h_phone}?text={wa_text.replace(" ", "%20")}" '
                f'target="_blank" class="emergency-btn whatsapp-btn">💬 WhatsApp</a>',
                unsafe_allow_html=True
            )
    else:
        st.info("Ee hospital ki emergency number ledu.")

    st.markdown("---")

    # ---------------- STEP 2: PATIENT DETAILS ----------------
    st.subheader("2️⃣ Patient Details")
    pcol1, pcol2 = st.columns(2)
    with pcol1:
        blood_group = st.selectbox("Blood Group", ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"])
    with pcol2:
        weight = st.number_input("Weight (kg)", min_value=1.0, max_value=300.0, step=0.5)

    # Appointment date 1 week mundu varake maathrame open (today to today+7)
    today = date.today()
    max_date = today + timedelta(days=7)
    selected_date = st.date_input(
        "Select Date (only next 7 days allowed)",
        min_value=today,
        max_value=max_date,
        value=today,
    )

    time_slots = [
        "09:00 AM", "09:30 AM", "10:00 AM", "10:30 AM", "11:00 AM", "11:30 AM",
        "02:00 PM", "02:30 PM", "03:00 PM", "03:30 PM", "04:00 PM", "04:30 PM",
    ]
    selected_time = st.selectbox("Select Time Slot", time_slots)

    st.markdown("---")

    # ---------------- STEP 3: UPI PAYMENT ----------------
    st.subheader("3️⃣ Payment (UPI)")
    consultation_fee = 300
    st.write(f"**Consultation Fee: ₹{consultation_fee}**")

    if has_hospital_number:
        hospital_upi_id = f"{h_phone}@upi"
        st.markdown(
            f'<div class="hospital-card"><p class="hospital-phone">'
            f'💳 Paying directly to <b>{selected_hospital}</b><br>UPI ID: <b>{hospital_upi_id}</b></p></div>',
            unsafe_allow_html=True
        )
    else:
        st.warning("Ee hospital ki number ledu kabatti UPI payment automatic ga set avvadu.")

    if st.button("Pay via UPI", use_container_width=True, disabled=not has_hospital_number):
        new_appointment = pd.DataFrame([[
            st.session_state.current_user,
            st.session_state.phone,
            blood_group,
            weight,
            selected_hospital,
            selected_specialist,
            selected_doctor,
            selected_date.strftime("%Y-%m-%d"),
            selected_time,
            "Paid",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ]], columns=[
            "patient_name", "phone", "blood_group", "weight",
            "hospital", "specialist", "doctor",
            "date", "time", "payment_status", "booked_on"
        ])
        new_appointment.to_csv(APPOINTMENTS_FILE, mode="a", header=False, index=False)

        # Payment success ayyaka, hospital ki pampadaniki WhatsApp confirmation details save cheddam
        st.session_state.last_booking = {
            "hospital": selected_hospital,
            "phone": h_phone,
            "patient": st.session_state.current_user,
            "doctor": selected_doctor,
            "specialist": selected_specialist,
            "date": selected_date.strftime("%d-%m-%Y"),
            "time": selected_time,
            "fee": consultation_fee,
        }
        st.success("✅ Payment successful! Appointment booked.")
        st.balloons()

    # ---------------- STEP 4: SEND CONFIRMATION TO HOSPITAL ----------------
    booking = st.session_state.get("last_booking")
    if booking and booking["hospital"] == selected_hospital:
        msg = (
            f"Appointment Confirmed! Patient: {booking['patient']}, "
            f"Doctor: {booking['doctor']} ({booking['specialist']}), "
            f"Date: {booking['date']} at {booking['time']}. "
            f"Fee of ₹{booking['fee']} paid via UPI."
        )
        wa_link = f"https://wa.me/91{booking['phone']}?text={msg.replace(' ', '%20')}"
        st.markdown(
            f'<a href="{wa_link}" target="_blank" class="emergency-btn whatsapp-btn">'
            f'📤 Send Payment Confirmation to Hospital</a>',
            unsafe_allow_html=True
        )


# ---------------------------------------------------------
# MY APPOINTMENTS PAGE (Patient)
# ---------------------------------------------------------
def my_appointments_page():
    st.header("📋 My Appointments")

    appointments_df = safe_read_csv(APPOINTMENTS_FILE, [
        "patient_name", "phone", "blood_group", "weight",
        "hospital", "specialist", "doctor",
        "date", "time", "payment_status", "booked_on"
    ], dtype=str)
    my_appts = appointments_df[appointments_df["phone"] == st.session_state.phone]

    if my_appts.empty:
        st.info("Meeku appointments emi ledu ippatiki.")
    else:
        st.dataframe(my_appts, use_container_width=True)


# ---------------------------------------------------------
# HOSPITAL DASHBOARD PAGE (Hospital login ayyaka appointments chudataniki)
# ---------------------------------------------------------
def hospital_dashboard_page():
    st.header(f"📋 Appointments — {st.session_state.hospital_name}")

    appointments_df = safe_read_csv(APPOINTMENTS_FILE, [
        "patient_name", "phone", "blood_group", "weight",
        "hospital", "specialist", "doctor",
        "date", "time", "payment_status", "booked_on"
    ], dtype=str)
    hosp_appts = appointments_df[appointments_df["hospital"] == st.session_state.hospital_name]

    if hosp_appts.empty:
        st.info("Ee hospital ki appointments emi ledu ippatiki.")
    else:
        st.dataframe(hosp_appts, use_container_width=True)


# ---------------------------------------------------------
# MAIN APP FLOW
# ---------------------------------------------------------
def main():
    if not st.session_state.logged_in:
        if st.session_state.auth_page == "signup":
            signup_page()
        elif st.session_state.auth_page == "admin_login":
            admin_login_page()
        elif st.session_state.auth_page == "hospital_login":
            hospital_login_page()
        else:
            login_page()
    else:
        logout_button()
        st.title("🏥 Hospital Appointment Booking")

        # Admin ki "Add Hospital" matrame kanipistundi
        if st.session_state.user_type == "admin":
            add_hospital_page()

        # Hospital login ki appointments dashboard matrame kanipistundi
        elif st.session_state.user_type == "hospital":
            hospital_dashboard_page()

        # Normal patient ki Book Appointment / My Appointments matrame - Add Hospital ledu
        else:
            menu = st.sidebar.radio(
                "Menu",
                ["Book Appointment", "My Appointments"],
            )

            if menu == "Book Appointment":
                book_appointment_page()
            elif menu == "My Appointments":
                my_appointments_page()


if __name__ == "__main__":
    main()