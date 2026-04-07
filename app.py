import streamlit as st
import os
import math

# Sayfa Ayarları
st.set_page_config(page_title="Kampanya & Brief Yönetimi", layout="wide")

# CSS: Poppins Font ve Kompakt Tasarım
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
    html, body, p, h1, h2, h3, h4, h5, h6, label, li {
        font-family: 'Poppins', sans-serif !important;
    }
    .stButton>button { border-radius: 8px; font-family: 'Poppins', sans-serif !important; }
    </style>
""", unsafe_allow_html=True)

# Dosya Yolu (GitHub klasörünle aynı olmalı)
DOSYA_KLASORU = "yuklenen_briefler"
if not os.path.exists(DOSYA_KLASORU):
    os.makedirs(DOSYA_KLASORU)

# Başlık ve İmza
st.markdown("<h1>📂 Kampanya & Brief Yönetim Portalı <span style='font-size:18px; color:#6c757d; font-weight:400; vertical-align:middle;'>created by yaso®</span></h1>", unsafe_allow_html=True)

# Aciliyet Sıralama Mantığı
ACILIYET_PUANLARI = {"CokAcil": 1, "Kritik": 2, "Onemli": 3, "Normal": 4}
ACILIYET_EMOJILER = {"CokAcil": "🔴 Çok Acil!", "Kritik": "🟠 Kritik", "Onemli": "🟡 Önemli", "Normal": "🟢 Normal"}

# --- DOSYALARI OKUMA VE KAMPANYALARI OLUŞTURMA ---
def kampanyalari_getir():
    kampanyalar = []
    dosyalar = [f for f in os.listdir(DOSYA_KLASORU) if f.endswith(".pdf")]
    
    for dosya in dosyalar:
        try:
            # Dosya adını parçala: Aciliyet_Bas_Bit_Ad.pdf
            parcalar = dosya.replace(".pdf", "").split("_")
            if len(parcalar) >= 4:
                acil_key = parcalar[0]
                kampanyalar.append({
                    "id": ACILIYET_PUANLARI.get(acil_key, 99),
                    "aciliyet_str": ACILIYET_EMOJILER.get(acil_key, "⚪ Belirsiz"),
                    "baslangic": parcalar[1],
                    "bitis": parcalar[2],
                    "adi": " ".join(parcalar[3:]),
                    "dosya_yolu": os.path.join(DOSYA_KLASORU, dosya),
                    "dosya_adi": dosya
                })
        except:
            continue
    
    # Aciliyete göre sırala
    return sorted(kampanyalar, key=lambda x: x["id"])

aktif_isler = kampanyalari_getir()

# --- AJANS GÖRÜNÜMÜ ---
st.divider()
st.header("📋 Aktif Kampanyalar")

# Sayfalama: 12 iş per sayfa
is_basina = 12
toplam_is = len(aktif_isler)
toplam_slot = 40 # İstediğin 40 boşluk

# Mevcut işleri listele
for i in range(toplam_slot):
    if i < toplam_is:
        # Aktif Kampanya Kartı
        is_verisi = aktif_isler[i]
        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([3, 2, 2, 2])
            with c1:
                st.markdown(f"#### 🎯 {is_verisi['adi']}")
                st.write(f"**Durum:** {is_verisi['aciliyet_str']}")
            with c2:
                st.write(f"**Başlangıç:**\n{is_verisi['baslangic']}")
            with c3:
                st.write(f"**Bitiş:**\n{is_verisi['bitis']}")
            with c4:
                with open(is_verisi['dosya_yolu'], "rb") as f:
                    st.download_button("📥 Brief İndir", f, file_name=is_verisi['dosya_adi'], key=f"dl_{i}", use_container_width=True)
    else:
        # Boş Slot Görünümü
        with st.container(border=False):
            st.markdown(f"<div style='border: 1px dashed #d3d3d3; padding: 15px; border-radius: 10px; color: #d3d3d3; text-align: center;'>📄 Boş Slot {i+1} - Brief Bekleniyor</div>", unsafe_allow_html=True)

st.sidebar.info(f"Sistemde toplam {toplam_is} aktif brief bulunmaktadır. Boş kapasite: {toplam_slot - toplam_is}")
