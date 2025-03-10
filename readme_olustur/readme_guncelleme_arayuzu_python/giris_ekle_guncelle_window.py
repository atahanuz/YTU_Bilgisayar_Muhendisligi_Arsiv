from yazarin_notlari_duzenle_window import YazarinNotlariWindow
from degiskenler import *
from PyQt5.QtWidgets import (
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QDesktopWidget,
    QHBoxLayout,
    QDialog,
    QVBoxLayout,
    QTextEdit,
    QInputDialog,
)
from metin_islemleri import kisaltMetin
import json
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
import re


class GirisEkleGuncelleWindow(YazarinNotlariWindow):
    def __init__(self, parent):
        super().__init__(parent)

    def initUI(self):
        super().initUI()
        baslik = self.data.get(BASLIK, VARSAYILAN_GIRIS_BASLIK)
        aciklama = self.data.get(ACIKLAMA, VARSAYILAN_GIRIS_ACIKLAMA)
        self.baslikBtn.setText(kisaltMetin(baslik))
        self.baslikBtn.setToolTip(baslik)
        self.aciklama_label = QLabel("Açıklama", self)
        self.aciklama_label.setAlignment(Qt.AlignCenter)
        self.mainLayout.insertWidget(3, self.aciklama_label)
        self.aciklama_duzenle_btn = QPushButton(kisaltMetin(aciklama), self)
        self.aciklama_duzenle_btn.setStyleSheet(ACIKLAMA_BUTON_STILI)
        self.aciklama_duzenle_btn.setToolTip(
            aciklama
        )  # Tam metni araç ipucu olarak ekle
        self.aciklama_duzenle_btn.clicked.connect(
            lambda: self.aciklamaDuzenle(ACIKLAMA)
        )
        self.mainLayout.insertWidget(4, self.aciklama_duzenle_btn)
        self.ekleBtn.setText("İçindekiler Ekle")
        self.setWindowTitle("Giriş Güncelleme")
        if os.path.exists(SELCUKLU_ICO_PATH):
            self.setWindowIcon(QIcon(SELCUKLU_ICO_PATH))

    def ilklendir(self):
        ilklendirildi = False
        if ICINDEKILER not in self.data:
            self.data[ICINDEKILER] = []
            ilklendirildi = True
        if BASLIK not in self.data:
            self.data[BASLIK] = VARSAYILAN_GIRIS_BASLIK
            ilklendirildi = True
        if ACIKLAMA not in self.data:
            self.data[ACIKLAMA] = VARSAYILAN_GIRIS_ACIKLAMA
            ilklendirildi = True
        return ilklendirildi

    def notlariYukle(self):
        self.data = self.jsonDosyasiniYukle()
        try:
            icindekiler_sayisi = len(self.data[ICINDEKILER])  # Not sayısını hesapla
            self.notSayisiLabel.setText(
                f"Toplam {icindekiler_sayisi} içindekiler"
            )  # Not sayısını etikette güncelle

            for idx, not_ in enumerate(self.data[ICINDEKILER]):
                btn = QPushButton(
                    f"İçindekiler {idx + 1}: {kisaltMetin(not_)}", self.scrollWidget
                )  # İlk 30 karakteri göster
                btn.setToolTip(not_)  # Tam metni araç ipucu olarak ekle
                btn.clicked.connect(lambda checked, i=idx: self.notDuzenle(i))
                self.notlarLayout.addWidget(btn)
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Dosya okunurken bir hata oluştu: {e}")

    def jsonDosyasiniYukle(self):
        try:
            with open(GIRIS_JSON_PATH, "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception as e:
            return json.loads("{}")

    def jsonKaydet(self):
        try:
            with open(GIRIS_JSON_PATH, "w", encoding="utf-8") as file:
                json.dump(self.data, file, ensure_ascii=False, indent=4)
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Dosya yazılırken bir hata oluştu: {e}")

    # Filtreleri temizleme fonksiyonu
    def clearFilters(self, is_clicked=True):
        if is_clicked:
            reply = QMessageBox.question(
                self,
                "Filtreleri Temizle",
                "Filtreleri temizlemek istediğinize emin misiniz?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
        if not is_clicked or reply == QMessageBox.Yes:
            for i in range(self.notlarLayout.count()):
                widget = self.notlarLayout.itemAt(i).widget()
                if isinstance(widget, QPushButton):
                    widget.show()
            self.clearFiltersButton.hide()  # Temizle butonunu gizle
            self.notSayisiLabel.setText(
                f"Toplam {len(self.data[ICINDEKILER])} içindekiler"
            )  # Not sayısını etikette güncelle

    def searchNotes(self, query):
        if not query:
            self.clearFilters(is_clicked=False)
            return
        size = 0
        for idx, not_ in enumerate(self.data[ICINDEKILER]):
            widget = self.notlarLayout.itemAt(idx).widget()
            if isinstance(widget, QPushButton):
                if query.lower() in not_.lower():
                    widget.show()
                    size += 1
                else:
                    widget.hide()
        if size == len(self.data[ICINDEKILER]):
            self.clearFilters(is_clicked=False)
            return
        self.notSayisiLabel.setText(f"{size} içindekiler bulundu")
        if query:
            self.clearFiltersButton.show()
        else:
            self.clearFiltersButton.hide()

    def baslikDuzenle(self):
        self.aciklamaDuzenle(BASLIK)

    def aciklamaDuzenle(self, anahtar):
        eski_aciklama = self.data.get(anahtar, "")
        baslik = "Başlık" if anahtar == BASLIK else "Açıklama"
        yeni_aciklama, ok = QInputDialog.getMultiLineText(
            self, f"{baslik} Düzenle", "Açıklama:", eski_aciklama
        )

        if ok and yeni_aciklama != eski_aciklama:
            self.data[anahtar] = yeni_aciklama
            if baslik == "Başlık":
                self.baslikBtn.setText(kisaltMetin(yeni_aciklama))
                self.baslikBtn.setToolTip(yeni_aciklama)
            else:
                self.aciklama_duzenle_btn.setText(kisaltMetin(yeni_aciklama))
                self.aciklama_duzenle_btn.setToolTip(yeni_aciklama)
            self.kaydet()

    def kaydet(self):
        try:
            with open(GIRIS_JSON_PATH, "w", encoding="utf-8") as file:
                json.dump(self.data, file, ensure_ascii=False, indent=4)
            QMessageBox.information(
                self, "Başarılı", "Açıklama güncellendi ve kaydedildi!"
            )
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Dosya yazılırken bir hata oluştu: {e}")

    def notEkle(self):
        self.duzenlemePenceresi = IcindekilerDuzenleWindow(None, self.data,"",ICINDEKILER, GIRIS_JSON_PATH, self)
        self.duzenlemePenceresi.show()

    def notDuzenle(self, idx):
        self.duzenlemePenceresi = IcindekilerDuzenleWindow(idx, self.data, self.data.get(ICINDEKILER,[""])[idx],ICINDEKILER, GIRIS_JSON_PATH, self)
        self.duzenlemePenceresi.show()


class IcindekilerDuzenleWindow(QDialog):
    def __init__(self, idx, data, metin, key, json_path, parent):
        super().__init__(parent)
        self.parent = parent
        self.idx = idx
        self.setModal(True)
        self.data = data
        self.key = key
        self.json_path = json_path
        eslesme = re.search(capa_deseni, metin)
        self.capa = None
        self.baslik = None
        # eşleşme var mı kontrolü
        if eslesme:
            self.baslik = eslesme.group(1)
            # eşleşme iki tane varsa ikincisi çapa oluyor büyüktür 2 kontrolü
            if eslesme.lastindex > 1:
                self.capa = eslesme.group(2)
        self.initUI()
        if os.path.exists(SELCUKLU_ICO_PATH):
            self.setWindowIcon(QIcon(SELCUKLU_ICO_PATH))

    def initUI(self):
        self.setWindowTitle(
            "İçindekileri Düzenle" if self.idx is not None else "İçindekiler Ekle"
        )
        self.resize(400, 300)
        self.layout = QVBoxLayout(self)
        # başlık için label bileşeni
        self.baslik_label = QLabel("İçerik Başlığı", self)
        self.baslik_label.setAlignment(Qt.AlignCenter)
        self.baslik_label.setToolTip("İçerik başlığı giriniz. (Örneği Hocalar)")
        self.layout.addWidget(self.baslik_label)
        # başlık için line edit bileşeni
        self.baslik_input = QLineEdit(self)
        if self.baslik is not None:
            self.baslik_input.setText(self.baslik)
        self.layout.addWidget(self.baslik_input)
        # başlığa ait çapa için label bileşeni
        self.capa_label = QLabel("İçerik Çapası", self)
        self.capa_label.setAlignment(Qt.AlignCenter)
        self.capa_label.setToolTip(
            "İçerik çapası giriniz. (Örneği hocalar) Çapa, içerik başlığına tıklanınca sayfanın o kısmına gitmek için kullanılır."
        )
        self.layout.addWidget(self.capa_label)
        # başlığa ait çapa için line edit bileşeni
        self.capa_input = QLineEdit(self)
        if self.capa is not None:
            self.capa_input.setText(self.capa)
        self.layout.addWidget(self.capa_input)

        buttonLayout = QHBoxLayout()
        self.kaydetBtn = QPushButton(
            "Değişiklikleri Kaydet" if self.idx is not None else "Ekle", self
        )
        self.kaydetBtn.setStyleSheet(EKLE_BUTONU_STILI)
        self.kaydetBtn.clicked.connect(self.kaydet)
        buttonLayout.addWidget(self.kaydetBtn)

        if self.idx is not None:
            self.silBtn = QPushButton("İçeriği Sil", self)
            self.silBtn.clicked.connect(self.sil)
            self.silBtn.setStyleSheet(SIL_BUTONU_STILI)
            buttonLayout.addWidget(self.silBtn)

        self.layout.addLayout(buttonLayout)
        self.center()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def kaydet(self):
        baslik = self.baslik_input.text().strip()
        if not baslik:
            QMessageBox.warning(self, "Hata", "Başlık boş olamaz!")
            return
        capa = self.capa_input.text().strip()
        if not capa:
            QMessageBox.warning(self, "Hata", "Çapa boş olamaz!")
            return
        yeni_icindekiler = f"[{baslik}]({capa})"
        if self.idx is None:
            self.data[self.key].append(yeni_icindekiler)
        else:
            self.data[self.key][self.idx] = yeni_icindekiler

        self.kaydetVeKapat()

    def sil(self):
        if self.idx is not None:
            del self.data[self.key][self.idx]
            self.kaydetVeKapat()

    def kaydetVeKapat(self):
        try:
            with open(self.json_path, "w", encoding="utf-8") as file:
                json.dump(self.data, file, ensure_ascii=False, indent=4)
            QMessageBox.information(self, "Başarılı", "İçindekiler güncellendi!")
            self.parent.notlariYenile()
            self.is_programmatic_close = True
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Dosya yazılırken bir hata oluştu: {e}")
