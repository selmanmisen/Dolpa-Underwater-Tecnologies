# -*- coding: utf-8 -*-
"""
DOLPA Underwater Technologies
Stylesheet Definitions
"""

# Ana pencere arkaplan rengi
MAIN_WINDOW_STYLE = "background-color: #2c74b3;"

# Durum çubuğu stil
STATUS_BAR_STYLE = """
QWidget {
    background-color: #0d447d;
    border: none;
}
"""

# Görev başlık labelları için stil
GOREV_LABEL_STYLE = """
QLabel {
    background-color: #0a2647;
    color: white;
    border-radius: 8px;
    font-weight: bold;
    font-size: 13px;
    padding: 5px;
}
"""

# Koordinat text editleri için stil
KOORDINAT_TEXT_STYLE = """
QTextEdit {
    background-color: #023972;
    color: white;
    border: 1px solid #4a90e2;
    border-radius: 8px;
    padding: 5px;
    font-size: 12px;
}
"""

# Anomali labelları için stil
ANOMALI_LABEL_STYLE = """
QLabel {
    background-color: #023972;
    color: white;
    border: 1px solid #4a90e2;
    border-radius: 8px;
    font-size: 11px;
}
"""

# Butonlar için stil
BUTTON_STYLE = """
QPushButton {
    background-color: #023972;
    color: white;
    border: 1px solid #4a90e2;
    border-radius: 8px;
    font-weight: bold;
    font-size: 12px;
    padding: 5px;
}
QPushButton:hover {
    background-color: #034a94;
}
QPushButton:pressed {
    background-color: #012855;
}
"""

# Radio buttonlar için stil
RADIO_BUTTON_STYLE = """
QRadioButton {
    background-color: #0a2647;
}
QRadioButton::indicator {
    width: 15px;
    height: 15px;
    border-radius: 7px;
    border: 1px solid #FFFFFF;    
    background-color: #FFFFFF;
}
QRadioButton::indicator:checked {
    background-color: #0a2647;
}
"""

# Başlık etiketleri için stil
BASLIK_LABEL_STYLE = """
QLabel {
    background-color: #0a2647;
    color: white;
    font-weight: bold;
    font-size: 14px;
    border: none;
}
"""

# Grup kutuları için stil
GROUP_BOX_STYLE = """
QGroupBox {
    border: 1px solid #4a90e2;
    border-radius: 8px;
    background-color: #0a2647;
}
QGroupBox:title {
    color: white;
    font-weight: bold;
    font-size: 12px;
}
"""

# Terminal metin alanı için stil
TERMINAL_TEXT_STYLE = """
QTextEdit {
    background-color: #0a2647;
    color: white;
    border: none;
    font-size: 12px;
}
"""

# Durum etiketleri için stil (bağlantı durumu)
DURUM_LABEL_STYLE = """
QLabel {
    background-color: #0a2647;
    color: #ff0000;
    font-weight: bold;
    font-size: 12px;
    border: none;
}
"""

# Görev durumu etiketleri için stil (her zaman beyaz)
GOREV_DURUM_LABEL_STYLE = """
QLabel {
    background-color: #0a2647;
    color: white;
    font-weight: bold;
    font-size: 12px;
    border: none;
}
"""

# Şarj durumu etiketi için stil
BATTERY_LABEL_STYLE = """
QLabel {
    color: white;
    font-weight: bold;
    font-size: 12px;
}
"""

# Tarih/saat etiketi için stil
DATETIME_LABEL_STYLE = "color: white; font-weight: bold; font-size: 12px;"

# Bağlı durum stil (yeşil)
CONNECTED_STYLE = "background-color: #0a2647; color: #00ff00; font-weight: bold; border: none;"

# Bağlı değil durum stil (kırmızı)
DISCONNECTED_STYLE = "background-color: #0a2647; color: #ff0000; font-weight: bold; border: none;"

# Şarj renkleri
BATTERY_GREEN = "#00ff00"  # Yeşil (>50%)
BATTERY_ORANGE = "#ffa500"  # Turuncu (20-50%)
BATTERY_RED = "#ff0000"  # Kırmızı (<20%)
BATTERY_WHITE = "white"  # Bilinmeyen durum
