import streamlit as st
import pandas as pd
import os
import math

# Sayfa Ayarları
st.set_page_config(page_title="Kampanya & Brief Yönetimi", layout="wide")

# CSS: Sadece fontları ayarlıyoruz, tasarımı Streamlit'in kendi kutularına bırakıyoruz
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
    
    # 1. KAMPANYA EKLEME
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
                    dosya_adi = ""
                    
                    if yeni_pdf:
                        dosya_adi = f"kampanya_{yeni_id}_brief.pdf"
                        tam_yol = os.path.join(DOSYA_KLASORU, dosya_adi)
                        with open(tam_yol, "wb") as f:
                            f.write(yeni_pdf.getbuffer())
                    
                    # Artık sadece dosyanın adını kaydediyoruz, tam yolu değil
                    yeni_satir = pd.DataFrame([{"ID": yeni_id, "Kampanya Adı": k_adi, "Başlangıç": baslangic, "Bitiş": bitis, "Aciliyet": aciliyet, "Dosya": dosya_adi}])
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
                    dosya_degeri = str(row["Dosya"]).strip()
                    if pd.notna(row["Dosya"]) and dosya_degeri != "" and dosya_degeri != "nan":
                        eski_dosya_adi = os.path.basename(dosya_degeri.replace("\\", "/"))
                        silinecek_yol = os.path.join(DOSYA_KLASORU, eski_dosya_adi)
                        try:
                            if os.path.exists(silinecek_yol):
                                os.remove(silinecek_yol)
                        except Exception:
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
        # HTML DİV YERİNE STREAMLIT'İN KENDİ DÜZENLİ KUTULARINI KULLANIYORUZ
        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([3, 2, 2, 2])
            
            with c1:
                st.subheader(f"🎯 {row['Kampanya Adı']}")
                r = "🔴" if row["Aciliyet"] == "Çok Acil!" else "🟡" if row["Aciliyet"] == "Önemli" else "🟢"
                st.write(f"**Aciliyet:** {r} {row['Aciliyet']}")
            
            with c2:
                st.write(f"**Başlangıç:**")
                st.write(f"{row['Başlangıç']}")
                
            with c3:
                st.write(f"**Bitiş:**")
                st.write(f"{row['Bitiş']}")
            
            with c4:
                st.write("**Brief Dosyası:**")
                dosya_degeri = str(row["Dosya"]).strip()
                
                # Hem boş mu diye bakıyoruz hem de NaN metni mi diye kontrol ediyoruz
                if pd.notna(row["Dosya"]) and dosya_degeri != "" and dosya_degeri != "nan":
                    # Windows/Linux karmaşasını çözen kısım:
                    gercek_dosya_adi = os.path.basename(dosya_degeri.replace("\\", "/"))
                    okunacak_yol = os.path.join(DOSYA_KLASORU, gercek_dosya_adi)
                    
                    if os.path.exists(okunacak_yol):
                        with open(okunacak_yol, "rb") as f:
                            st.download_button(
                                label="📥 Brief İndir", 
                                data=f, 
                                file_name=f"{row['Kampanya Adı']}.pdf", 
                                mime="application/pdf",
                                key=f"dl_{index}",
                                use_container_width=True
                            )
                    else:
                        st.caption("⚠️ Dosya sunucuda yok")
                else:
                    st.caption("⏳ Brief Bekleniyor")
