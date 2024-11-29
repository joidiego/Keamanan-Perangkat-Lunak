#Nama :  Joi Diego Napitupulu
#NIM : 11322034

import numpy as np
import pywt
from PIL import Image
import os
from tkinter import Tk, Label, Button, Entry, filedialog, messagebox

# Fungsi untuk menyisipkan pesan
def hide_message_gui(input_image_path, message):
    try:
        # Dapatkan direktori dan nama file input
        directory, filename = os.path.split(input_image_path)
        output_filename = f"FileRahasia_{os.path.splitext(filename)[0]}.png"
        output_image_path = os.path.join(directory, output_filename)

        # Muat gambar Cover
        cover_image = np.array(Image.open(input_image_path))

        # Ubah gambar sampel menjadi ruang warna YCbCr
        cover_image_ycbcr = np.array(Image.fromarray(cover_image).convert('YCbCr'))

        # Ekstrak saluran Y untuk komponen pencahayaan
        y_channel = cover_image_ycbcr[:, :, 0]

        # Lakukan Integer Wavelet Transform (IWT) pada saluran Y
        coeffs = pywt.dwt2(y_channel, 'haar')
        LL, (LH, HL, HH) = coeffs

        # Ubah pesan menjadi biner
        binary_message = ''.join(format(ord(char), '08b') for char in message)

        # Periksa apakah ukuran pesan melebihi kapasitas maksimum
        max_capacity = LH.size
        if len(binary_message) > max_capacity:
            raise ValueError('Ukuran pesan melebihi kapasitas maksimum')

        # Sembunyikan pesan di subband LH
        modified_LH = LH.flatten()
        for i, bit in enumerate(binary_message):
            modified_LH[i] = int(modified_LH[i]) | int(bit)

        # Bentuk ulang subband LH yang dimodifikasi
        modified_LH = np.reshape(modified_LH, LH.shape)

        # Lakukan Inverse Integer Wavelet Transform (IIWT)
        modified_coeffs = (LL, (modified_LH, HL, HH))
        modified_y_channel = pywt.idwt2(modified_coeffs, 'haar')

        # Update Y channel di gambar YCbCr
        stego_image_ycbcr = np.copy(cover_image_ycbcr)
        stego_image_ycbcr[:, :, 0] = modified_y_channel

        # Ubah gambar YCbCr kembali ke ruang warna RGB
        stego_image = Image.fromarray(stego_image_ycbcr, 'YCbCr').convert('RGB')

        # Simpan gambar stego
        stego_image.save(output_image_path)
        messagebox.showinfo("Sukses", f"Pesan berhasil disembunyikan! File disimpan sebagai: {output_filename}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Fungsi untuk mengekstrak pesan
def extract_message_gui(input_image_path):
    try:
        # Muat gambar stego
        stego_image = np.array(Image.open(input_image_path))

        # Ubah gambar stego menjadi ruang warna YCbCr
        stego_image_ycbcr = np.array(Image.fromarray(stego_image).convert('YCbCr'))

        # Ekstrak saluran Y yang dimodifikasi
        modified_y_channel = stego_image_ycbcr[:, :, 0]

        # Lakukan Integer Wavelet Transform (IWT) pada saluran Y yang dimodifikasi
        coeffs = pywt.dwt2(modified_y_channel, 'haar')
        LL, (LH, HL, HH) = coeffs

        # Ekstrak pesan tersembunyi dari subband LH
        binary_message = ''
        for pixel in LH.flatten():
            bit = int(pixel) & 1
            binary_message += str(bit)

        # Ubah pesan biner menjadi ASCII
        message = ''
        for i in range(0, len(binary_message), 8):
            byte = binary_message[i:i + 8]
            try:
                message += chr(int(byte, 2))
            except ValueError:
                break

        messagebox.showinfo("Pesan Terdeteksi", f"Pesan yang disembunyikan: {message}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Fungsi untuk memilih file input
def select_file(entry_widget):
    filepath = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
    if filepath:
        entry_widget.delete(0, 'end')
        entry_widget.insert(0, filepath)

# GUI utama
root = Tk()
root.title("Steganografi DWT")

# Input path
Label(root, text="Path Gambar Input:").grid(row=0, column=0, padx=10, pady=5)
entry_input_path = Entry(root, width=50)
entry_input_path.grid(row=0, column=1, padx=10, pady=5)
Button(root, text="Pilih File", command=lambda: select_file(entry_input_path)).grid(row=0, column=2, padx=10, pady=5)

# Secret message
Label(root, text="Pesan Rahasia:").grid(row=1, column=0, padx=10, pady=5)
entry_secret_message = Entry(root, width=50)
entry_secret_message.grid(row=1, column=1, padx=10, pady=5)

# Buttons
Button(root, text="Sisipkan Pesan", command=lambda: hide_message_gui(entry_input_path.get(), entry_secret_message.get())).grid(row=2, column=0, columnspan=3, pady=10)
Button(root, text="Ekstrak Pesan", command=lambda: extract_message_gui(entry_input_path.get())).grid(row=3, column=0, columnspan=3, pady=10)

# Run GUI
root.mainloop()
