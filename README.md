# 🤖 Discord Auto Poster Selfbot

Auto-poster ini akan mengirim pesan otomatis ke channel Discord dengan delay dan konfigurasi yang kamu atur sendiri.

---

## 🚀 Cara Menggunakan

### 1. Clone atau Download Repo
```bash
git clone https://github.com/namakuhans/TRASH-AUTOPOST-LMFAO.com
cd discord-auto-poster
```

Atau download zip:
- Klik **Code > Download ZIP**
- Extract foldernya

---

### 2. Install Dependency
```bash
pip install -r requirements.txt
```

---

### 3. Siapkan Konfigurasi
Salin file `teks.example.json` menjadi `teks.json`:
```bash
cp teks.example.json teks.json
```

Lalu edit `teks.json` dan isi:
- `token` Discord kamu
- `webhook_url` untuk log
- `channel` dan pesan

---

### 4. Jalankan Bot
```bash
python main.py
```

---

## ⛔️ Jangan Lupa!
- Jangan bagikan token Discord kamu ke siapa pun.
- File `teks.json` tidak akan ikut keupload (lihat `.gitignore`).

---

## 📷 Preview Log
Auto poster akan mengirim log embed seperti ini ke webhook kamu setiap kali mengirim pesan:

![preview](https://cdn.discordapp.com/attachments/1334163100974452756/1372259788762644592/IMG_20250515_000952.jpg?ex=68262004&is=6824ce84&hm=2f0d8c9757ed2c45ba3202e6a72b78c9304ee669185faae1597950e9ddf02797&)

---

## 👨‍💼 Dibuat Oleh
**iHannsy** × **NamiKulo.jS**
