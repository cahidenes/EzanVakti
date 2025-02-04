# <img src="icons/icon.svg" alt="icon" width="30"/> Ezan Vakti

Diyanet İşleri Başkanlığı tarafından yayınlanan ezan vakitlerini gösteren bir GTK uygulamasıdır.

![vakitler](screenshots/vakitler.png)

## Kurulum

    flatpak install com.cahidenes.EzanVakti

## Özellikler

### Konum Seçimi

![ayarlar](screenshots/ayarlar.png)

### Görev Çubuğu İkonu

Uygulama çalıştırdığında bir sonraki vakte kalan dakika görev çubuğunda ikon olarak gösterilir.

![tray ikonu](screenshots/tray_icon.png)

Kalan dakika 3 farklı şekilde gösterilebilir:

#### Dakika Modu: <img src="icons/12.svg" width="20"/>

Sadece kalan dakika gösterilir. Vaktin üzerinden 9 dakikaya kadar geçmişse - dakika olarak gösterebilir: <img src="icons/-5.svg" width="20"/>

**-9** ile **99 (1:39)** arasındaki değerleri gösterebilir.

#### Saat:Dakika Modu: <img src="icons/1:23.svg" width="20"/>

Saat ve dakika birlikte gösterilir. 

**1:00** ile **9:59** arasındaki değerleri gösterebilir.

#### Saat Modu: <img src="icons/3:.svg" width="20"/>

Sadece saat gösterilir. 3:00 ile 3:59 arasındaki değerler 3: olarak gösterilir.

**1:00** ile **23:59** arasındaki değerleri gösterebilir.

> Hangi dakika değerlerinde hangi modun gösterileceği ayarlardan belirlenebilir.
 
https://github.com/eminfedar/vaktisalah-gtk-rs ilham alınarak yapılmıştır.