import streamlit as st
import os

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

# Dosya Yolu
DOSYA_KLASORU = "yuklenen_briefler"
if not os.path.exists(DOSYA_KLASORU):
    os.makedirs(DOSYA_KLASORU)

# Başlık ve İmza
st.markdown("<h1>📂 Kampanya & Brief Yönetim Portalı <span style='font-size:18px; color:#6c757d; font-weight:400; vertical-align:middle;'>created by yaso®</span></h1>", unsafe_allow_html=True)

# Aciliyet Sıralama Mantığı
ACILIYET_PUANLARI = {"CokAcil": 1, "Kritik": 2, "Onemli": 3, "Normal": 4}
ACILIYET_EMOJILER = {"CokAcil": "🔴 Çok Acil!", "Kritik": "🟠 Kritik", "Onemli": "🟡 Önemli", "Normal": "🟢 Normal"}

# --- AKILLI DOSYA OKUMA SİSTEMİ (GÜNCELLENDİ) ---
def kampanyalari_getir():
    kampanyalar = []
    dosyalar = [f for f in os.listdir(DOSYA_KLASORU) if f.endswith(".pdf")]
    
    for dosya in dosyalar:
        try:
            dosya_saf = dosya.replace(".pdf", "")
            parcalar = dosya_saf.split("_")
            
            # Typo Düzeltici (Onemi yazılırsa Onemli anlar)
            acil_key = parcalar[0]
            if acil_key == "Onemi": 
                acil_key = "Onemli"
            
            # Tam format girildiyse: Aciliyet_Bas_Bit_Ad
            if len(parcalar) >= 4:
                bas = parcalar[1]
                bit = parcalar[2]
                ad = " ".join(parcalar[3:])
            
            # Tarihler eksik girildiyse: Aciliyet_Ad (Örn: Kritik_Rodos.pdf)
            elif len(parcalar) >= 2:
                bas = "Belirtilmedi"
                bit = "Belirtilmedi"
                ad = " ".join(parcalar[1:])
                
            # Hiçbir formata uymuyorsa düz dosya ismi olarak al
            else:
                acil_key = "Normal"
                bas = "-"
                bit = "-"
                ad = dosya_saf

            kampanyalar.append({
                "id": ACILIYET_PUANLARI.get(acil_key, 99),
                "aciliyet_str": ACILIYET_EMOJILER.get(acil_key, "⚪ Belirsiz"),
                "baslangic": bas,
                "bitis": bit,
                "adi": ad,
                "dosya_yolu": os.path.join(DOSYA_KLASORU, dosya),
                "dosya_adi": dosya
            })
        except Exception as e:
            continue
    
    # Aciliyete göre sırala (Önce Çok Acil, sonra Kritik vs.)
    return sorted(kampanyalar, key=lambda x: x["id"])

aktif_isler = kampanyalari_getir()

# --- AJANS GÖRÜNÜMÜ ---
st.divider()
st.header("📋 Aktif Kampanyalar")

is_basina = 12
toplam_is = len(aktif_isler)
toplam_slot = 40

for i in range(toplam_slot):
    if i < toplam_is:
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
        with st.container(border=False):
            st.markdown(f"<div style='border: 1px dashed #d3d3d3; padding: 15px; border-radius: 10px; color: #d3d3d3; text-align: center;'>📄 Boş Slot {i+1} - Brief Bekleniyor</div>", unsafe_allow_html=True)

st.sidebar.info(f"Sistemde toplam {toplam_is} aktif brief bulunmaktadır. Boş kapasite: {toplam_slot - toplam_is}")
