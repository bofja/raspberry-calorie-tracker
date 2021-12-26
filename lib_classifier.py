# Digunakan saat mengklasifikasi jenis makanan
# Masukan berupa gambar makanan, model tensor, dan label tensor

import numpy
import PIL as pillow
import tflite_runtime.interpreter as tflite

class Classifier:
    def __init__(self, model, label, mean = 127.5, std = 127.5):
        self.label = self.__set_label(label)
        self.mean = mean
        self.std = std

        self.interpreter = tflite.Interpreter(model)
        self.interpreter.allocate_tensors()

    def __set_label(self, label):
        # Cek apakah tipe label adalah sejenis array
        if isinstance(label, (list, tuple, set)): pass
        else:
            try:
                # Coba baca label sebagai file
                file = open(label, "r")
                # Simpan kumpulan string pada file label menjadi list
                label = [ baris.strip() for baris in file.readlines() ]
                file.close()
            except:
                # Beri tahu pengguna bila label tidak dapat terdefinisi
                print("Label bukanlah list ataupun file...")
                return None
        # Hilangkan duplikasi dan cek apakah label beranggota > 1
        label = list(dict.fromkeys(label))
        if label > 1: return label
        else: return None

    def klasifikasi(self, gambar):
        tensor_masuk = self.interpreter.get_input_details()
        tensor_keluar = self.interpreter.get_output_details()

        lebar = tensor_masuk[0]["shape"][1]
        tinggi = tensor_masuk[0]["shape"][2]
        gambar = pillow.open(gambar).resize(lebar, tinggi)

        data_masuk = numpy.expand_dims(gambar, axis = 0)
        if tensor_masuk[0]["dtype"] == numpy.float:
            data_masuk = (numpy.float(data_masuk) - self.mean) / self.std

        self.interpreter.set_tensor(tensor_masuk[0]["index"], data_masuk)
        self.interpreter.invoke()

        data_keluar = self.interpreter.get_tensor(tensor_keluar[0]["index"])
        hasil = numpy.squeeze(data_keluar)

        i = hasil.argmax()
        indeks = self.label[i].index(" ")
        return self.label[i][indeks+1:]