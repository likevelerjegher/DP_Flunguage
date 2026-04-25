from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QToolBar
)
from PyQt6.QtGui import QAction
import qtawesome as qta
import json

from repositories.training_repository import TrainingRepository
from services.data_storage_service import DataStorageService
from ui.nav_button import NavButton
from services.training_service import TrainingService
from ui.widgets.dictionary.dictionary_widget import DictionaryWidget
from ui.settings_dialog import SettingsDialog
from ui.widgets.dictionary.dictionary_detail_widget import DictionaryDetailWidget
from ui.widgets.statictics.stat_widget import StatWidget
from ui.widgets.training.training_widget import TrainingWidget


class MainWindow(QMainWindow):
    def __init__(self, dictionary_service, word_service):
        super().__init__()
        self.icon_color_value = "#BBBBBB"
        self.word_service = word_service
        self.service = dictionary_service
        self.storage = DataStorageService("app.db")
        self.training_repo = TrainingRepository(self.storage)

        self.training_service = TrainingService(
            self.word_service,
            self.service,
            self.training_repo
        )
        self.current_theme = "dark"
        self.font_size = 14

        self.setWindowTitle("Flunguage")
        self.setMinimumSize(900, 600)

        # центральный контейнер
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)

        # STACK (экраны)
        self.stack = QStackedWidget()

        self.dict_screen = DictionaryWidget(self.service, self)
        self.training_view = TrainingWidget(self.training_service, self)
        self.statistics_view = StatWidget(self.training_repo)

        self.stack.addWidget(self.dict_screen)
        self.stack.addWidget(self.training_view)
        self.stack.addWidget(self.statistics_view)

        self.current_dictionary_screen = None
        self.current_dictionary_id = None

        # НИЖНЯЯ ПАНЕЛЬ
        navbar_layout = QHBoxLayout()
        navbar_layout.setContentsMargins(0, 0, 0, 0)

        self.btn_dictionary = NavButton('fa5s.book', "Словарь")
        self.btn_training = NavButton('fa5s.dumbbell', "Тренировка")
        self.btn_stats = NavButton('fa5s.chart-bar', "Статистика")

        navbar_layout.addWidget(self.btn_dictionary)
        navbar_layout.addWidget(self.btn_training)
        navbar_layout.addWidget(self.btn_stats)

        navbar = QWidget()
        navbar.setLayout(navbar_layout)
        navbar.setObjectName("navbar")

        # добавляем в layout
        self.layout.addWidget(self.stack)
        self.layout.addWidget(navbar)

        main_widget.setLayout(self.layout)

        # обработка кликов
        self.btn_dictionary.mousePressEvent = lambda e: self.switch_screen(0)

        # self.btn_dictionary.mousePressEvent = lambda e: self.go_to_dictionaries()

        self.btn_training.mousePressEvent = lambda e: self.switch_screen(1)
        self.btn_stats.mousePressEvent = lambda e: self.switch_screen(2)

        # TOOLBAR (настройки)
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        self.settings_action = QAction("Настройки", self)
        self.settings_action.triggered.connect(self.open_settings)
        toolbar.addAction(self.settings_action)

        #  применяем стиль
        self.apply_theme("dark")
        self.load_settings()

        # активная кнопка по умолчанию
        self.switch_screen(0)

    # переключение экранов
    def switch_screen(self, index: int):
        self.stack.setCurrentIndex(index)
        if index == 0:
            self.dict_screen.refresh()
        if index == 2:
            self.statistics_view.load_stats()
        if self.current_theme == "dark":
            active = "#4CAF50"
            inactive = "#BBBBBB"
        else:
            active = "#2E7D32"
            inactive = "#666666"

        buttons = [self.btn_dictionary, self.btn_training, self.btn_stats]

        for i, btn in enumerate(buttons):
            btn.set_active(i == index, active, inactive)

    # открыть настройки
    def open_settings(self):
        dialog = SettingsDialog(self)

        # прокидываем текущие значения
        dialog.set_values(self.current_theme, self.font_size)

        if dialog.exec():
            theme = dialog.theme_box.currentText()
            font_size = dialog.font_size.value()

            self.apply_theme(theme)
            self.apply_font(font_size)
            self.save_settings(theme, font_size)

    # тема
    def apply_theme(self, theme):
        self.current_theme = theme
        self.update_styles()

    # шрифт
    def apply_font(self, size):
        self.font_size = size
        self.update_styles()

    #сохранение настроек
    def save_settings(self, theme, font_size):
        with open("config.json", "w") as f:
            json.dump({
                "theme": theme,
                "font_size": font_size
            }, f)

    #загрузка настроек
    def load_settings(self):
        try:
            with open("config.json") as f:
                data = json.load(f)

                self.current_theme = data.get("theme", "dark")
                self.font_size = data.get("font_size", 12)
        except:
            pass

        self.update_styles()

    def update_navbar_icons(self, active_color, inactive_color):
        buttons = [self.btn_training, self.btn_dictionary, self.btn_stats]
        current = self.stack.currentIndex()

        for i, btn in enumerate(buttons):
            btn.set_active(i == current, active_color, inactive_color)

    def update_toolbar_icons(self):
        if self.current_theme == "dark":
            color = "#BBBBBB"
        else:
            color = "#444444"

        icon = qta.icon('fa5s.cog', color=color)
        self.settings_action.setIcon(icon)

    def open_dictionary(self, dictionary_id):
        screen = DictionaryDetailWidget(
            self.service,
            self.word_service,
            dictionary_id,
            self
        )

        self.stack.addWidget(screen)
        self.stack.setCurrentWidget(screen)

        self.current_dictionary_screen = screen
        self.current_dictionary_id = dictionary_id

        # применяем тему сразу
        screen.update_icons(self.current_theme)

    def go_to_dictionaries(self):
        self.dict_screen.refresh()
        self.stack.setCurrentWidget(self.dict_screen)

        # сброс текущего словаря
        self.current_dictionary_screen = None
        self.current_dictionary_id = None

#    def go_to_all_words(self):
#        self.stack.setCurrentWidget(self.all_words_screen)

    def refresh_all(self):
        # обновляем главный экран
        self.dict_screen.refresh()

        # обновляем открытый словарь (если есть)
        if self.current_dictionary_screen is not None:
            self.current_dictionary_screen.refresh()

    def icon_color(self):
        return self.icon_color_value

    def update_styles(self):
        if self.current_theme == "dark":
            bg = "#121212"
            surface = "#1E1E1E"
            text = "#FFFFFF"
            border = "#333333"
            accent = "#4CAF50"
            active = "#4CAF50"
            inactive = "#BBBBBB"
            icon = "#BBBBBB"
        else:
            bg = "#F5F5F5"
            surface = "#FFFFFF"
            text = "#222222"
            border = "#DDDDDD"
            accent = "#4CAF50"
            active = "#2E7D32"
            inactive = "#666666"
            icon = "#444444"

        self.setStyleSheet(f"""
        QMainWindow {{
            background-color: {bg};
        }}

        QWidget {{
            background-color: {bg};
            color: {text};
            font-size: {self.font_size}px;
        }}

        QLabel {{
            color: {text};
            background: transparent;

        }}
        QFrame {{
            background-color: {surface};
            border-radius: 10px;
        }}
        QPushButton {{
            background-color: transparent;
            color: {text};
            border: none;
            padding: 6px;
        }}

        QPushButton:hover {{
            background-color: {border};
            border-radius: 6px;
        }}

        QLineEdit {{
            background-color: {surface};
            border: 1px solid {border};
            border-radius: 6px;
            padding: 6px;
        }}

        QComboBox {{
            background-color: {surface};
            border: 1px solid {border};
            border-radius: 6px;
            padding: 5px;
        }}

        QSpinBox {{
            background-color: {surface};
            border: 1px solid {border};
            border-radius: 6px;
            padding: 5px;
        }}

        QWidget#navbar {{
            background-color: {surface};
            border-top: 1px solid {border};
        }}
        QToolBar {{
            background: transparent;
            border: none;
        }}

        QToolButton {{
            background: transparent;
        }}
        
        QTableWidget {{
            background-color: {surface};
            color: {text};
            border: 1px solid {border};
            border-radius: 8px;
            gridline-color: {border};
            selection-background-color: {accent};
            selection-color: #ffffff;
            padding: 4px;
        }}
        
        QTableWidget::item {{
            padding: 6px;
            border-bottom: 1px solid {border};
        }}
        
        QTableWidget::item:selected {{
            background-color: {accent};
            color: white;
        }}
        
        QHeaderView::section {{
            background-color: {surface};
            color: {text};
            padding: 6px;
            border: none;
            border-bottom: 1px solid {border};
            font-weight: bold;
        }}
        
        QTableWidget::item:hover {{
            background-color: {border};
        }}
        QTabWidget::pane {{
            border: none;
            background: transparent;
        }}
        QTabBar::tab {{
            background: transparent;
            color: {inactive};
        
            padding: 10px 14px;
        
            border: 1px solid transparent;
            border-top-left-radius: 10px;
            border-top-right-radius: 10px;
        }}
        
        QTabBar::tab:selected {{
            color: {accent};
            border-bottom: 2px solid {accent};
            border-top-left-radius: 10px;
            border-top-right-radius: 10px;
            font-weight: bold;
        }}
        QTabBar::tab:hover {{
            color: {accent};
        }}
        QTabWidget::pane {{
            border: none;
            background: {bg};
        }}
        QScrollArea {{
            border: none;
            background: transparent;
        }}
        
        QScrollArea > QWidget > QWidget {{
            border-radius: 10px;
        }}
        
        QScrollArea::viewport {{
            background: transparent;
            border-radius: 10px;
        }}
        QRadioButton {{
            background: transparent;
            color: {text};
            spacing: 6px;
        }}
        
        /* сам кружок */
        QRadioButton::indicator {{
            width: 16px;
            height: 16px;
            border-radius: 8px;
            border: 2px solid {border};
            background: transparent;
        }}

        QRadioButton::indicator:unchecked {{
            background-color: transparent;
            border: 1px solid {accent};

        }}
        
        /* когда выбран */
        QRadioButton::indicator:checked {{
            background-color: rgba(40, 120, 45, 0.6);
            border: 1px solid {accent};
        }}
        """)

        self.icon_color_value = icon
        self.update_navbar_icons(active, inactive)
        self.update_toolbar_icons()
        if hasattr(self.training_view, "update_info_icon"):
            self.training_view.update_info_icon(inactive)

        if hasattr(self.dict_screen, "update_bin_icon"):
            self.dict_screen.update_bin_icon(inactive)
        if self.current_dictionary_screen:
            self.current_dictionary_screen.update_icons(self.current_theme)
        if hasattr(self.statistics_view, "load_chart"):
            self.statistics_view.load_chart()
        self.statistics_view.update_theme(self.current_theme)
        if self.dict_screen:
            self.dict_screen.update_theme()

    def primary_button_style(self):
        if self.current_theme == "dark":
            return """
                QPushButton {
                    background-color: #2563eb;
                    color: white;
                    border-radius: 10px;
                    padding: 10px;
                    font-weight: 500;
                }

                QPushButton:hover {
                    background-color: #1d4ed8;
                }

                QPushButton:pressed {
                    background-color: #1e40af;
                }
            """
        else:
            return """
                QPushButton {
                    background-color: #2563eb;
                    color: white;
                    border-radius: 10px;
                    padding: 10px;
                    font-weight: 500;
                }

                QPushButton:hover {
                    background-color: #1d4ed8;
                }

                QPushButton:pressed {
                    background-color: #1e40af;
                }
            """