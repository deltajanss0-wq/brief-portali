import streamlit as st
import pandas as pd
import os
import math

# Sayfa Ayarları
st.set_page_config(page_title="Kampanya & Brief Yönetimi", layout="wide")

# CSS: Poppins Font ve Modern Tasarım
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
    
    html, body, p, h1, h2, h3, h4, h5, h6, label, li, span.st-emotion-cache-10trblm {
        font-family: 'Poppins', sans-serif !important;
    }
    
    .stButton>button {
        border-radius: 8px;
        font-family: 'Poppins', sans-serif !important;
    }
    </style>
""", unsafe_allow_html=True)

# Dosya Yolları
DOSYA_KLASORU = "yuklenen_briefler"
CSV_DOSYASI = "kampanya_verileri.csv"
MAKS_KAMPANYA = 25
# YENİ LİSTE: Kritik eklendi
ACILIYET_LISTESI = ["Normal", "Önemli", "Kritik", "Çok Acil!"]

os.makedirs(DOSYA_KLASORU, exist_ok=True)

if not os.path.exists(CSV_DOSYASI):
    df = pd.DataFrame(columns=["ID", "Kampanya Adı", "Başlangıç", "Bitiş", "Aciliyet", "Dosya"])
    df.to_csv(CSV_DOSYASI, index=False)

df = pd.read_csv(CSV_DOSYASI)

# Başlık ve İmza
st.markdown("<h1>📂 Kampanya & Brief Yönetim Portalı <span style='font-size:18px; color:#6c757d; font-weight:400; vertical-align:middle;'>created by yaso®</span></h1>", unsafe_allow_html=True)

# --- YÖNETİCİ PANELİ ---
st.sidebar.title("Yönetici Paneli")
sifre = st.sidebar.text_input("Şifre", type="password")
is_admin = (sifre == "13579")

if is_admin:
    st.sidebar.success("Erişim Yetkisi Verildi")
    
    st.header("⚙️ Yeni Kampanya Ekle")
    if len(df) < MAKS_KAMPANYA:
        with st.form("yeni_ekle_form", clear_on_submit=True):
            col_ad, col_acil = st.columns(2)
            k_adi = col_ad.text_input("Kampanya Adı")
            # Güncellenmiş liste burada
            aciliyet = col_acil.selectbox("Aciliyet", ACILIYET_LISTESI)
            
            c_bas, c_bit = st.columns(2)
            baslangic = c_bas.date_input("Başlangıç")
            bitis = c_bit.date_input("Bitiş")
            
            yeni_pdf = st.file_uploader("Brief (PDF)", type=["pdf"])
            
            if st.form_submit_button("Kampanyayı Kaydet"):
                if k_adi:
                    yeni_id = int(df["ID"].max() + 1) if not df.empty else 1
                    dosya_adi = ""
                    if yeni_pdf:
                        dosya_adi = f"kampanya_{yeni_id}_brief.pdf"
                        tam_yol = os.path.join(DOSYA_KLASORU, dosya_adi)
                        with open(tam_yol, "wb") as f:
                            f.write(yeni_pdf.getbuffer())
                    
                    yeni_satir = pd.DataFrame([{"ID": yeni_id, "Kampanya Adı": k_adi, "Başlangıç": baslangic, "Bitiş": bitis, "Aciliyet": aciliyet, "Dosya": dosya_adi}])
                    df = pd.concat([df, yeni_satir], ignore_index=True)
                    df.to_csv(CSV_DOSYASI, index=False)
                    st.success("Yeni kampanya eklendi.")
                    st.rerun()
    else:
        st.warning(f"Maksimum {MAKS_KAMPANYA} kampanya limitine ulaştınız.")

    st.divider()
    st.header("📝 Yönetim ve Silme")
    for index, row in df.iterrows():
        with st.expander(f"⚙️ {row['Kampanya Adı']}"):
            col_ed, col_del = st.columns([4, 1])
            with col_ed:
                y_bas = st.date_input("Başlangıç", pd.to_datetime(row["Başlangıç"]), key=f"eb_{index}")
                y_bit = st.date_input("Bitiş", pd.to_datetime(row["Bitiş"]), key=f"et_{index}")
                # Mevcut değer listede yoksa Normal'i seç
                mevcut_acil = row["Aciliyet"] if row["Aciliyet"] in ACILIYET_LISTESI else "Normal"
                y_acil = st.selectbox("Aciliyet", ACILIYET_LISTESI, index=ACILIYET_LISTESI.index(mevcut_acil), key=f"ea_{index}")
                if st.button("Güncelle", key=f"upd_{index}"):
                    df.at[index, "Başlangıç"], df.at[index, "Bitiş"], df.at[index, "Aciliyet"] = y_bas, y_bit, y_acil
                    df.to_csv(CSV_DOSYASI, index=False)
                    st.success("Güncellendi")
                    st.rerun()
            with col_del:
                st.write("---")
                if st.button("🗑️ SİL", key=f"del_{index}"):
                    dosya_degeri = str(row["Dosya"]).strip()
                    if pd.notna(row["Dosya"]) and dosya_degeri not in ["", "nan"]:
                        eski_yol = os.path.join(DOSYA_KLASORU, os.path.basename(dosya_degeri.replace("\\", "/")))
                        try:
                            if os.path.exists(eski_yol): os.remove(eski_yol)
                        except: pass
                    df = df.drop(index).reset_index(drop=True)
                    df.to_csv(CSV_DOSYASI, index=False)
                    st.rerun()

# --- AJANS GÖRÜNÜMÜ ---
st.divider()
st.header("📋 Aktif Kampanyalar")

if df.empty:
    st.info("Gösterilecek kampanya bulunmuyor.")
else:
    is_basina_kampanya = 5
    toplam_sayfa = math.ceil(len(df) / is_basina_kampanya)
    sayfa = 1
    if toplam_sayfa > 1:
        sayfa = st.sidebar.select_slider("Sayfa Seçin", options=list(range(1, toplam_sayfa + 1)), value=1)
    
    bas_index = (sayfa - 1) * is_basina_kampanya
    gosterilecek_df = df.iloc[bas_index:bas_index + is_basina_kampanya]

    for index, row in gosterilecek_df.iterrows():
        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([3, 2, 2, 2])
            with c1:
                st.subheader(f"🎯 {row['Kampanya Adı']}")
                # Emoji Mantığı Güncellendi
                if row["Aciliyet"] == "Çok Acil!": r = "🔴"
                elif row["Aciliyet"] == "Kritik": r = "🟠"
                elif row["Aciliyet"] == "Önemli": r = "🟡"
                else: r = "🟢"
                st.write(f"**Aciliyet:** {r} {row['Aciliyet']}")
            with c2:
                st.write(f"**Başlangıç:**\n{row['Başlangıç']}")
            with c3:
                st.write(f"**Bitiş:**\n{row['Bitiş']}")
            with c4:
                st.write("**Brief Dosyası:**")
                d_ad = str(row["Dosya"]).strip()
                if pd.notna(row["Dosya"]) and d_ad not in ["", "nan"]:
                    yol = os.path.join(DOSYA_KLASORU, os.path.basename(d_ad.replace("\\", "/")))
                    if os.path.exists(yol):
                        with open(yol, "rb") as f:
                            st.download_button("📥 Brief İndir", f, file_name=f"{row['Kampanya Adı']}.pdf", key=f"dl_{index}", use_container_width=True)
                    else: st.caption("⚠️ Dosya eksik")
                else: st.caption("⏳ Bekleniyor")
