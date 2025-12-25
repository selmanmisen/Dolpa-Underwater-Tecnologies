from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import QtWebEngineWidgets
import os
import math
import socket
import json
import subprocess
import sys
from styles import *

def resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

def load_config():
    try:
        config_path = resource_path("config.json")
        
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Default config settings
            default_config = {
                "arac_ip": "192.168.1.10",
                "arac_port": 5000,
                "pencere_boyutu": {"width": 960, "height": 587},
                "minimum_boyut": {"width": 800, "height": 500},
                "baglanti_kontrol_araligi": 15000,  # 15 saniye (daha az sık kontrol)
                "datetime_guncelleme_araligi": 1000
            }
            # Create default config file
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=4, ensure_ascii=False)
            return default_config
    except Exception as e:
        print(f"Config yüklenirken hata: {e}")
        # In case of error, return default settings
        return {
            "arac_ip": "192.168.1.10",
            "arac_port": 5000,
            "pencere_boyutu": {"width": 960, "height": 587},
            "minimum_boyut": {"width": 800, "height": 500},
            "baglanti_kontrol_araligi": 15000,  # 15 saniye (daha az sık kontrol)
            "datetime_guncelleme_araligi": 1000
        }

# Global config values
CONFIG = load_config()
ARAC_IP = CONFIG["arac_ip"]
ARAC_PORT = CONFIG["arac_port"]

class ResponsiveMainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = None
    
    def resizeEvent(self, event):
        if self.ui and hasattr(self.ui, 'main_window_width') and hasattr(self.ui, 'main_window_height'):
            # Yeni boyutları al
            new_width = event.size().width()
            new_height = event.size().height()
            
            # Tüm widget'ları yeniden boyutlandır
            self.ui.update_widget_geometries(new_width, new_height)
        
        super().resizeEvent(event)


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        # upload icon
        try:
            icon_path = resource_path("dolpa.ico")
            if os.path.exists(icon_path):
                icon = QtGui.QIcon(icon_path)
                MainWindow.setWindowIcon(icon)
                if hasattr(QtWidgets.QApplication, 'instance'):
                    app = QtWidgets.QApplication.instance()
                    if app:
                        app.setWindowIcon(icon)
            else:
                print(f"İkon dosyası bulunamadı: {icon_path}")
        except Exception as e:
            print(f"İkon yükleme hatası: {e}")
        
        MainWindow.setWindowModality(QtCore.Qt.NonModal)
        
        # Take window size from config
        self.main_window_width = CONFIG["pencere_boyutu"]["width"]
        self.main_window_height = CONFIG["pencere_boyutu"]["height"]
        MainWindow.resize(self.main_window_width, self.main_window_height)
        MainWindow.setMinimumSize(CONFIG["minimum_boyut"]["width"], CONFIG["minimum_boyut"]["height"])
        
        MainWindow.setAutoFillBackground(False)
        MainWindow.setTabShape(QtWidgets.QTabWidget.Rounded)
        MainWindow.setUnifiedTitleAndToolBarOnMac(False)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        # Status Bar
        status_bar_height = int(self.main_window_height * 0.068)  # 40px -> %6.8
        self.statusBar = QtWidgets.QWidget(self.centralwidget)
        self.statusBar.setGeometry(QtCore.QRect(0, 0, self.main_window_width, status_bar_height))
        self.statusBar.setStyleSheet("background-color: #0d447d;")
        self.statusBar.setObjectName("statusBar")
        
        # Date time labels 
        datetime_width = int(self.main_window_width * 0.208)  # 200px -> %20.8
        datetime_height = int(status_bar_height * 0.5)  # %50 of status bar
        datetime_y = int(status_bar_height * 0.25)  # %25 of status bar
        self.labelDateTime = QtWidgets.QLabel(self.statusBar)
        self.labelDateTime.setGeometry(QtCore.QRect(10, datetime_y, datetime_width, datetime_height))
        self.labelDateTime.setStyleSheet("color: white; font-weight: bold; font-size: 12px;")
        self.labelDateTime.setObjectName("labelDateTime")
        
        # Battery status label 
        battery_width = int(self.main_window_width * 0.104)  # 100px -> %10.4
        battery_x = int(self.main_window_width * 0.885)  # %88.5 konumda
        self.labelBattery = QtWidgets.QLabel(self.statusBar)
        self.labelBattery.setGeometry(QtCore.QRect(battery_x, datetime_y, battery_width, datetime_height))
        self.labelBattery.setStyleSheet("color: white; font-weight: bold; font-size: 12px;")
        self.labelBattery.setAlignment(QtCore.Qt.AlignRight)
        self.labelBattery.setText("Şarj: ?")
        self.labelBattery.setObjectName("labelBattery")
        
        # Mission Selection Area
        gorev_grup_width = int(self.main_window_width * 0.708)  # 680px -> %70.8
        gorev_grup_height = int(self.main_window_height * 0.29)  # 170px -> %29
        gorev_y = int(self.main_window_height * 0.085)  # %8.5 y konumu
        self.gorevSecimiAlani = QtWidgets.QGroupBox(self.centralwidget)
        self.gorevSecimiAlani.setGeometry(QtCore.QRect(10, gorev_y, gorev_grup_width, gorev_grup_height))
        self.gorevSecimiAlani.setObjectName("gorevSecimiAlani")
        
        # Locating widgets
        margin = int(gorev_grup_width * 0.03) 
        dalış_width = int(gorev_grup_width * 0.20)  
        koordinat_width = int(gorev_grup_width * 0.17)    
        buton_width_big = int(gorev_grup_width * 0.14)  
        buton_width_small = int(gorev_grup_width * 0.11)  
        anomali_width = int(gorev_grup_width * 0.14)  
        nesne_width = int(gorev_grup_width * 0.20)  
        
        # Y Axis positions
        ust_satir_y = int(gorev_grup_height * 0.18)  
        alt_satir_y = int(gorev_grup_height * 0.53)  
        widget_height = int(gorev_grup_height * 0.24)  
        
        self.textEditBaslangicKonumu = QtWidgets.QTextEdit(self.gorevSecimiAlani)
        self.textEditBaslangicKonumu.setGeometry(QtCore.QRect(
            int(gorev_grup_width * 0.29), ust_satir_y, koordinat_width, widget_height)) 
        self.textEditBaslangicKonumu.setGeometry(QtCore.QRect(
            int(gorev_grup_width * 0.29), ust_satir_y, koordinat_width, widget_height)) 
        self.textEditBaslangicKonumu.setInputMethodHints(QtCore.Qt.ImhHiddenText|QtCore.Qt.ImhMultiLine)
        self.textEditBaslangicKonumu.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.textEditBaslangicKonumu.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.textEditBaslangicKonumu.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustIgnored)
        self.textEditBaslangicKonumu.setDocumentTitle("")
        self.textEditBaslangicKonumu.setOverwriteMode(False)
        self.textEditBaslangicKonumu.setObjectName("textEditBaslangicKonumu")
        
        self.labelAnomali_1 = QtWidgets.QLabel(self.gorevSecimiAlani)
        self.labelAnomali_1.setGeometry(QtCore.QRect(
            int(gorev_grup_width * 0.29), alt_satir_y, anomali_width, widget_height))  
        self.labelAnomali_1.setToolTip("")
        self.labelAnomali_1.setWhatsThis("")
        self.labelAnomali_1.setAccessibleDescription("")
        self.labelAnomali_1.setAutoFillBackground(False)
        self.labelAnomali_1.setFrameShape(QtWidgets.QFrame.Box)
        self.labelAnomali_1.setText("")
        self.labelAnomali_1.setTextFormat(QtCore.Qt.AutoText)
        self.labelAnomali_1.setObjectName("labelAnomali_1")
        self.labelAnomali_4 = QtWidgets.QLabel(self.gorevSecimiAlani)
        self.labelAnomali_4.setGeometry(QtCore.QRect(
            int(gorev_grup_width * 0.81), alt_satir_y, anomali_width, widget_height))  
        self.labelAnomali_4.setToolTip("")
        self.labelAnomali_4.setWhatsThis("")
        self.labelAnomali_4.setAccessibleDescription("")
        self.labelAnomali_4.setAutoFillBackground(False)
        self.labelAnomali_4.setFrameShape(QtWidgets.QFrame.Box)
        self.labelAnomali_4.setText("")
        self.labelAnomali_4.setTextFormat(QtCore.Qt.AutoText)
        self.labelAnomali_4.setObjectName("labelAnomali_4")
        self.labelNesneGorevi = QtWidgets.QLabel(self.gorevSecimiAlani)
        self.labelNesneGorevi.setGeometry(QtCore.QRect(
            int(gorev_grup_width * 0.07), alt_satir_y, nesne_width, widget_height)) 
        self.labelNesneGorevi.setFrameShape(QtWidgets.QFrame.WinPanel)
        self.labelNesneGorevi.setTextFormat(QtCore.Qt.AutoText)
        self.labelNesneGorevi.setAlignment(QtCore.Qt.AlignCenter)
        self.labelNesneGorevi.setWordWrap(True)
        self.labelNesneGorevi.setObjectName("labelNesneGorevi")
        self.labelAnomali_3 = QtWidgets.QLabel(self.gorevSecimiAlani)
        self.labelAnomali_3.setGeometry(QtCore.QRect(
            int(gorev_grup_width * 0.63), alt_satir_y, anomali_width, widget_height))  
        self.labelAnomali_3.setToolTip("")
        self.labelAnomali_3.setWhatsThis("")
        self.labelAnomali_3.setAccessibleDescription("")
        self.labelAnomali_3.setAutoFillBackground(False)
        self.labelAnomali_3.setFrameShape(QtWidgets.QFrame.Box)
        self.labelAnomali_3.setText("")
        self.labelAnomali_3.setTextFormat(QtCore.Qt.AutoText)
        self.labelAnomali_3.setObjectName("labelAnomali_3")
        self.labelDalisGorevi = QtWidgets.QLabel(self.gorevSecimiAlani)
        self.labelDalisGorevi.setGeometry(QtCore.QRect(
            int(gorev_grup_width * 0.07), ust_satir_y, dalış_width, widget_height)) 
        self.labelDalisGorevi.setFrameShape(QtWidgets.QFrame.WinPanel)
        self.labelDalisGorevi.setAlignment(QtCore.Qt.AlignCenter)
        self.labelDalisGorevi.setObjectName("labelDalisGorevi")
        self.textEditBitisKonumu = QtWidgets.QTextEdit(self.gorevSecimiAlani)
        self.textEditBitisKonumu.setGeometry(QtCore.QRect(
            int(gorev_grup_width * 0.48), ust_satir_y, koordinat_width, widget_height))  
        self.textEditBitisKonumu.setInputMethodHints(QtCore.Qt.ImhHiddenText|QtCore.Qt.ImhMultiLine)
        self.textEditBitisKonumu.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.textEditBitisKonumu.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.textEditBitisKonumu.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustIgnored)
        self.textEditBitisKonumu.setDocumentTitle("")
        self.textEditBitisKonumu.setOverwriteMode(False)
        self.textEditBitisKonumu.setObjectName("textEditBitisKonumu")
        self.labelAnomali_2 = QtWidgets.QLabel(self.gorevSecimiAlani)
        self.labelAnomali_2.setGeometry(QtCore.QRect(
            int(gorev_grup_width * 0.46), alt_satir_y, anomali_width, widget_height))  
        self.labelAnomali_2.setToolTip("")
        self.labelAnomali_2.setWhatsThis("")
        self.labelAnomali_2.setAccessibleDescription("")
        self.labelAnomali_2.setAutoFillBackground(False)
        self.labelAnomali_2.setFrameShape(QtWidgets.QFrame.Box)
        self.labelAnomali_2.setText("")
        self.labelAnomali_2.setTextFormat(QtCore.Qt.AutoText)
        self.labelAnomali_2.setObjectName("labelAnomali_2")
        
        radio_x = int(gorev_grup_width * 0.029)  
        radio_width = int(gorev_grup_width * 0.029)  
        radio_height = int(gorev_grup_height * 0.118)  
        radio_dalis_y = int(gorev_grup_height * 0.235)  
        radio_nesne_y = int(gorev_grup_height * 0.588)  
        
        self.btnDalis = QtWidgets.QRadioButton(self.gorevSecimiAlani)
        self.btnDalis.setGeometry(QtCore.QRect(radio_x, radio_dalis_y, radio_width, radio_height))
        self.btnDalis.setText("")
        self.btnDalis.setObjectName("btnDalis")
        self.btnNesne = QtWidgets.QRadioButton(self.gorevSecimiAlani)
        self.btnNesne.setGeometry(QtCore.QRect(radio_x, radio_nesne_y, radio_width, radio_height))
        self.btnNesne.setText("")
        self.btnNesne.setObjectName("btnNesne")
        self.kontrolAlani = QtWidgets.QGroupBox(self.centralwidget)
        kontrol_grup_width = int(self.main_window_width * 0.272)  
        kontrol_grup_height = int(self.main_window_height * 0.138)  
        kontrol_y = int(self.main_window_height * 0.392) 
        self.kontrolAlani.setGeometry(QtCore.QRect(10, kontrol_y, kontrol_grup_width, kontrol_grup_height))
        self.kontrolAlani.setObjectName("kontrolAlani")
        
        
        kontrol_margin = int(kontrol_grup_width * 0.08)  
        head_label_width = int(kontrol_grup_width * 0.42)  
        durum_label_width = int(kontrol_grup_width * 0.35)  
        
        self.labelAracErisimHead = QtWidgets.QLabel(self.kontrolAlani)
        self.labelAracErisimHead.setGeometry(QtCore.QRect(
            kontrol_margin, int(kontrol_grup_height * 0.25), head_label_width, 16))  
        self.labelAracErisimHead.setObjectName("labelAracErisimHead")
        self.labelAracDurum = QtWidgets.QLabel(self.kontrolAlani)
        self.labelAracDurum.setGeometry(QtCore.QRect(
            int(kontrol_grup_width * 0.55), int(kontrol_grup_height * 0.25), durum_label_width, 16))  
        self.labelAracDurum.setObjectName("labelAracDurum")
        self.labelAktifGorevHead = QtWidgets.QLabel(self.kontrolAlani)
        self.labelAktifGorevHead.setGeometry(QtCore.QRect(
            kontrol_margin, int(kontrol_grup_height * 0.60), head_label_width, 16))  
        self.labelAktifGorevHead.setObjectName("labelAktifGorevHead")
        self.labelAracDurum_2 = QtWidgets.QLabel(self.kontrolAlani)
        self.labelAracDurum_2.setGeometry(QtCore.QRect(
            int(kontrol_grup_width * 0.55), int(kontrol_grup_height * 0.60), durum_label_width, 16))  
        self.labelAracDurum_2.setObjectName("labelAracDurum_2")
        self.groupBoxGPS = QtWidgets.QGroupBox(self.centralwidget)
        gps_grup_width = int(self.main_window_width * 0.261)  
        gps_grup_height = int(self.main_window_height * 0.436)  
        gps_x = int(self.main_window_width * 0.729)  
        self.groupBoxGPS.setGeometry(QtCore.QRect(gps_x, gorev_y, gps_grup_width, gps_grup_height))
        self.groupBoxGPS.setObjectName("groupBoxGPS")
        
        
        map_width = int(gps_grup_width * 0.916) 
        map_height = int(gps_grup_height * 0.898) 
        map_margin = int(gps_grup_width * 0.04)  
        map_y = int(gps_grup_height * 0.059)  
        self.widgetForOpenStreetMap = QtWebEngineWidgets.QWebEngineView(self.groupBoxGPS)
        self.widgetForOpenStreetMap.setGeometry(QtCore.QRect(map_margin, map_y, map_width, map_height))
        self.widgetForOpenStreetMap.setObjectName("widgetForOpenStreetMap")
        self.groupBoxTerminal = QtWidgets.QGroupBox(self.centralwidget)
        terminal_grup_width = int(self.main_window_width * 0.521)  
        terminal_grup_height = int(self.main_window_height * 0.359) 
        terminal_y = int(self.main_window_height * 0.545) 
        self.groupBoxTerminal.setGeometry(QtCore.QRect(10, terminal_y, terminal_grup_width, terminal_grup_height))
        self.groupBoxTerminal.setObjectName("groupBoxTerminal")
        
        
        terminal_text_width = int(terminal_grup_width * 0.96)  
        terminal_text_height = int(terminal_grup_height * 0.858)  
        terminal_text_margin = int(terminal_grup_width * 0.02) 
        terminal_text_y = int(terminal_grup_height * 0.095)  
        self.terminalTextEdit = QtWidgets.QTextEdit(self.groupBoxTerminal)
        self.terminalTextEdit.setGeometry(QtCore.QRect(terminal_text_margin, terminal_text_y, terminal_text_width, terminal_text_height))
        self.terminalTextEdit.setReadOnly(True)
        self.terminalTextEdit.setObjectName("terminalTextEdit")
        self.groupBoxTest = QtWidgets.QGroupBox(self.centralwidget)
        test_grup_width = int(self.main_window_width * 0.261)  
        test_grup_height = int(self.main_window_height * 0.155) 
        test_y = int(self.main_window_height * 0.545)  
        self.groupBoxTest.setGeometry(QtCore.QRect(gps_x, test_y, test_grup_width, test_grup_height))
        self.groupBoxTest.setObjectName("groupBoxTest")
        
        
        test_button_width = int(test_grup_width * 0.35) 
        test_label_width = int(test_grup_width * 0.54) 
        test_button_height = int(test_grup_height * 0.35) 
        test_label_height = int(test_grup_height * 0.35) 
        test_margin = int(test_grup_width * 0.04)  
        test_label_x = int(test_grup_width * 0.43) 
        
        
        kalibrasyon_y = int(test_grup_height * 0.25)  
        self.pushButtonKalibre = QtWidgets.QPushButton(self.groupBoxTest)
        self.pushButtonKalibre.setGeometry(QtCore.QRect(test_margin, kalibrasyon_y, test_button_width, test_button_height))
        self.pushButtonKalibre.setObjectName("pushButtonKalibre")
        
        self.labelKalibreText = QtWidgets.QLabel(self.groupBoxTest)
        self.labelKalibreText.setGeometry(QtCore.QRect(test_label_x, kalibrasyon_y, test_label_width, test_label_height))
        self.labelKalibreText.setScaledContents(False)
        self.labelKalibreText.setWordWrap(True)
        self.labelKalibreText.setObjectName("labelKalibreText")
        
        
        sizdirmazlik_y = int(test_grup_height * 0.63)  
        self.pushButtonSizdirmazlik = QtWidgets.QPushButton(self.groupBoxTest)
        self.pushButtonSizdirmazlik.setGeometry(QtCore.QRect(test_margin, sizdirmazlik_y, test_button_width, test_button_height))
        self.pushButtonSizdirmazlik.setDefault(False)
        self.pushButtonSizdirmazlik.setObjectName("pushButtonSizdirmazlik")
        
        self.labelSizdirmazlikText = QtWidgets.QLabel(self.groupBoxTest)
        self.labelSizdirmazlikText.setGeometry(QtCore.QRect(test_label_x, sizdirmazlik_y, test_label_width, test_label_height))
        self.labelSizdirmazlikText.setScaledContents(False)
        self.labelSizdirmazlikText.setWordWrap(True)
        self.labelSizdirmazlikText.setObjectName("labelSizdirmazlikText")
        self.pushButtonRotaCiz = QtWidgets.QPushButton(self.gorevSecimiAlani)
        self.pushButtonRotaCiz.setGeometry(QtCore.QRect(
            int(gorev_grup_width * 0.67), ust_satir_y, buton_width_big, widget_height))
        self.pushButtonRotaCiz.setText("Rota Çiz")
        self.pushButtonRotaCiz.setObjectName("pushButtonRotaCiz")
        self.pushButtonGonder = QtWidgets.QPushButton(self.gorevSecimiAlani)
        self.pushButtonGonder.setGeometry(QtCore.QRect(
            int(gorev_grup_width * 0.83), ust_satir_y, buton_width_small, widget_height)) 
        self.pushButtonGonder.setText("Gönder")
        self.pushButtonGonder.setObjectName("pushButtonGonder")
        MainWindow.setCentralWidget(self.centralwidget)
       

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        self.ekle_islevsellik()

        
        map_path = resource_path("map.html")
        if os.path.exists(map_path):
            self.widgetForOpenStreetMap.load(QtCore.QUrl.fromLocalFile(map_path))
        else:
           
            self.widgetForOpenStreetMap.setHtml("<html><body><h3>Harita dosyası bulunamadı</h3></body></html>")

        
        self.apply_styles(MainWindow)
        
        
        MainWindow.ui = self

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "DOLPA Underwater Technologies"))
        self.gorevSecimiAlani.setTitle(_translate("MainWindow", "Görev Seçimi"))
        self.textEditBaslangicKonumu.setPlaceholderText(_translate("MainWindow", "Başlangıç Konumu"))
        self.labelNesneGorevi.setText(_translate("MainWindow", "Kablo Takibi ve Anomali Tespiti"))
        self.labelDalisGorevi.setText(_translate("MainWindow", "Kayıp Hazine Avı: \n"
"Atlantis’in Peşinde"))
        self.textEditBitisKonumu.setPlaceholderText(_translate("MainWindow", "Bitiş Konumu"))
        self.kontrolAlani.setTitle(_translate("MainWindow", "Kontrol Alanı"))
        self.labelAracErisimHead.setText(_translate("MainWindow", "ARACA ERİŞİM:"))
        self.labelAracDurum.setText(_translate("MainWindow", "Bağlı Değil"))
        self.labelAktifGorevHead.setText(_translate("MainWindow", "AKTİF GÖREV:"))
        self.labelAracDurum_2.setText(_translate("MainWindow", "-"))
        self.groupBoxGPS.setTitle(_translate("MainWindow", "GPS"))
        self.groupBoxTerminal.setTitle(_translate("MainWindow", "Terminal"))
        self.groupBoxTest.setTitle(_translate("MainWindow", "Test"))
        self.labelKalibreText.setText(_translate("MainWindow", "Kalibrasyon Butonu"))
        self.pushButtonKalibre.setText(_translate("MainWindow", "Kalibrasyon"))
        self.pushButtonSizdirmazlik.setText(_translate("MainWindow", "Sızdırmazlık"))
        self.labelSizdirmazlikText.setText(_translate("MainWindow", "Sızdırmazlık Testi"))
        

    def ekle_islevsellik(self):
        self.btnDalis.toggled.connect(self.update_active_gorev)
        self.btnNesne.toggled.connect(self.update_active_gorev)

        
        self.connection_timer = QtCore.QTimer()
        self.connection_timer.timeout.connect(self.check_arac_baglanti)
        self.connection_timer.start(CONFIG["baglanti_kontrol_araligi"])

       
        self.datetime_timer = QtCore.QTimer()
        self.datetime_timer.timeout.connect(self.update_datetime)
        self.datetime_timer.start(CONFIG["datetime_guncelleme_araligi"])
        
        
        self.update_datetime()

        
        self._arac_bagli_onceki = None
        self.check_arac_baglanti()

        self.pushButtonRotaCiz.clicked.connect(self.rota_ciz_butonuna_basildi)
        self.pushButtonGonder.clicked.connect(self.rota_ve_gorev_gonder)
        self.pushButtonKalibre.clicked.connect(self.kalibrasyon_butonuna_basildi)

    def update_active_gorev(self):
        if self.btnDalis.isChecked() and self.labelAracDurum_2.text() != "Dalış Görevi":
            self.labelAracDurum_2.setText("Dalış Görevi")
            self.terminale_yaz("Görev seçildi: Dalış Görevi")
            self.textEditBaslangicKonumu.setEnabled(True)
            self.textEditBitisKonumu.setEnabled(True)
            self.pushButtonRotaCiz.setEnabled(True)
            self.pushButtonGonder.setEnabled(True)
        elif self.btnNesne.isChecked() and self.labelAracDurum_2.text() != "Kablo Takibi":
            self.labelAracDurum_2.setText("Kablo Takibi")
            self.terminale_yaz("Görev seçildi: Kablo Takibi")
            self.textEditBaslangicKonumu.setEnabled(False)
            self.textEditBitisKonumu.setEnabled(False)
            self.pushButtonRotaCiz.setEnabled(False)
            self.pushButtonGonder.setEnabled(True)

    def check_arac_baglanti(self):
        arac_bagli = self.is_arac_connected()
        
        if arac_bagli != getattr(self, "_arac_bagli_onceki", None):
            if arac_bagli:
                self.labelAracDurum.setText("Bağlı")
                self.labelAracDurum.setStyleSheet(CONNECTED_STYLE)
                self.terminale_yaz("Araç bağlantısı sağlandı.")
                self.update_battery_status()
            else:
                self.labelAracDurum.setText("Bağlı Değil")
                self.labelAracDurum.setStyleSheet(DISCONNECTED_STYLE)
                self.terminale_yaz("Araç bağlantısı yok.")
                self.labelBattery.setStyleSheet(f"color: {BATTERY_WHITE}; font-weight: bold; font-size: 12px;")
                self.labelBattery.setText("🔋 ?")
            self._arac_bagli_onceki = arac_bagli
        else:
            if arac_bagli:
                self.labelAracDurum.setText("Bağlı")
                self.labelAracDurum.setStyleSheet(CONNECTED_STYLE)
                self.update_battery_status()
            else:
                self.labelAracDurum.setText("Bağlı Değil")
                self.labelAracDurum.setStyleSheet(DISCONNECTED_STYLE)
                self.labelBattery.setStyleSheet(f"color: {BATTERY_WHITE}; font-weight: bold; font-size: 12px;")
                self.labelBattery.setText("🔋 ?")

    def is_arac_connected(self):
        """Araç bağlantısını kontrol et - optimize edilmiş versiyon"""
        try:
            with socket.create_connection((ARAC_IP, ARAC_PORT), timeout=0.5) as s:
                return True
        except (socket.timeout, socket.error, ConnectionRefusedError, OSError):
            return False

    def terminale_yaz(self, mesaj):
        self.terminalTextEdit.append(mesaj)

    def draw_route_on_map(self, start_lat, start_lng, end_lat, end_lng):
        js = f"drawRoute({start_lat}, {start_lng}, {end_lat}, {end_lng});"
        self.widgetForOpenStreetMap.page().runJavaScript(js)

    def rota_ciz_butonuna_basildi(self):
        if not self.btnDalis.isChecked():
            self.terminale_yaz("Önce 'Dalış Görevi'ni seçmelisiniz!")
            return
        start = self.textEditBaslangicKonumu.toPlainText().split(",")
        end = self.textEditBitisKonumu.toPlainText().split(",")
        if len(start) == 2 and len(end) == 2:
            try:
                start_lat, start_lng = float(start[0]), float(start[1])
                end_lat, end_lng = float(end[0]), float(end[1])
                self.draw_route_on_map(start_lat, start_lng, end_lat, end_lng)
                mesafe = self.haversine(start_lat, start_lng, end_lat, end_lng)
                self.terminale_yaz(f"Rota çizildi: {start_lat},{start_lng} -> {end_lat},{end_lng} (Mesafe: {mesafe:.2f} m)")
            except ValueError:
                self.terminale_yaz("Hatalı koordinat girişi!")

    def rota_ve_gorev_gonder(self):
        
        if not self.is_arac_connected():
            self.terminale_yaz("HATA: Araç bağlı değil, bilgi gönderilemedi!")
            return
        if self.btnDalis.isChecked():
            start = self.textEditBaslangicKonumu.toPlainText().split(",")
            end = self.textEditBitisKonumu.toPlainText().split(",")
            try:
                start_lat, start_lng = float(start[0]), float(start[1])
                end_lat, end_lng = float(end[0]), float(end[1])
                veri = {
                    "gorev": "dalis",
                    "baslangic": [start_lat, start_lng],
                    "bitis": [end_lat, end_lng]
                }
            except Exception:
                self.terminale_yaz("Koordinatlar eksik veya hatalı!")
                return
        elif self.btnNesne.isChecked():
            veri = {
                "gorev": "kablo",
                "komut": "basla"
            }
        else:
            self.terminale_yaz("Önce görev seçmelisiniz!")
            return

        try:
            mesaj = json.dumps(veri).encode("utf-8")
            with socket.create_connection((ARAC_IP, ARAC_PORT), timeout=2) as s:
                s.sendall(mesaj)
            self.terminale_yaz("Görev araca gönderildi.")
        except Exception as e:
            self.terminale_yaz(f"Veri gönderilemedi: {e}")

    def haversine(self, lat1, lon1, lat2, lon2):
        R = 6371000
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c 

    def kalibrasyon_butonuna_basildi(self):
        if not self.is_arac_connected():
            self.terminale_yaz("HATA: Araç bağlı değil, kalibrasyon başlatılamadı!")
            return
        try:
            veri = {"komut": "kalibrasyon"}
            mesaj = json.dumps(veri).encode("utf-8")
            with socket.create_connection((ARAC_IP, ARAC_PORT), timeout=2) as s:
                s.sendall(mesaj)
            self.terminale_yaz("Kalibrasyon komutu araca gönderildi.")
        except Exception as e:
            self.terminale_yaz(f"Kalibrasyon komutu gönderilemedi: {e}")

    def update_datetime(self):
        """Tarih ve saat güncelle - optimize edilmiş"""
        try:
            import datetime
            now = datetime.datetime.now()
            datetime_str = now.strftime("%d.%m.%Y %H:%M:%S")
            self.labelDateTime.setText(datetime_str)
        except Exception:
            pass

    def update_battery_status(self):
        try:
            veri = {"komut": "sarj_durumu"}
            mesaj = json.dumps(veri).encode("utf-8")
            
            with socket.create_connection((ARAC_IP, ARAC_PORT), timeout=1) as s:
                s.sendall(mesaj)
                response = s.recv(1024).decode("utf-8")
                data = json.loads(response)
                
                if "sarj" in data:
                    sarj_yuzdesi = data["sarj"]
                    if sarj_yuzdesi > 50:
                        color = BATTERY_GREEN
                    elif sarj_yuzdesi > 20:
                        color = BATTERY_ORANGE
                    else:
                        color = BATTERY_RED
                    
                    self.labelBattery.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 12px;")
                    self.labelBattery.setText(f"🔋 {sarj_yuzdesi}%")
                else:
                    self.labelBattery.setStyleSheet(f"color: {BATTERY_WHITE}; font-weight: bold; font-size: 12px;")
                    self.labelBattery.setText("🔋 ?")
        except Exception:
            self.labelBattery.setStyleSheet(f"color: {BATTERY_WHITE}; font-weight: bold; font-size: 12px;")
            self.labelBattery.setText("🔋 ?")

    def apply_styles(self, MainWindow):
        MainWindow.setStyleSheet(MAIN_WINDOW_STYLE)
        
        self.statusBar.setStyleSheet(STATUS_BAR_STYLE)
        
        self.labelDateTime.setStyleSheet(DATETIME_LABEL_STYLE)
        
        self.labelBattery.setStyleSheet(BATTERY_LABEL_STYLE)
        
        self.labelDalisGorevi.setStyleSheet(GOREV_LABEL_STYLE)
        self.labelNesneGorevi.setStyleSheet(GOREV_LABEL_STYLE)
        
        self.textEditBaslangicKonumu.setStyleSheet(KOORDINAT_TEXT_STYLE)
        self.textEditBitisKonumu.setStyleSheet(KOORDINAT_TEXT_STYLE)
        
        self.labelAnomali_1.setStyleSheet(ANOMALI_LABEL_STYLE)
        self.labelAnomali_2.setStyleSheet(ANOMALI_LABEL_STYLE)
        self.labelAnomali_3.setStyleSheet(ANOMALI_LABEL_STYLE)
        self.labelAnomali_4.setStyleSheet(ANOMALI_LABEL_STYLE)
        
        self.pushButtonRotaCiz.setStyleSheet(BUTTON_STYLE)
        self.pushButtonGonder.setStyleSheet(BUTTON_STYLE)
        self.pushButtonKalibre.setStyleSheet(BUTTON_STYLE)
        self.pushButtonSizdirmazlik.setStyleSheet(BUTTON_STYLE)
        
        self.btnDalis.setStyleSheet(RADIO_BUTTON_STYLE)
        self.btnNesne.setStyleSheet(RADIO_BUTTON_STYLE)
        
        self.labelAracErisimHead.setStyleSheet(BASLIK_LABEL_STYLE)
        self.labelAktifGorevHead.setStyleSheet(BASLIK_LABEL_STYLE)
        self.labelKalibreText.setStyleSheet(BASLIK_LABEL_STYLE)
        self.labelSizdirmazlikText.setStyleSheet(BASLIK_LABEL_STYLE)
        
        self.gorevSecimiAlani.setStyleSheet(GROUP_BOX_STYLE)
        self.kontrolAlani.setStyleSheet(GROUP_BOX_STYLE)
        self.groupBoxGPS.setStyleSheet(GROUP_BOX_STYLE)
        self.groupBoxTerminal.setStyleSheet(GROUP_BOX_STYLE)
        self.groupBoxTest.setStyleSheet(GROUP_BOX_STYLE)
        
        self.terminalTextEdit.setStyleSheet(TERMINAL_TEXT_STYLE)
        
        self.labelAracDurum.setStyleSheet(DURUM_LABEL_STYLE)
        self.labelAracDurum_2.setStyleSheet(GOREV_DURUM_LABEL_STYLE)

    def update_widget_geometries(self, new_width, new_height):
        status_bar_height = int(new_height * 0.068)
        self.statusBar.setGeometry(QtCore.QRect(0, 0, new_width, status_bar_height))
        
        datetime_width = int(new_width * 0.208)
        datetime_height = int(status_bar_height * 0.5)
        datetime_y = int(status_bar_height * 0.25)
        self.labelDateTime.setGeometry(QtCore.QRect(10, datetime_y, datetime_width, datetime_height))
        
        battery_width = int(new_width * 0.104)
        battery_x = int(new_width * 0.885)
        self.labelBattery.setGeometry(QtCore.QRect(battery_x, datetime_y, battery_width, datetime_height))
        
        gorev_grup_width = int(new_width * 0.708)
        gorev_grup_height = int(new_height * 0.29)
        gorev_y = int(new_height * 0.085)
        self.gorevSecimiAlani.setGeometry(QtCore.QRect(10, gorev_y, gorev_grup_width, gorev_grup_height))
        
        self.update_gorev_widget_geometries(gorev_grup_width, gorev_grup_height)
        
        kontrol_grup_width = int(new_width * 0.272)
        kontrol_grup_height = int(new_height * 0.138)
        kontrol_y = int(new_height * 0.392)
        self.kontrolAlani.setGeometry(QtCore.QRect(10, kontrol_y, kontrol_grup_width, kontrol_grup_height))
        
        self.update_kontrol_widget_geometries(kontrol_grup_width, kontrol_grup_height)
        
        gps_grup_width = int(new_width * 0.261)
        gps_grup_height = int(new_height * 0.436)
        gps_x = int(new_width * 0.729)
        self.groupBoxGPS.setGeometry(QtCore.QRect(gps_x, gorev_y, gps_grup_width, gps_grup_height))
        
        map_width = int(gps_grup_width * 0.916)
        map_height = int(gps_grup_height * 0.898)
        map_margin = int(gps_grup_width * 0.04)
        map_y = int(gps_grup_height * 0.059)
        self.widgetForOpenStreetMap.setGeometry(QtCore.QRect(map_margin, map_y, map_width, map_height))
        
        terminal_grup_width = int(new_width * 0.521)
        terminal_grup_height = int(new_height * 0.359)
        terminal_y = int(new_height * 0.545)
        self.groupBoxTerminal.setGeometry(QtCore.QRect(10, terminal_y, terminal_grup_width, terminal_grup_height))
        
        terminal_text_width = int(terminal_grup_width * 0.96)
        terminal_text_height = int(terminal_grup_height * 0.858)
        terminal_text_margin = int(terminal_grup_width * 0.02)
        terminal_text_y = int(terminal_grup_height * 0.095)
        self.terminalTextEdit.setGeometry(QtCore.QRect(terminal_text_margin, terminal_text_y, terminal_text_width, terminal_text_height))
        
        test_grup_width = int(new_width * 0.261)
        test_grup_height = int(new_height * 0.155)
        test_y = int(new_height * 0.545)
        self.groupBoxTest.setGeometry(QtCore.QRect(gps_x, test_y, test_grup_width, test_grup_height))
        
        self.update_test_widget_geometries(test_grup_width, test_grup_height)
    
    def update_gorev_widget_geometries(self, gorev_grup_width, gorev_grup_height):
        koordinat_width = int(gorev_grup_width * 0.17)
        buton_width_big = int(gorev_grup_width * 0.14)
        buton_width_small = int(gorev_grup_width * 0.11)
        anomali_width = int(gorev_grup_width * 0.14)
        nesne_width = int(gorev_grup_width * 0.20)
        dalış_width = int(gorev_grup_width * 0.20)
        
        ust_satir_y = int(gorev_grup_height * 0.18)  
        alt_satir_y = int(gorev_grup_height * 0.53)  
        widget_height = int(gorev_grup_height * 0.24)  
        
        self.textEditBaslangicKonumu.setGeometry(QtCore.QRect(int(gorev_grup_width * 0.29), ust_satir_y, koordinat_width, widget_height))
        self.textEditBitisKonumu.setGeometry(QtCore.QRect(int(gorev_grup_width * 0.48), ust_satir_y, koordinat_width, widget_height))
        
        self.labelAnomali_1.setGeometry(QtCore.QRect(int(gorev_grup_width * 0.29), alt_satir_y, anomali_width, widget_height))
        self.labelAnomali_2.setGeometry(QtCore.QRect(int(gorev_grup_width * 0.46), alt_satir_y, anomali_width, widget_height))
        self.labelAnomali_3.setGeometry(QtCore.QRect(int(gorev_grup_width * 0.63), alt_satir_y, anomali_width, widget_height))
        self.labelAnomali_4.setGeometry(QtCore.QRect(int(gorev_grup_width * 0.81), alt_satir_y, anomali_width, widget_height))
        
        self.labelNesneGorevi.setGeometry(QtCore.QRect(int(gorev_grup_width * 0.07), alt_satir_y, nesne_width, widget_height))
        self.labelDalisGorevi.setGeometry(QtCore.QRect(int(gorev_grup_width * 0.07), ust_satir_y, dalış_width, widget_height))
        
        self.pushButtonRotaCiz.setGeometry(QtCore.QRect(int(gorev_grup_width * 0.67), ust_satir_y, buton_width_big, widget_height))
        self.pushButtonGonder.setGeometry(QtCore.QRect(int(gorev_grup_width * 0.83), ust_satir_y, buton_width_small, widget_height))
        
        radio_x = int(gorev_grup_width * 0.029)
        radio_width = int(gorev_grup_width * 0.029)
        radio_height = int(gorev_grup_height * 0.118)
        radio_dalis_y = int(gorev_grup_height * 0.235)
        radio_nesne_y = int(gorev_grup_height * 0.588)
        self.btnDalis.setGeometry(QtCore.QRect(radio_x, radio_dalis_y, radio_width, radio_height))
        self.btnNesne.setGeometry(QtCore.QRect(radio_x, radio_nesne_y, radio_width, radio_height))
    
    def update_kontrol_widget_geometries(self, kontrol_grup_width, kontrol_grup_height):
        kontrol_margin = int(kontrol_grup_width * 0.08)
        head_label_width = int(kontrol_grup_width * 0.42)
        durum_label_width = int(kontrol_grup_width * 0.35)
        
        self.labelAracErisimHead.setGeometry(QtCore.QRect(kontrol_margin, int(kontrol_grup_height * 0.25), head_label_width, 16))
        self.labelAracDurum.setGeometry(QtCore.QRect(int(kontrol_grup_width * 0.55), int(kontrol_grup_height * 0.25), durum_label_width, 16))
        self.labelAktifGorevHead.setGeometry(QtCore.QRect(kontrol_margin, int(kontrol_grup_height * 0.60), head_label_width, 16))
        self.labelAracDurum_2.setGeometry(QtCore.QRect(int(kontrol_grup_width * 0.55), int(kontrol_grup_height * 0.60), durum_label_width, 16))
    
    def update_test_widget_geometries(self, test_grup_width, test_grup_height):
        test_button_width = int(test_grup_width * 0.35)
        test_label_width = int(test_grup_width * 0.54)
        test_button_height = int(test_grup_height * 0.35)
        test_label_height = int(test_grup_height * 0.35)
        test_margin = int(test_grup_width * 0.04)
        test_label_x = int(test_grup_width * 0.43)
        
        kalibrasyon_y = int(test_grup_height * 0.25)
        sizdirmazlik_y = int(test_grup_height * 0.63)
        
        self.pushButtonKalibre.setGeometry(QtCore.QRect(test_margin, kalibrasyon_y, test_button_width, test_button_height))
        self.labelKalibreText.setGeometry(QtCore.QRect(test_label_x, kalibrasyon_y, test_label_width, test_label_height))
        self.pushButtonSizdirmazlik.setGeometry(QtCore.QRect(test_margin, sizdirmazlik_y, test_button_width, test_button_height))
        self.labelSizdirmazlikText.setGeometry(QtCore.QRect(test_label_x, sizdirmazlik_y, test_label_width, test_label_height))

if __name__ == "__main__":
    import sys
    
    app = QtWidgets.QApplication(sys.argv)
    app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
    
    MainWindow = ResponsiveMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    
    MainWindow.show()
    
    sys.exit(app.exec_())