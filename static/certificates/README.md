# Certificate Images

Folder ini untuk menyimpan gambar scan/foto sertifikat.

## Cara Menggunakan

1. Simpan gambar sertifikat Anda di folder ini
2. Format nama file yang disarankan:
   - `aws-certified-architect.jpg` - Sertifikat AWS
   - `tensorflow-developer.jpg` - Sertifikat TensorFlow
   - `scrum-master.jpg` - Sertifikat PSM I
   - `toefl-itp.jpg` - Sertifikat TOEFL ITP

3. Update URL gambar di `templates/index.html`:
   - Ganti URL Unsplash dengan: `/static/certificates/nama-file.jpg`
   - Contoh: `'/static/certificates/aws-certified-architect.jpg'`

## Format Gambar yang Disarankan

- Format: JPG, PNG, atau PDF (akan dikonversi)
- Resolusi: Minimal 1200x800 pixels untuk kualitas terbaik
- Ukuran file: Maksimal 2MB per gambar

## Current Status

Saat ini menggunakan placeholder images dari Unsplash. Ganti dengan scan sertifikat asli untuk hasil yang lebih profesional.
