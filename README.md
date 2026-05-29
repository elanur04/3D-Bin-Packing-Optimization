# 📦 PackOptima: 3D Bin Packing Optimization Web App

PackOptima, **Genetik Algoritma (GA)** ve **Balina Sürü Optimizasyonu (WOA)** gibi modern meta-sezgisel algoritmaları kullanarak 3 Boyutlu Kutu Paketleme (3D Bin Packing) problemini çözen etkileşimli bir web uygulamasıdır.

Uygulama, verilen koli setlerini minimum araç (konteyner) sayısıyla ve maksimum hacim kullanımıyla yerleştirmeyi hedefler.

## ✨ Özellikler

- **🧬 Genetik Algoritma (GA):** Doğal seçilim, çaprazlama ve mutasyon mekanizmalarına dayalı güçlü arama.
- **🐳 Balina Sürü Optimizasyonu (WOA):** Kambur balinaların kabarcık ağıyla helezonik avlanma davranışını simüle eden yenilikçi optimizasyon.
- **📊 Canlı Yakınsama Analizi:** Optimizasyon süreci çalışırken her iki algoritmanın performans gelişimini (fitness eğrisi) gerçek zamanlı grafiklerle izleyin.
- **🧊 3D İnteraktif Görselleştirme:** Elde edilen en iyi koli yerleşim düzenini 3 boyutlu etkileşimli grafiklerle inceleyin.
- **⚙️ Dinamik Parametre Ayarı:** Popülasyon boyutu, nesil sayısı, mutasyon oranı gibi algoritma parametrelerini sol menüden anında değiştirin.

## 🛠️ Teknolojiler

- **[Streamlit](https://streamlit.io/):** Web arayüzü ve uygulama çatısı
- **[Plotly](https://plotly.com/python/):** 2D yakınsama grafikleri ve 3D kutu yerleşimi görselleştirmesi
- **Python:** Çekirdek algoritmalar ve matematiksel modelleme

## 🚀 Kurulum & Çalıştırma (Yerel Bilgisayar İçin)

Projenin kendi bilgisayarınızda çalışabilmesi için sisteminizde Python 3.8+ kurulu olması gereklidir.

1. Depoyu bilgisayarınıza indirin:
   ```bash
   git clone https://github.com/KULLANICI_ADINIZ/3D-Bin-Packing-Optimization.git
   cd 3D-Bin-Packing-Optimization
   ```

2. Gerekli kütüphaneleri yükleyin:
   ```bash
   pip install -r requirements.txt
   ```

3. Uygulamayı başlatın:
   ```bash
   streamlit run app.py
   ```

## ☁️ Cloud Deploy (Google Cloud / Streamlit Cloud)

Bu proje doğrudan **Google Cloud Run** ve **Streamlit Community Cloud** üzerinde yayınlanmaya hazır şekilde tasarlanmıştır. Sunucu üzerinde derlenmesi için gerekli olan `Dockerfile` ve bağımlılık dosyaları (`requirements.txt`) proje kök dizininde yer almaktadır.

---
*Bu proje Elanur Beycan tarafından geliştirilmiştir.*
