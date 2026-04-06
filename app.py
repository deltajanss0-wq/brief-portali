import streamlit as st
import pandas as pd
import os
import math

# Sayfa Ayarları
st.set_page_config(page_title="Kampanya & Brief Yönetimi", layout="wide")

# CSS: Poppins Font ve Modern Kart Tasarımı
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
    
    /* Sadece metin elemanlarını hedef alıyoruz, ikon sınıflarını serbest bırakıyoruz */
    html, body, p, h1, h2, h3, h4, h5, h6, label, li, span.st-emotion-cache-10trblm {
        font-family: 'Poppins', sans-serif !important;
    }
    
    .stButton>button {
        border-radius: 8px;
        font-family: 'Poppins', sans-serif !important;
    }
    
    .ajans-kutu {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #4CAF50;
        margin-bottom: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        font-family: 'Poppins', sans-serif;
    }
    </style>
""", unsafe_allow_html=True)

# Dosya Yolları
DOSYA_KLASORU = "yuklenen_briefler"
CSV_DOSYASI = "kampanya_verileri.csv"
MAKS_KAMPANYA = 25

os.makedirs(DOSYA_KLASORU, exist_ok=True)

# Veriyi Yükle
if not os.path.exists(CSV_DOSYASI):
    df = pd.DataFrame(columns=["ID", "Kampanya Adı", "Başlangıç", "Bitiş", "Aciliyet", "Dosya"])
    df.to_csv(CSV_DOSYASI, index=False)

df = pd.read_csv(CSV_DOSYASI)

# İmzanın Başlığa Eklenmesi
st.markdown("<h1>📂 Kampanya & Brief Yönetim Portalı <span style='font-size:18px; color:#6c757d; font-weight:400; vertical-align:middle;'>created by yaso®</span></h1>", unsafe_allow_html=True)

# --- YÖNETİCİ PANELİ (Giriş) ---
st.sidebar.title("Yönetici Paneli")
sifre = st.sidebar.text_input("Şifre", type="password")
is_admin = (sifre == "13579")

if is_admin:
    st.sidebar.success("Erişim Yetkisi Verildi")
    
    # 1. KAMPANYA EKLEME (LİMİTLİ)
    st.header("⚙️ Yeni Kampanya Ekle")
    if len(df) < MAKS_KAMPANYA:
        with st.form("yeni_ekle_form", clear_on_submit=True):
            col_ad, col_acil = st.columns(2)
            k_adi = col_ad.text_input("Kampanya Adı")
            aciliyet = col_acil.selectbox("Aciliyet", ["Normal", "Önemli", "Çok Acil!"])
            
            c_bas, c_bit = st.columns(2)
            baslangic = c_bas.date_input("Başlangıç")
            bitis = c_bit.date_input("Bitiş")
            
            yeni_pdf = st.file_uploader("Brief (PDF)", type=["pdf"])
            
            if st.form_submit_button("Kampanyayı Kaydet"):
                if k_adi:
                    yeni_id = int(df["ID"].max() + 1) if not df.empty else 1
                    d_yolu = ""
                    if yeni_pdf:
                        d_adi = f"kampanya_{yeni_id}_brief.pdf"
                        d_yolu = os.path.join(DOSYA_KLASORU, d_adi)
                        with open(d_yolu, "wb") as f:
                            f.write(yeni_pdf.getbuffer())
                    
                    yeni_satir = pd.DataFrame([{"ID": yeni_id, "Kampanya Adı": k_adi, "Başlangıç": baslangic, "Bitiş": bitis, "Aciliyet": aciliyet, "Dosya": d_yolu}])
                    df = pd.concat([df, yeni_satir], ignore_index=True)
                    df.to_csv(CSV_DOSYASI, index=False)
                    st.success("Yeni kampanya eklendi.")
                    st.rerun()
    else:
        st.warning(f"Maksimum {MAKS_KAMPANYA} kampanya limitine ulaştınız. Yeni eklemek için eskileri silmelisiniz.")

    # 2. DÜZENLEME VE SİLME
    st.divider()
    st.header("📝 Yönetim ve Silme")
    for index, row in df.iterrows():
        with st.expander(f"⚙️ {row['Kampanya Adı']}"):
            col_ed, col_del = st.columns([4, 1])
            
            with col_ed:
                y_bas = st.date_input("Başlangıç", pd.to_datetime(row["Başlangıç"]), key=f"eb_{index}")
                y_bit = st.date_input("Bitiş", pd.to_datetime(row["Bitiş"]), key=f"et_{index}")
                y_acil = st.selectbox("Aciliyet", ["Normal", "Önemli", "Çok Acil!"], index=["Normal", "Önemli", "Çok Acil!"].index(row["Aciliyet"]), key=f"ea_{index}")
                if st.button("Güncelle", key=f"upd_{index}"):
                    df.at[index, "Başlangıç"], df.at[index, "Bitiş"], df.at[index, "Aciliyet"] = y_bas, y_bit, y_acil
                    df.to_csv(CSV_DOSYASI, index=False)
                    st.success("Güncellendi")
                    st.rerun()
            
            with col_del:
                st.write("---")
                if st.button("🗑️ SİL", key=f"del_{index}", help="Bu kampanyayı kalıcı olarak siler"):
                    if pd.notna(row["Dosya"]) and str(row["Dosya"]).strip() != "" and os.path.exists(str(row["Dosya"])):
                        try:
                            os.remove(str(row["Dosya"]))
                        except Exception as e:
                            pass
                            
                    df = df.drop(index).reset_index(drop=True)
                    df.to_csv(CSV_DOSYASI, index=False)
                    st.error("Kampanya silindi.")
                    st.rerun()

# --- AJANS GÖRÜNÜMÜ VE SAYFALAMA ---
st.divider()
st.header("📋 Aktif Kampanyalar")

if df.empty:
    st.info("Gösterilecek kampanya bulunmuyor.")
else:
    # Sayfalama Mantığı
    is_basina_kampanya = 5
    toplam_sayfa = math.ceil(len(df) / is_basina_kampanya)
    
    sayfa = 1
    
    if toplam_sayfa > 1:
        sayfa = st.sidebar.select_slider("Sayfa Seçin", options=list(range(1, toplam_sayfa + 1)), value=1)
    
    bas_index = (sayfa - 1) * is_basina_kampanya
    bit_index = bas_index + is_basina_kampanya
    gosterilecek_df = df.iloc[bas_index:bit_index]

    st.write(f"Toplam {len(df)} kampanya arasından {bas_index+1}-{min(bit_index, len(df))} arası gösteriliyor.")

    for index, row in gosterilecek_df.iterrows():
        st.markdown(f'<div class="ajans-kutu">', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
        
        c1.markdown(f"### 🎯 {row['Kampanya Adı']}")
        r = "🔴" if row["Aciliyet"] == "Çok Acil!" else "🟡" if row["Aciliyet"] == "Önemli" else "🟢"
        c1.markdown(f"**Durum:** {r} {row['Aciliyet']}")
        
        c2.write(f"**Başlangıç:**\n{row['Başlangıç']}")
        c3.write(f"**Bitiş:**\n{row['Bitiş']}")
        
        with c4:
            if pd.notna(row["Dosya"]) and str(row["Dosya"]).strip() != "" and os.path.exists(str(row["Dosya"])):
                with open(str(row["Dosya"]), "rb") as f:
                    st.download_button("📥 Brief İndir", f, file_name=f"{row['Kampanya Adı']}.pdf", key=f"dl_{index}")
            else:
                st.caption("Brief Henüz Yok")
        st.markdown('</div>', unsafe_allow_html=True)