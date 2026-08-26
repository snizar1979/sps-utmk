import streamlit as st
import pandas as pd
import sqlite3
import datetime

# --- SETTING HALAMAN ---
st.set_page_config(
    page_title="Sistem Pengurusan Stor UTMK",
    page_icon="🖥️",
    layout="wide"
)

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
        
        btn_simpan = st.form_submit_button("Simpan Perubahan", use_container_width=True)
        if btn_simpan:
            if update_item(row['id'], nama, no_siri, kategori, kuantiti, status):
                st.success("Maklumat aset berjaya dikemaskini!")
                st.rerun()
            else:
                st.error("Gagal! Nombor siri bertembung dengan aset lain.")

# --- LOGIK LOG MASUK (AUTHENTICATION) ---
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
    st.markdown("<h2 style='text-align: center;'>💻 Log Masuk Sistem Pengurusan Stor UTMK</h2>", unsafe_allow_html=True)
    st.write("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.subheader("Sila Masukkan Kredensial Admin")
        username_input = st.text_input("Nama Pengguna (Username)", value="admin")
        password_input = st.text_input("Kata Laluan (Password)", type="password", value="utmk123")
        
        if st.button("Log Masuk", use_container_width=True):
            login(username_input, password_input)
            
        st.info("💡 **Nota Demonstrasi:** Username default = `admin`, Password default = `utmk123`")

# --- PAPARAN 2: PAPAN PEMUKA (DASHBOARD) UTAMA ---
else:
    st.sidebar.title(f"👤 {st.session_state['user']}")
    menu = st.sidebar.radio("Navigasi Menu", ["Papan Pemuka", "Pendaftaran Aset Baharu", "Senarai & Urus Aset"])
    st.sidebar.write("---")
    if st.sidebar.button("Log Keluar", use_container_width=True):
        logout()

    st.title("🖥️ Papan Pemuka Pengurusan Stor UTMK")
    st.caption("Sistem Pemantauan Aset dan Peralatan ICT Unit Teknologi Maklumat")
    st.write("---")

    df_items = get_items()

    # --- MENU 1: PAPAN PEMUKA ---
    if menu == "Papan Pemuka":
        total_items = df_items['kuantiti'].sum()
        total_tersedia = df_items[df_items['status'] == 'Tersedia']['kuantiti'].sum()
        total_dipinjam = df_items[df_items['status'] == 'Dipinjam']['kuantiti'].sum()
        total_rosak = df_items[df_items['status'] == 'Perlu Baiki']['kuantiti'].sum()

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Jumlah Unit Aset", total_items)
        col2.metric("Stok Tersedia", total_tersedia)
        col3.metric("Sedang Dipinjam", total_dipinjam)
        col4.metric("Perlu Baiki", total_rosak)

        st.write("### 📊 Taburan Aset Mengikut Kategori")
        kategori_chart = df_items.groupby('kategori')['kuantiti'].sum()
        st.bar_chart(kategori_chart)

        st.write("### 📦 Ringkasan Stok Terkini")
        st.dataframe(df_items[['nama_aset', 'no_siri', 'kategori', 'kuantiti', 'status']], use_container_width=True)

    # --- MENU 2: PENDAFTARAN ASET BAHARU ---
    elif menu == "Pendaftaran Aset Baharu":
        st.subheader("➕ Tambah Aset ICT Baharu ke Stor")
        
        with st.form("add_asset_form", clear_on_submit=True):
            nama_aset = st.text_input("Nama Aset / Peralatan")
            no_siri = st.text_input("Nombor Siri / Tag Aset (Mesti Unik)")
            kategori = st.selectbox("Kategori", ["Laptop", "Desktop", "Monitor", "Projektor", "Aksesori", "Rangkaian"])
            kuantiti = st.number_input("Kuantiti", min_value=1, value=1)
            status = st.selectbox("Status Initial", ["Tersedia", "Dipinjam", "Perlu Baiki"])
            
            submitted = st.form_submit_button("Simpan Aset Baharu")
            
            if submitted:
                if nama_aset and no_siri:
                    success = add_item(nama_aset, no_siri, kategori, kuantiti, status)
                    if success:
                        st.success(f"Aset **{nama_aset}** berjaya didaftarkan!")
                        st.rerun()
                    else:
                        st.error("Gagal! Nombor siri ini sudah wujud dalam sistem.")
                else:
                    st.warning("Sila isi semua ruang yang wajib.")

    # --- MENU 3: SENARAI & URUS ASET ---
    elif menu == "Senarai & Urus Aset":
        st.subheader("📑 Senarai Penuh & Pengurusan Aset")
        
        search_query = st.text_input("🔍 Cari mengikut Nama Aset atau Nombor Siri")
        filtered_df = df_items
        if search_query:
            filtered_df = df_items[
                df_items['nama_aset'].str.contains(search_query, case=False) | 
                df_items['no_siri'].str.contains(search_query, case=False)
            ]
        
        st.write("---")
        
        # Header Table Manual
        h1, h2, h3, h4, h5, h6 = st.columns([3, 2, 2, 1, 2, 2])
        h1.markdown("**Nama Aset**")
        h2.markdown("**No. Siri**")
        h3.markdown("**Kategori**")
        h4.markdown("**Kuantiti**")
        h5.markdown("**Status**")
        h6.markdown("**Tindakan**")
        st.divider()

        # Flag pemadaman di peringkat session state
        if 'item_deleted' not in st.session_state:
            st.session_state['item_deleted'] = False

        # Paparan setiap baris data bersama butang tindakan
        if filtered_df.empty:
            st.info("Tiada rekod aset dijumpai.")
        else:
            for _, row in filtered_df.iterrows():
                c1, c2, c3, c4, c5, c6 = st.columns([3, 2, 2, 1, 2, 2])
                c1.write(row['nama_aset'])
                c2.write(f"`{row['no_siri']}`")
                c3.write(row['kategori'])
                c4.write(row['kuantiti'])
                
                # Warna Lencana Status
                if row['status'] == 'Tersedia':
                    c5.caption("🟢 Tersedia")
                elif row['status'] == 'Dipinjam':
                    c5.caption("🟡 Dipinjam")
                else:
                    c5.caption("🔴 Perlu Baiki")
                
                # Lajur Butang Tindakan
                btn_col1, btn_col2 = c6.columns(2)
                
                # Butang Edit (Membuka Modal Pop-up)
                if btn_col1.button("✏️", key=f"edit_{row['id']}", help="Kemaskini Aset"):
                    edit_dialog(row)

                # Butang Padam (Menggunakan Popover Pengesahan)
                with btn_col2:
                    with st.popover("🗑️", help="Padam Aset"):
                        st.write("Padam rekod ini?")
                        if st.button("Ya, Padam", key=f"del_confirm_{row['id']}", type="primary"):
                            delete_item(row['id'])
                            st.toast(f"Aset '{row['nama_aset']}' telah dipadam.")
                            st.session_state['item_deleted'] = True
                            st.rerun()

        # Lakukan pemuatan semula peringkat aplikasi jika ada rekod yang dipadam
        if st.session_state['item_deleted']:
            st.session_state['item_deleted'] = False
            st.rerun()
