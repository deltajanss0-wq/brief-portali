import streamlit as st
import pandas as pd
import os
import math

# Sayfa Ayarları
st.set_page_config(page_title="Kampanya & Brief Yönetimi", layout="wide")

# CSS: Poppins Font ve Kompakt (Küçültülmüş) Kart Tasarımı
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

    /* Kartların iç boşluklarını daraltarak 12 kampanyanın ekrana daha iyi sığmasını sağladık */
    [data-testid="stVerticalBlockBorderWrapper"] {
        padding: 0.8rem !important;
    }
    </style>
""", unsafe_allow_html=True)

# Dosya Yolları
DOSYA_KLASORU = "yuklenen_briefler"
CSV_DOSYASI = "kampanya_verileri.csv"
MAKS_KAMPANYA = 50 # 12'şer listelediğimiz için limiti biraz artırdım

# Doğru Aciliyet Sıralaması (Hiyerarşik)
ACILIYET_LISTESI = ["Çok Acil!", "Kritik", "Önemli", "Normal"]

os.makedirs(DOSYA_KLASORU, exist_ok=True)

# Veri Yükleme
if not os.path.exists(CSV_DOSYASI):
    df = pd.DataFrame(columns=["ID", "Kampanya Adı", "Başlangıç", "Bitiş", "Aciliyet", "Dosya"])
    df.to_csv(CSV_DOSYASI, index=False)

df = pd.read_csv(CSV_DOSYASI)

# Sayfa Durumu Kontrolü (Session State)
if 'mevcut_sayfa' not in st.session_state:
    st.session_state.mevcut_sayfa = 1

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
            aciliyet = col_acil.selectbox("Aciliyet Durumu", ACILIYET_LISTESI)
            
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
        with st.expander(f"⚙️ {row['Kampanya Adı']} ({row['Aciliyet']})"):
            col_ed, col_del = st.columns([4, 1])
            with col_ed:
                y_bas = st.date_input("Başlangıç", pd.to_datetime(row["Başlangıç"]), key=f"eb_{index}")
                y_bit = st.date_input("Bitiş", pd.to_datetime(row["Bitiş"]), key=f"et_{index}")
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
                    d_ad = str(row["Dosya"]).strip()
                    if pd.notna(row["Dosya"]) and d_ad not in ["", "nan"]:
                        eski_yol = os.path.join(DOSYA_KLASORU, os.path.basename(d_ad.replace("\\", "/")))
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
    # --- SIRALAMA MANTIĞI: Aciliyete göre, ardından yeniliğe göre ---
    siralama_kategorisi = pd.CategoricalDtype(categories=ACILIYET_LISTESI, ordered=True)
    df_sirali = df.copy()
    df_sirali["Aciliyet"] = df_sirali["Aciliyet"].astype(siralama_kategorisi)
    # Önce aciliyet (artan), sonra ID (azalan - en yeni ilk)
    df_sirali = df_sirali.sort_values(["Aciliyet", "ID"], ascending=[True, False]).reset_index(drop=True)

    # Sayfalama Hesaplamaları (12 Kampanya)
    is_basina_kampanya = 12
    toplam_kampanya = len(df_sirali)
    toplam_sayfa = math.ceil(toplam_kampanya / is_basina_kampanya)
    
    if st.session_state.mevcut_sayfa > toplam_sayfa:
        st.session_state.mevcut_sayfa = toplam_sayfa
    if st.session_state.mevcut_sayfa < 1:
        st.session_state.mevcut_sayfa = 1

    bas_index = (st.session_state.mevcut_sayfa - 1) * is_basina_kampanya
    bit_index = min(bas_index + is_basina_kampanya, toplam_kampanya)
    gosterilecek_df = df_sirali.iloc[bas_index:bit_index]

    # Kampanya Listesi (Kompakt)
    for index, row in gosterilecek_df.iterrows():
        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([3, 2, 2, 2])
            with c1:
                # Yazı boyutu st.subheader yerine markdown(####) ile küçültüldü
                st.markdown(f"#### 🎯 {row['Kampanya Adı']}")
                if row["Aciliyet"] == "Çok Acil!": r = "🔴"
                elif row["Aciliyet"] == "Kritik": r = "🟠"
                elif row["Aciliyet"] == "Önemli": r = "🟡"
                else: r = "🟢"
                st.markdown(f"**Aciliyet:** {r} {row['Aciliyet']}")
            with c2:
                st.write(f"**Başlangıç:**\n{row['Başlangıç']}")
            with c3:
                st.write(f"**Bitiş:**\n{row['Bitiş']}")
            with c4:
                d_ad = str(row["Dosya"]).strip()
                if pd.notna(row["Dosya"]) and d_ad not in ["", "nan"]:
                    yol = os.path.join(DOSYA_KLASORU, os.path.basename(d_ad.replace("\\", "/")))
                    if os.path.exists(yol):
                        with open(yol, "rb") as f:
                            st.download_button("📥 Brief İndir", f, file_name=f"{row['Kampanya Adı']}.pdf", key=f"dl_ajans_{index}", use_container_width=True)
                    else: st.caption("⚠️ Dosya eksik")
                else: st.caption("⏳ Bekleniyor")

    # --- ALT SAYFALAMA KONTROLÜ ---
    st.write("---")
    p1, p2, p3 = st.columns([1, 2, 1])
    
    with p1:
        if st.session_state.mevcut_sayfa > 1:
            if st.button("⬅️ Önceki Sayfa", use_container_width=True):
                st.session_state.mevcut_sayfa -= 1
                st.rerun()
    
    with p2:
        st.markdown(f"<p style='text-align: center; font-weight: bold; font-size: 16px; margin-bottom: 0;'>Sayfa {st.session_state.mevcut_sayfa} / {toplam_sayfa}</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; font-size: 12px; color: gray;'>Gösterilen iş: {len(gosterilecek_df)} | Toplam iş: {toplam_kampanya}</p>", unsafe_allow_html=True)

    with p3:
        if st.session_state.mevcut_sayfa < toplam_sayfa:
            if st.button("Sonraki Sayfa ➡️", use_container_width=True):
                st.session_state.mevcut_sayfa += 1
                st.rerun()
