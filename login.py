import streamlit as st
import pandas as pd
import sqlite3
import datetime

# --- SETTING HALAMAN ---
st.set_page_config(
    page_title="Sistem Pengurusan Stor UTMK - IPN JANM",
    page_icon="🏛️",
    layout="wide"
)

# --- REKA BENTUK KORPORAT & RESPONSIF (CUSTOM CSS) ---
st.markdown("""
    <style>
    /* Variabel Skim Warna (Biru, Hitam, Oren) */
    :root {
        --bg-navy: #0F172A;        /* Biru Gelap / Black-Navy */
        --accent-orange: #FF6B00;   /* Oren Korporat */
        --text-dark: #1E293B;       /* Hitam Slate */
        --blue-accent: #2563EB;     /* Biru Terang Accent */
        --bg-card: #FFFFFF;
    }
    
    /* Header Container - Center & Responsive */
    .header-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        background: linear-gradient(135deg, #0F172A 0%, #1E3A8A 100%);
        padding: 20px 15px;
        border-radius: 12px;
        border-bottom: 4px solid var(--accent-orange);
        box-shadow: 0 4px 15px rgba(0,0,0,0.15);
        margin-bottom: 25px;
        color: white;
    }

    /* Susunan Logo & Teks */
    .header-content {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 10px;
    }

    @media (min-width: 768px) {
        .header-content {
            flex-direction: row;
            gap: 20px;
        }
        .header-text {
            text-align: left;
        }
    }

    .header-logo {
        width: 65px;
        height: auto;
        filter: drop-shadow(0px 2px 4px rgba(0,0,0,0.4));
    }
    
    .header-text h3 {
        margin: 0;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 1.5px;
        color: #94A3B8; /* Biru Kelabu Soft */
        text-transform: uppercase;
    }
    
    .header-text h1 {
        margin: 2px 0;
        font-size: 18px;
        font-weight: 700;
        color: #FFFFFF;
        letter-spacing: 0.5px;
    }
    
    .header-text h4 {
        margin: 0;
        font-size: 12px;
        font-weight: 600;
        color: var(--accent-orange);
        letter-spacing: 1px;
    }

    /* Kad Metrik Styling */
    [data-testid="stMetricValue"] {
        font-size: 22px !important;
        font-weight: bold;
        color: var(--bg-navy) !important;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 12px !important;
        color: #475569 !important;
    }
    
    [data-testid="stMetric"] {
        background-color: var(--bg-card);
        padding: 12px 16px;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        border-left: 4px solid var(--accent-orange);
    }
    
    /* Penyesuaian Butang */
    .stButton>button {
        border-radius: 6px;
        font-size: 13px;
        font-weight: 600;
    }

    /* Primary Button Customization (Oren) */
    button[kind="primary"] {
        background-color: var(--accent-orange) !important;
        border-color: var(--accent-orange) !important;
        color: white !important;
    }

    button[kind="primary"]:hover {
        background-color: #E66000 !important;
        border-color: #E66000 !important;
    }

    /* Sembunyikan elemen bawaan Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- FUNGSI HEADER RASMI (TERENGAH & RESPONSIVE) ---
def render_header():
    jata_url = "https://upload.wikimedia.org/wikipedia/commons/2/26/Coat_of_arms_of_Malaysia.svg"
    
    st.markdown(f"""
        <div class="header-container">
            <div class="header-content">
                <img src="{jata_url}" class="header-logo" alt="Jata Negara">
                <div class="header-text">
                    <h3>INSTITUT PERAKAUNAN NEGARA</h3>
                    <h1>JABATAN AKAUNTAN NEGARA MALAYSIA</h1>
                    <h4>SPS-ICT (UTMK)</h4>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# --- PANGKALAN DATA (SQLITE) ---
def init_db():
    conn = sqlite3.connect('stor_utmk.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama_aset TEXT NOT NULL,
            no_siri TEXT UNIQUE NOT NULL,
            kategori TEXT NOT NULL,
            kuantiti INTEGER NOT NULL,
            status TEXT NOT NULL
        )
    ''')
    c.execute("SELECT COUNT(*) FROM items")
    if c.fetchone()[0] == 0:
        sample_data = [
            ("Laptop Dell Latitude 3420", "UTMK-LAP-001", "Laptop", 5, "Tersedia"),
            ("Projector Epson EB-X51", "UTMK-PRJ-002", "Projektor", 2, "Dipinjam"),
            ("Monitor Samsung 24 IPS", "UTMK-MON-003", "Monitor", 10, "Tersedia"),
            ("Kabel HDMI 5m", "UTMK-KBL-004", "Aksesori", 15, "Perlu Baiki")
        ]
        c.executemany("INSERT INTO items (nama_aset, no_siri, kategori, kuantiti, status) VALUES (?, ?, ?, ?, ?)", sample_data)
        conn.commit()
    conn.close()

init_db()

# --- FUNGSI CRUD DATABASE ---
def get_items():
    conn = sqlite3.connect('stor_utmk.db')
    df = pd.read_sql_query("SELECT * FROM items", conn)
    conn.close()
    return df

def add_item(nama, no_siri, kategori, kuantiti, status):
    conn = sqlite3.connect('stor_utmk.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO items (nama_aset, no_siri, kategori, kuantiti, status) VALUES (?, ?, ?, ?, ?)", 
                  (nama, no_siri, kategori, kuantiti, status))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

def update_item(item_id, nama, no_siri, kategori, kuantiti, status):
    conn = sqlite3.connect('stor_utmk.db')
    c = conn.cursor()
    try:
        c.execute('''
            UPDATE items 
            SET nama_aset=?, no_siri=?, kategori=?, kuantiti=?, status=?
            WHERE id=?
        ''', (nama, no_siri, kategori, kuantiti, status, item_id))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

def delete_item(item_id):
    conn = sqlite3.connect('stor_utmk.db')
    c = conn.cursor()
    c.execute("DELETE FROM items WHERE id=?", (item_id,))
    conn.commit()
    conn.close()

# --- DIALOG KEMASKINI (EDIT POP-UP) ---
@st.dialog("✏️ Kemaskini Maklumat Aset")
def edit_dialog(row):
    st.write(f"Mengemaskini Aset: **{row['nama_aset']}**")
    
    kategori_list = ["Laptop", "Desktop", "Monitor", "Projektor", "Aksesori", "Rangkaian"]
    idx_kategori = kategori_list.index(row['kategori']) if row['kategori'] in kategori_list else 0
    
    status_list = ["Tersedia", "Dipinjam", "Perlu Baiki"]
    idx_status = status_list.index(row['status']) if row['status'] in status_list else 0

    with st.form("edit_form"):
        nama = st.text_input("Nama Aset", value=row['nama_aset'])
        no_siri = st.text_input("Nombor Siri", value=row['no_siri'])
        kategori = st.selectbox("Kategori", kategori_list, index=idx_kategori)
        kuantiti = st.number_input("Kuantiti", min_value=1, value=int(row['kuantiti']))
        status = st.selectbox("Status", status_list, index=idx_status)
        
        btn_simpan = st.form_submit_button("Simpan Perubahan", use_container_width=True, type="primary")
        if btn_simpan:
            if update_item(row['id'], nama, no_siri, kategori, kuantiti, status):
                st.success("Maklumat aset berjaya dikemaskini!")
                st.rerun()
            else:
                st.error("Gagal! Nombor siri bertembung dengan aset lain.")

# --- LOGIK LOG MASUK ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user' not in st.session_state:
    st.session_state['user'] = ""

def login(username, password):
    if username == "admin" and password == "utmk123":
        st.session_state['logged_in'] = True
        st.session_state['user'] = "Admin UTMK"
        st.rerun()
    else:
        st.error("Nama pengguna atau kata laluan salah!")

def logout():
    st.session_state['logged_in'] = False
    st.session_state['user'] = ""
    st.rerun()

# --- PAPARAN 1: HALAMAN LOG MASUK ---
if not st.session_state['logged_in']:
    render_header()
    
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("""
            <div style="background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); border-top: 3px solid #FF6B00;">
                <h4 style="text-align: center; color: #0F172A; margin-bottom: 15px; font-size: 16px;">🔒 Log Masuk Sistem</h4>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            username_input = st.text_input("Nama Pengguna (Username)", value="admin")
            password_input = st.text_input("Kata Laluan (Password)", type="password", value="utmk123")
            
            if st.form_submit_button("Log Masuk", use_container_width=True, type="primary"):
                login(username_input, password_input)
            
        st.caption("💡 **Akses Demo:** Username: `admin` | Password: `utmk123`")

# --- PAPARAN 2: PAPAN PEMUKA (DASHBOARD) UTAMA ---
else:
    render_header()

    # Sidebar Navigasi Korporat
    st.sidebar.markdown("### 👤 Pengguna")
    st.sidebar.info(f"**{st.session_state['user']}**\n\nSPS-ICT (UTMK)")
    st.sidebar.markdown("---")
    
    menu = st.sidebar.radio("📌 Menu Utama", ["Papan Pemuka", "Pendaftaran Aset Baharu", "Senarai & Urus Aset"])
    st.sidebar.markdown("---")
    
    if st.sidebar.button("🚪 Log Keluar", use_container_width=True):
        logout()

    df_items = get_items()

    # --- MENU 1: PAPAN PEMUKA ---
    if menu == "Papan Pemuka":
        st.markdown("##### 📊 Ringkasan Eksekutif Aset")
        
        total_items = df_items['kuantiti'].sum()
        total_tersedia = df_items[df_items['status'] == 'Tersedia']['kuantiti'].sum()
        total_dipinjam = df_items[df_items['status'] == 'Dipinjam']['kuantiti'].sum()
        total_rosak = df_items[df_items['status'] == 'Perlu Baiki']['kuantiti'].sum()

        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
        col1.metric("Jumlah Unit", f"{total_items}")
        col2.metric("Tersedia", f"{total_tersedia}")
        col3.metric("Dipinjam", f"{total_dipinjam}")
        col4.metric("Perlu Baiki", f"{total_rosak}")

        st.markdown("<br>", unsafe_allow_html=True)
        
        c_left, c_right = st.columns([1, 1])
        with c_left:
            st.markdown("<h6>📦 Taburan Kategori</h6>", unsafe_allow_html=True)
            kategori_chart = df_items.groupby('kategori')['kuantiti'].sum()
            st.bar_chart(kategori_chart, color="#1E3A8A")

        with c_right:
            st.markdown("<h6>📋 Taburan Status</h6>", unsafe_allow_html=True)
            status_chart = df_items.groupby('status')['kuantiti'].sum()
            st.bar_chart(status_chart, color="#FF6B00")

        st.markdown("---")
        st.markdown("<h6>🔍 Ringkasan Inventori Terkini</h6>", unsafe_allow_html=True)
        st.dataframe(
            df_items[['nama_aset', 'no_siri', 'kategori', 'kuantiti', 'status']], 
            use_container_width=True,
            hide_index=True
        )

    # --- MENU 2: PENDAFTARAN ASET BAHARU ---
    elif menu == "Pendaftaran Aset Baharu":
        st.markdown("##### ➕ Pendaftaran Aset ICT Baharu")
        
        with st.form("add_asset_form", clear_on_submit=True):
            col_a, col_b = st.columns(2)
            with col_a:
                nama_aset = st.text_input("Nama Aset / Peralatan*")
                no_siri = st.text_input("Nombor Siri / Tag Aset (Unik)*")
                kategori = st.selectbox("Kategori", ["Laptop", "Desktop", "Monitor", "Projektor", "Aksesori", "Rangkaian"])
            with col_b:
                kuantiti = st.number_input("Kuantiti Unit", min_value=1, value=1)
                status = st.selectbox("Status Awal", ["Tersedia", "Dipinjam", "Perlu Baiki"])
            
            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button("Daftar Aset Baharu", use_container_width=True, type="primary")
            
            if submitted:
                if nama_aset and no_siri:
                    success = add_item(nama_aset, no_siri, kategori, kuantiti, status)
                    if success:
                        st.success(f"Aset **{nama_aset}** berjaya didaftarkan!")
                        st.rerun()
                    else:
                        st.error("Gagal! Nombor siri telah didaftarkan sebelum ini.")
                else:
                    st.warning("Sila isi ruang bertanda *")

    # --- MENU 3: SENARAI & URUS ASET ---
    elif menu == "Senarai & Urus Aset":
        st.markdown("##### 📑 Senarai & Pengurusan Aset")
        
        search_query = st.text_input("🔍 Carian (Nama Aset / Nombor Siri):")
        filtered_df = df_items
        if search_query:
            filtered_df = df_items[
                df_items['nama_aset'].str.contains(search_query, case=False) | 
                df_items['no_siri'].str.contains(search_query, case=False)
            ]
        
        st.markdown("---")
        
        # Header Table Style
        h1, h2, h3, h4, h5, h6 = st.columns([3, 2, 2, 1, 2, 1.5])
        h1.markdown("**Nama Aset**")
        h2.markdown("**No. Siri**")
        h3.markdown("**Kategori**")
        h4.markdown("**Kuantiti**")
        h5.markdown("**Status**")
        h6.markdown("**Tindakan**")
        st.divider()

        if 'item_deleted' not in st.session_state:
            st.session_state['item_deleted'] = False

        if filtered_df.empty:
            st.info("Tiada rekod aset dijumpai.")
        else:
            for _, row in filtered_df.iterrows():
                c1, c2, c3, c4, c5, c6 = st.columns([3, 2, 2, 1, 2, 1.5])
                c1.write(f"**{row['nama_aset']}**")
                c2.write(f"`{row['no_siri']}`")
                c3.write(row['kategori'])
                c4.write(row['kuantiti'])
                
                # Indicator Status
                if row['status'] == 'Tersedia':
                    c5.markdown("🟢 **Tersedia**")
                elif row['status'] == 'Dipinjam':
                    c5.markdown("🟡 **Dipinjam**")
                else:
                    c5.markdown("🔴 **Perlu Baiki**")
                
                # Action Buttons
                btn_col1, btn_col2 = c6.columns(2)
                
                if btn_col1.button("✏️", key=f"edit_{row['id']}", help="Kemaskini"):
                    edit_dialog(row)

                with btn_col2:
                    with st.popover("🗑️", help="Padam"):
                        st.write("Padam rekod ini?")
                        if st.button("Ya, Padam", key=f"del_confirm_{row['id']}", type="primary"):
                            delete_item(row['id'])
                            st.toast(f"Aset '{row['nama_aset']}' telah dipadam.")
                            st.session_state['item_deleted'] = True
                            st.rerun()

        if st.session_state['item_deleted']:
            st.session_state['item_deleted'] = False
            st.rerun()
