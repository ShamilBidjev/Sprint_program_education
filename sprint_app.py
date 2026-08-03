import sys
import os
import random
import shutil
import time
from datetime import datetime

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QLineEdit, QListWidget, QTableWidget, 
    QTableWidgetItem, QStackedWidget, QSpinBox, QHeaderView, 
    QMessageBox, QFrame, QScrollArea, QAbstractItemView, QComboBox,
    QFileDialog, QDialog, QInputDialog, QCheckBox
)
from PyQt5.QtCore import Qt, QTimer, QSize, QPoint
from PyQt5.QtGui import QIcon, QFont, QColor, QPixmap, QMovie, QCursor

# Import modular components!
from db_manager import DatabaseManager
from assets_manager import create_svg_assets, render_latex_to_pixmap, get_asset_path, image_to_latex_ocr, get_user_file_path

# Feature Toggle: Set to False to build the standard version without backups for other users!
BACKUPS_ENABLED = True


# ==========================================
# RESPONSIVE ZOOMABLE STYLE TEMPLATE
# ==========================================
VK_FACEBOOK_QSS_TEMPLATE = """
QMainWindow {{
    background-color: #F0F2F5;
}}

QWidget {{
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Arial, sans-serif;
    color: #1C1E21;
}}

QLabel {{
    color: #1C1E21;
}}

/* Titles */
QLabel#title_label {{
    font-size: {size_34}px;
    font-weight: 800;
    color: #2688EB;
    margin-bottom: 2px;
}}

QLabel#subtitle_label {{
    font-size: {size_14}px;
    color: #65676B;
    margin-bottom: 25px;
}}

QLabel#section_title {{
    font-size: {size_22}px;
    font-weight: 700;
    color: #1C1E21;
}}

QLabel#question_counter {{
    font-size: {size_13}px;
    font-weight: 600;
    color: #65676B;
}}

QLabel#timer_label {{
    font-size: {size_14}px;
    font-weight: 700;
    color: #C2410C;
    background-color: #FFF7ED;
    border: 1px solid #FFEDD5;
    border-radius: {radius_8}px;
    padding: {pad_6}px {pad_14}px;
}}

QLabel#question_text {{
    font-size: {size_26}px;
    font-weight: 700;
    color: #1C1E21;
}}

QLabel#card_title {{
    font-size: {size_16}px;
    font-weight: 700;
    color: #050505;
}}

QDialog {{
    background-color: #FFFFFF;
    border: 1px solid #CCD0D5;
    border-radius: {radius_8}px;
}}

QFrame#card_frame {{
    background-color: #FFFFFF;
    border: 1px solid #E4E6EB;
    border-radius: {radius_8}px;
}}

/* Buttons style library */
QPushButton {{
    background-color: #FFFFFF;
    border: 1px solid #CCD0D5;
    border-radius: {radius_6}px;
    padding: {pad_8}px {pad_16}px;
    font-size: {size_14}px;
    font-weight: 600;
    color: #2688EB;
}}

QPushButton:hover {{
    background-color: #F2F6FA;
    border-color: #A4C6FA;
}}

QPushButton:pressed {{
    background-color: #E1ECF4;
}}

QPushButton#primary_button {{
    background-color: #2688EB;
    border: none;
    color: #FFFFFF;
}}

QPushButton#primary_button:hover {{
    background-color: #2177D2;
}}

QPushButton#primary_button:pressed {{
    background-color: #1B66B8;
}}

QPushButton#lobby_action_button_primary {{
    background-color: #2688EB;
    border: none;
    border-radius: {radius_6}px;
    padding: {pad_12}px {pad_24}px;
    font-size: {size_15}px;
    font-weight: 700;
    color: #FFFFFF;
}}

QPushButton#lobby_action_button_primary:hover {{
    background-color: #2177D2;
}}

QPushButton#lobby_action_button_primary:pressed {{
    background-color: #1B66B8;
}}

QPushButton#lobby_action_button {{
    background-color: #E4E6EB;
    border: none;
    border-radius: {radius_6}px;
    padding: {pad_12}px {pad_24}px;
    font-size: {size_15}px;
    font-weight: 700;
    color: #050505;
}}

QPushButton#lobby_action_button:hover {{
    background-color: #D8DADF;
}}

QPushButton#lobby_action_button:pressed {{
    background-color: #CCD0D5;
}}

QPushButton#danger_button {{
    background-color: #FFFFFF;
    border: 1px solid #E4E6EB;
    border-radius: {radius_6}px;
    color: #E11D48;
    font-weight: 600;
    padding: {pad_8}px {pad_16}px;
}}

QPushButton#danger_button:hover {{
    background-color: #FFF1F2;
    border-color: #FECDD3;
}}

QPushButton#danger_button:pressed {{
    background-color: #FFE4E6;
}}

QPushButton#gear_button {{
    background-color: #FFFFFF;
    border: 1px solid #E4E6EB;
    border-radius: {radius_18}px;
    width: {size_36}px;
    height: {size_36}px;
    padding: 0px;
}}

QPushButton#gear_button:hover {{
    background-color: #F0F2F5;
}}

QPushButton#gear_button:pressed {{
    background-color: #E4E6EB;
}}

/* Inputs */
QLineEdit {{
    background-color: #F0F2F5;
    border: 1px solid transparent;
    border-radius: {radius_6}px;
    padding: {pad_9}px {pad_12}px;
    font-size: {size_14}px;
    color: #1C1E21;
}}

QLineEdit:focus {{
    background-color: #FFFFFF;
    border: 1px solid #2688EB;
}}

QLineEdit#answer_input {{
    background-color: #FFFFFF;
    border: 2px solid #E4E6EB;
    font-size: {size_18}px;
    padding: {pad_12}px;
    border-radius: {radius_8}px;
}}

QLineEdit#answer_input:focus {{
    border: 2px solid #2688EB;
}}

/* SpinBox */
QSpinBox {{
    background-color: #FFFFFF;
    border: 1px solid #CCD0D5;
    border-radius: {radius_6}px;
    padding: {pad_8}px {pad_12}px;
    font-size: {size_14}px;
}}

QSpinBox:focus {{
    border: 1px solid #2688EB;
}}

/* Combo Box */
QComboBox {{
    background-color: #FFFFFF;
    border: 1px solid #CCD0D5;
    border-radius: {radius_6}px;
    padding: {pad_6}px {pad_12}px;
    font-size: {size_13}px;
    font-weight: 600;
}}

QComboBox:focus {{
    border: 1px solid #2688EB;
}}

QComboBox::drop-down {{
    border: none;
}}

/* CheckBox styling */
QCheckBox {{
    font-size: {size_14}px;
    padding: 3px;
}}

QCheckBox::indicator {{
    width: {size_18}px;
    height: {size_18}px;
}}

/* Lists */
QListWidget {{
    background-color: #FFFFFF;
    border: 1px solid #E4E6EB;
    border-radius: {radius_8}px;
    padding: 4px;
}}

QListWidget::item {{
    padding: {pad_8}px {pad_12}px;
    border-radius: {radius_6}px;
    margin-bottom: 2px;
}}

QListWidget::item:hover {{
    background-color: #F0F2F5;
}}

QListWidget::item:selected {{
    background-color: #E2EEF9;
    color: #2688EB;
    font-weight: 700;
}}

/* FULL RESPONSIVE DYNAMIC TABLE SCALING */
QTableWidget {{
    background-color: #FFFFFF;
    border: 1px solid #E4E6EB;
    border-radius: {radius_8}px;
    gridline-color: #F2F4F7;
    font-size: {size_15_table}px;
}}

QTableWidget::item {{
    padding: {pad_10_table}px;
    font-size: {size_15_table}px;
}}

QHeaderView::section {{
    background-color: #F0F2F5;
    padding: {pad_8}px;
    border: none;
    font-weight: 700;
    color: #65676B;
    font-size: {size_14_table}px;
}}

QScrollBar:vertical {{
    border: none;
    background: #F0F2F5;
    width: 6px;
    border-radius: 3px;
}}

QScrollBar::handle:vertical {{
    background: #B0B3B8;
    border-radius: 3px;
}}

QScrollBar::handle:vertical:hover {{
    background: #8D9196;
}}
"""


# ==========================================
# 7. SPRINT APP MAIN SYSTEM
# ==========================================
class SprintApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        create_svg_assets()
        self.db = DatabaseManager()
        
        # RAM caching of LaTeX math formulas
        self.latex_cache = {}
        
        # QMainWindow Configurations
        self.setWindowTitle("Sprint")
        self.resize(900, 650)
        self.setMinimumSize(850, 600)
        
        # Active States
        self.sprint_questions = []
        self.current_question_index = 0
        self.correct_answers_count = 0
        self.questions_answered_total_count = 0
        self.sprint_time_remaining = 60
        self.sprint_total_time = 60
        self.selected_topic_name = ""
        self.active_student_name = "Ученик"
        self.active_student_gender = "boys"
        self.active_age_cat = "old_2"
        self.sprint_start_time = None
        self.sprint_responses_log = []
        
        # Combo Streaks State
        self.current_streak = 0
        self.wrong_streak = 0
        
        # Load settings from database
        self.sprint_total_time, self.current_zoom_percent, animations_enabled_val = self.db.get_settings()
        self.animations_enabled = (animations_enabled_val == 1)
        
        # Guard zoom range to optimal predefined snapped levels
        if self.current_zoom_percent not in [80, 100, 120, 140, 160, 180]:
            self.current_zoom_percent = 100
            
        self.admin_selected_image_path = None
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.on_timer_tick)
        
        # 1. Flame animation rotational timer (ticks every 200ms)
        self.fire_frame_index = 0
        self.fire_timer = QTimer(self)
        self.fire_timer.setInterval(200)
        self.fire_timer.timeout.connect(self.on_fire_timer_tick)
        
        # 2. Text/GIF milestone auto-hide timer (single shot, 10 seconds)
        self.banner_hide_timer = QTimer(self)
        self.banner_hide_timer.setSingleShot(True)
        self.banner_hide_timer.timeout.connect(self.hide_streak_banner)
        
        # Preload Ronaldo QMovie using absolute PyInstaller-safe path
        self.ronaldo_movie = None
        ronaldo_path = get_asset_path("assets/ronaldo.gif")
        if os.path.exists(ronaldo_path):
            self.ronaldo_movie = QMovie(ronaldo_path)
            
        # 3. Create HOVER OVERLAY POPUP label for results table (pure UX excellence!)
        self.hover_popup = QLabel(self)
        self.hover_popup.setWindowFlags(Qt.ToolTip | Qt.FramelessWindowHint)
        self.hover_popup.setStyleSheet("""
            background-color: #FFFFFF;
            border: 2px solid #2688EB;
            border-radius: 8px;
            padding: 12px;
        """)
        self.hover_popup.setAlignment(Qt.AlignCenter)
        self.hover_popup.hide()
        
        # 4. GIF manager screen-specific active movie cache
        self.manager_preview_movie = None
        self.active_manager_gif_id = None
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(25, 25, 25, 25)
        
        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget)
        
        # Create all views
        self.create_lobby_view()          # Index 0
        self.create_topic_selection_view()# Index 1
        self.create_sprint_quiz_view()     # Index 2
        self.create_sprint_result_view()   # Index 3
        self.create_history_view()         # Index 4
        self.create_settings_view()        # Index 5
        self.create_admin_view()           # Index 6
        self.create_leaderboard_view()     # Index 7
        self.create_gif_manager_view()     # Index 8! (New dedicated screen!)
        
        # Set dynamic QSS and scale elements based on zoom level
        self.apply_zoom_scale(self.current_zoom_percent)
        
        self.show_lobby()
        
        # Trigger silent automated daily backup in background
        if BACKUPS_ENABLED:
            self.trigger_daily_auto_backup()

    # ==========================================
    # RESPONSIVE SCALE / ZOOM CONTROL
    # ==========================================
    def wheelEvent(self, event):
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self.adjust_zoom(20) # Snaps to 20% steps!
            elif delta < 0:
                self.adjust_zoom(-20)
            event.accept()
        else:
            super().wheelEvent(event)

    def adjust_zoom(self, amount):
        new_zoom = self.current_zoom_percent + amount
        if new_zoom < 80: new_zoom = 80
        if new_zoom > 180: new_zoom = 180
        
        if new_zoom != self.current_zoom_percent:
            self.current_zoom_percent = new_zoom
            self.apply_zoom_scale(self.current_zoom_percent)
            
            # Update Settings spinbox
            self.zoom_spinbox.setValue(self.current_zoom_percent)
            
            # Save settings
            self.db.update_settings(self.sprint_total_time, self.current_zoom_percent, 1 if self.animations_enabled else 0)

    def apply_zoom_scale(self, zoom_percent):
        scale = zoom_percent / 100.0
        
        scaled_qss = VK_FACEBOOK_QSS_TEMPLATE.format(
            size_34=int(34 * scale),
            size_26=int(26 * scale),
            size_22=int(22 * scale),
            size_18=int(18 * scale),
            size_16=int(16 * scale),
            size_15=int(15 * scale),
            size_14=int(14 * scale),
            size_13=int(13 * scale),
            size_15_table=int(16 * scale), # Enlarged table body
            size_14_table=int(15 * scale), # Enlarged table header
            pad_10_table=int(11 * scale),
            size_36=int(36 * scale),
            radius_18=int(18 * scale),
            radius_8=int(8 * scale),
            radius_6=int(6 * scale),
            pad_12=int(12 * scale),
            pad_24=int(24 * scale),
            pad_8=int(8 * scale),
            pad_16=int(16 * scale),
            pad_9=int(9 * scale),
            pad_6=int(6 * scale),
            pad_14=int(14 * scale)
        )
        self.setStyleSheet(scaled_qss)
        
        # Scale button icons
        scaled_icon_size = QSize(int(18 * scale), int(18 * scale))
        self.btn_start.setIconSize(scaled_icon_size)
        self.btn_leaderboard.setIconSize(scaled_icon_size)
        self.btn_history.setIconSize(scaled_icon_size)
        self.btn_settings.setIconSize(scaled_icon_size)
        if hasattr(self, 'btn_admin_backup'):
            self.btn_admin_backup.setIconSize(scaled_icon_size)
        
        # Scale button heights
        self.btn_start_sprint.setMinimumHeight(int(45 * scale))
        self.quiz_next_button.setMinimumHeight(int(48 * scale))
        self.btn_save_settings.setMinimumHeight(int(45 * scale))
        self.btn_lobby_result.setMinimumHeight(int(45 * scale))
        self.btn_lobby_leaderboard.setMinimumHeight(int(45 * scale))
        
        # Increase minimum height of the question card so that uploaded image tasks are large and readable!
        self.quiz_card.setMinimumHeight(int(340 * scale))
        
        # CRITICAL LAYOUT SCALE WIN: Scale the animation fixed-height container dynamically!
        # Increased to 145px scaled to beautifully fit both the large GIF and the text label under it!
        self.animation_container.setFixedHeight(int(145 * scale))
        
        # Scale fire label
        if self.fire_timer.isActive():
            self.on_fire_timer_tick()
        else:
            blank_pix = QPixmap(int(40 * scale), int(40 * scale))
            blank_pix.fill(Qt.transparent)
            self.quiz_fire_label.setPixmap(blank_pix)
            
        # Scale active movie inside container dynamically
        movie = self.quiz_streak_movie_label.movie()
        if movie and movie.state() == QMovie.Running:
            movie.setScaledSize(QSize(int(160 * scale), int(100 * scale)))
            
        # Rescale table heights
        self.leaderboard_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.history_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.result_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        
        self.leaderboard_table.resizeRowsToContents()
        self.history_table.resizeRowsToContents()
        self.result_table.resizeRowsToContents()


    # ==========================================
    # VIEW GENERATORS
    # ==========================================
    
    # --- 1. LOBBY VIEW ---
    def create_lobby_view(self):
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setAlignment(Qt.AlignCenter)
        
        title_label = QLabel("Спринт")
        title_label.setObjectName("title_label")
        title_label.setAlignment(Qt.AlignCenter)
        
        subtitle_label = QLabel("Тренажер быстрых ответов для учеников")
        subtitle_label.setObjectName("subtitle_label")
        subtitle_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)
        layout.addSpacing(15)
        
        buttons_container = QWidget()
        buttons_layout = QVBoxLayout(buttons_container)
        buttons_layout.setSpacing(12)
        buttons_layout.setContentsMargins(40, 0, 40, 0)
        
        self.btn_start = QPushButton(" Начать Спринт")
        self.btn_start.setObjectName("lobby_action_button_primary")
        self.btn_start.setIcon(QIcon(get_asset_path("assets/play.svg")))
        self.btn_start.setCursor(Qt.PointingHandCursor)
        self.btn_start.clicked.connect(self.show_topic_selection)
        
        self.btn_leaderboard = QPushButton(" Таблица лидеров")
        self.btn_leaderboard.setObjectName("lobby_action_button")
        self.btn_leaderboard.setIcon(QIcon(get_asset_path("assets/trophy.svg")))
        self.btn_leaderboard.setCursor(Qt.PointingHandCursor)
        self.btn_leaderboard.clicked.connect(self.show_leaderboard_screen)
        
        self.btn_history = QPushButton(" История результатов")
        self.btn_history.setObjectName("lobby_action_button")
        self.btn_history.setIcon(QIcon(get_asset_path("assets/history.svg")))
        self.btn_history.setCursor(Qt.PointingHandCursor)
        self.btn_history.clicked.connect(self.show_history)
        
        self.btn_settings = QPushButton(" Настройки")
        self.btn_settings.setObjectName("lobby_action_button")
        self.btn_settings.setIcon(QIcon(get_asset_path("assets/settings.svg")))
        self.btn_settings.setCursor(Qt.PointingHandCursor)
        self.btn_settings.clicked.connect(self.show_settings)
        
        buttons_layout.addWidget(self.btn_start)
        buttons_layout.addWidget(self.btn_leaderboard)
        buttons_layout.addWidget(self.btn_history)
        buttons_layout.addWidget(self.btn_settings)
        
        buttons_container.setMaximumWidth(380)
        layout.addWidget(buttons_container, alignment=Qt.AlignCenter)
        
        layout.addStretch()
        footer_layout = QHBoxLayout()
        footer_layout.addStretch()
        
        btn_admin = QPushButton()
        btn_admin.setObjectName("gear_button")
        btn_admin.setIcon(QIcon(get_asset_path("assets/gear.svg")))
        btn_admin.setIconSize(QSize(20, 20))
        btn_admin.setToolTip("Панель администратора")
        btn_admin.setCursor(Qt.PointingHandCursor)
        btn_admin.clicked.connect(self.attempt_admin_access)
        footer_layout.addWidget(btn_admin)
        
        layout.addLayout(footer_layout)
        self.stacked_widget.addWidget(view) # Index 0

    # --- 2. HIERARCHICAL TOPIC SELECTION VIEW (CLASSES -> TOPICS) ---
    def create_topic_selection_view(self):
        view = QWidget()
        layout = QVBoxLayout(view)
        
        header_layout = QHBoxLayout()
        self.topic_section_title = QLabel("Выберите класс")
        self.topic_section_title.setObjectName("section_title")
        header_layout.addWidget(self.topic_section_title)
        header_layout.addStretch()
        
        self.btn_topic_back = QPushButton(" Назад")
        self.btn_topic_back.setIcon(QIcon(get_asset_path("assets/back.svg")))
        self.btn_topic_back.setIconSize(QSize(16, 16))
        self.btn_topic_back.setCursor(Qt.PointingHandCursor)
        self.btn_topic_back.clicked.connect(self.on_topic_selection_back_clicked)
        header_layout.addWidget(self.btn_topic_back)
        layout.addLayout(header_layout)
        layout.addSpacing(15)
        
        self.topic_selector_stack = QStackedWidget()
        layout.addWidget(self.topic_selector_stack)
        
        # --- Page 0: Class Grid Area ---
        self.class_grid_scroll = QScrollArea()
        self.class_grid_scroll.setWidgetResizable(True)
        self.class_grid_scroll.setFrameShape(QFrame.NoFrame)
        
        self.class_grid_widget = QWidget()
        self.class_grid_layout = QVBoxLayout(self.class_grid_widget)
        self.class_grid_layout.setSpacing(10)
        self.class_grid_layout.setAlignment(Qt.AlignTop)
        self.class_grid_scroll.setWidget(self.class_grid_widget)
        
        self.topic_selector_stack.addWidget(self.class_grid_scroll) # Index 0
        
        # --- Page 1: Topics List Area ---
        topics_list_page = QWidget()
        topics_list_layout = QVBoxLayout(topics_list_page)
        topics_list_layout.setContentsMargins(0, 0, 0, 0)
        
        self.topics_list_widget = QListWidget()
        self.topics_list_widget.setCursor(Qt.PointingHandCursor)
        self.topics_list_widget.itemDoubleClicked.connect(self.start_sprint_on_selected_topic)
        self.topics_list_widget.setStyleSheet("font-size: 16px;")
        
        topics_list_layout.addWidget(self.topics_list_widget)
        self.topic_selector_stack.addWidget(topics_list_page) # Index 1
        
        layout.addSpacing(15)
        self.btn_start_sprint = QPushButton(" Запустить Спринт!")
        self.btn_start_sprint.setObjectName("primary_button")
        self.btn_start_sprint.setIcon(QIcon(get_asset_path("assets/rocket.svg")))
        self.btn_start_sprint.setIconSize(QSize(16, 16))
        self.btn_start_sprint.setCursor(Qt.PointingHandCursor)
        self.btn_start_sprint.clicked.connect(self.start_sprint_on_selected_topic)
        layout.addWidget(self.btn_start_sprint)
        
        self.btn_start_sprint.hide()
        self.stacked_widget.addWidget(view) # Index 1

    # --- 3. SPRINT QUIZ VIEW ---
    def create_sprint_quiz_view(self):
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(25, 10, 25, 25)
        layout.setAlignment(Qt.AlignTop)
        
        # Row 1: Top Header row (Level alignment of Title, Counter, and Timer!)
        top_header_layout = QHBoxLayout()
        top_header_layout.setContentsMargins(0, 0, 0, 0)
        
        self.quiz_topic_label = QLabel("Тема: Дроби")
        self.quiz_topic_label.setObjectName("card_title")
        self.quiz_topic_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        self.quiz_counter_label = QLabel("Верно: 0 | Задание 1")
        self.quiz_counter_label.setObjectName("question_counter")
        self.quiz_counter_label.setAlignment(Qt.AlignCenter)
        
        self.timer_container = QWidget()
        self.timer_layout = QVBoxLayout(self.timer_container)
        self.timer_layout.setContentsMargins(0, 0, 0, 0)
        self.timer_layout.setSpacing(3)
        self.timer_layout.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        self.quiz_timer_label = QLabel("Осталось: 60 сек")
        self.quiz_timer_label.setObjectName("timer_label")
        self.quiz_timer_label.setAlignment(Qt.AlignCenter)
        
        self.quiz_fire_label = QLabel()
        self.quiz_fire_label.setAlignment(Qt.AlignCenter)
        # Keep visible but clear/transparent initially to maintain rock-solid layout alignment!
        
        self.timer_layout.addWidget(self.quiz_timer_label)
        self.timer_layout.addWidget(self.quiz_fire_label)
        
        top_header_layout.addWidget(self.quiz_topic_label, stretch=2)
        top_header_layout.addWidget(self.quiz_counter_label, stretch=3)
        top_header_layout.addWidget(self.timer_container, stretch=2)
        
        layout.addLayout(top_header_layout)
        layout.addSpacing(10)
        
        # Row 3: Central Task Card (displays question) - Positioned directly under top header row!
        self.quiz_card = QFrame()
        self.quiz_card.setObjectName("card_frame")
        self.quiz_card_layout = QVBoxLayout(self.quiz_card)
        self.quiz_card_layout.setContentsMargins(30, 40, 30, 40)
        self.quiz_card_layout.setAlignment(Qt.AlignCenter)
        
        self.quiz_question_label = QLabel("")
        self.quiz_question_label.setObjectName("question_text")
        self.quiz_question_label.setAlignment(Qt.AlignCenter)
        self.quiz_question_label.setWordWrap(True)
        self.quiz_card_layout.addWidget(self.quiz_question_label)
        
        self.quiz_math_label = QLabel()
        self.quiz_math_label.setAlignment(Qt.AlignCenter)
        self.quiz_card_layout.addWidget(self.quiz_math_label)
        
        self.quiz_image_label = QLabel()
        self.quiz_image_label.setAlignment(Qt.AlignCenter)
        self.quiz_image_label.setStyleSheet("border: 1px solid #E4E6EB; border-radius: 6px; background-color: #F8FAFC;")
        self.quiz_card_layout.addWidget(self.quiz_image_label)
        
        layout.addWidget(self.quiz_card)
        layout.addSpacing(10)
        
        # Row 4: Dedicated CONSTANT FIXED-HEIGHT Animation container!
        # Positioned cleanly under the question box, between the tasks and the answers!
        # Dual-Stacked to hold both the GIF and its text detail cleanly under it!
        self.animation_container = QWidget()
        self.animation_container_layout = QVBoxLayout(self.animation_container)
        self.animation_container_layout.setContentsMargins(0, 0, 0, 0)
        self.animation_container_layout.setSpacing(2)
        self.animation_container_layout.setAlignment(Qt.AlignCenter)
        
        self.quiz_streak_movie_label = QLabel()
        self.quiz_streak_movie_label.setAlignment(Qt.AlignCenter)
        
        self.quiz_streak_text_label = QLabel()
        self.quiz_streak_text_label.setAlignment(Qt.AlignCenter)
        
        self.animation_container_layout.addWidget(self.quiz_streak_movie_label)
        self.animation_container_layout.addWidget(self.quiz_streak_text_label)
        
        # Set fixed height initially, gets dynamically scaled on apply_zoom_scale()
        self.animation_container.setFixedHeight(145)
        layout.addWidget(self.animation_container)
        layout.addSpacing(10)
        
        # Input & Button
        input_layout = QHBoxLayout()
        self.quiz_answer_input = QLineEdit()
        self.quiz_answer_input.setObjectName("answer_input")
        self.quiz_answer_input.setPlaceholderText("Введите ваш ответ здесь...")
        self.quiz_answer_input.returnPressed.connect(self.on_submit_answer)
        input_layout.addWidget(self.quiz_answer_input, stretch=3)
        
        self.quiz_next_button = QPushButton("Далее →")
        self.quiz_next_button.setObjectName("primary_button")
        self.quiz_next_button.setCursor(Qt.PointingHandCursor)
        self.quiz_next_button.clicked.connect(self.on_submit_answer)
        input_layout.addWidget(self.quiz_next_button, stretch=1)
        layout.addLayout(input_layout)
        layout.addSpacing(20)
        
        footer_layout = QHBoxLayout()
        btn_quit = QPushButton(" Завершить спринт")
        btn_quit.setObjectName("danger_button")
        btn_quit.setIcon(QIcon(get_asset_path("assets/trash.svg")))
        btn_quit.setIconSize(QSize(15, 15))
        btn_quit.setCursor(Qt.PointingHandCursor)
        btn_quit.clicked.connect(self.confirm_quit_sprint)
        footer_layout.addWidget(btn_quit)
        footer_layout.addStretch()
        layout.addLayout(footer_layout)
        
        self.stacked_widget.addWidget(view) # Index 2

    # --- 4. SPRINT RESULT VIEW (WITH HOVER POPUPS) ---
    def create_sprint_result_view(self):
        view = QWidget()
        layout = QVBoxLayout(view)
        
        section_title = QLabel("Итоги Спринта")
        section_title.setObjectName("section_title")
        layout.addWidget(section_title)
        layout.addSpacing(10)
        
        stats_layout = QHBoxLayout()
        
        card1 = QFrame()
        card1.setObjectName("card_frame")
        c1_lay = QVBoxLayout(card1)
        self.result_score_label = QLabel("0")
        self.result_score_label.setObjectName("title_label")
        self.result_score_label.setAlignment(Qt.AlignCenter)
        c1_sub = QLabel("Решено задач")
        c1_sub.setObjectName("subtitle_label")
        c1_sub.setAlignment(Qt.AlignCenter)
        c1_lay.addWidget(self.result_score_label)
        c1_lay.addWidget(c1_sub)
        stats_layout.addWidget(card1)
        
        card2 = QFrame()
        card2.setObjectName("card_frame")
        c2_lay = QVBoxLayout(card2)
        self.result_time_label = QLabel("0 сек")
        self.result_time_label.setObjectName("title_label")
        self.result_time_label.setAlignment(Qt.AlignCenter)
        c2_sub = QLabel("Времени ушло")
        c2_sub.setObjectName("subtitle_label")
        c2_sub.setAlignment(Qt.AlignCenter)
        c2_lay.addWidget(self.result_time_label)
        c2_lay.addWidget(c2_sub)
        stats_layout.addWidget(card2)
        
        layout.addLayout(stats_layout)
        layout.addSpacing(20)
        
        tbl_label = QLabel("Подробный разбор ответов (Наведите мышку для просмотра задания):")
        tbl_label.setObjectName("card_title")
        layout.addWidget(tbl_label)
        layout.addSpacing(5)
        
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(4)
        self.result_table.setHorizontalHeaderLabels(["Задание", "Ваш ответ", "Правильный", "Результат"])
        
        res_header = self.result_table.horizontalHeader()
        res_header.setSectionResizeMode(0, QHeaderView.Stretch)
        res_header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        res_header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        res_header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        
        self.result_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        
        # PRO UX TRICK: Enable Mouse Tracking so cellEntered triggers immediately on cursor hover!
        self.result_table.setMouseTracking(True)
        self.result_table.cellEntered.connect(self.on_result_table_hover)
        
        self.result_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.result_table.setSelectionMode(QAbstractItemView.NoSelection)
        layout.addWidget(self.result_table)
        
        layout.addSpacing(15)
        
        self.btn_lobby_result = QPushButton("Вернуться в Главное Меню")
        self.btn_lobby_result.setObjectName("primary_button")
        self.btn_lobby_result.setCursor(Qt.PointingHandCursor)
        self.btn_lobby_result.clicked.connect(self.show_lobby)
        layout.addWidget(self.btn_lobby_result)
        
        self.stacked_widget.addWidget(view) # Index 3

    # --- 5. HISTORY VIEW ---
    def create_history_view(self):
        view = QWidget()
        layout = QVBoxLayout(view)
        
        header_layout = QHBoxLayout()
        section_title = QLabel("История результатов")
        section_title.setObjectName("section_title")
        header_layout.addWidget(section_title)
        header_layout.addStretch()
        
        btn_back = QPushButton(" Назад")
        btn_back.setIcon(QIcon(get_asset_path("assets/back.svg")))
        btn_back.setIconSize(QSize(16, 16))
        btn_back.setCursor(Qt.PointingHandCursor)
        btn_back.clicked.connect(self.show_lobby)
        header_layout.addWidget(btn_back)
        
        layout.addLayout(header_layout)
        layout.addSpacing(15)
        
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels(["Дата и время", "Ученик", "Тема спринта", "Результат", "Время (сек)"])
        
        hist_header = self.history_table.horizontalHeader()
        hist_header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        hist_header.setSectionResizeMode(1, QHeaderView.Stretch)
        hist_header.setSectionResizeMode(2, QHeaderView.Stretch)
        hist_header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        hist_header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
        self.history_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        
        self.history_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        layout.addWidget(self.history_table)
        
        layout.addSpacing(15)
        
        control_layout = QHBoxLayout()
        btn_clear = QPushButton(" Стереть историю")
        btn_clear.setObjectName("danger_button")
        btn_clear.setIcon(QIcon(get_asset_path("assets/trash.svg")))
        btn_clear.setIconSize(QSize(16, 16))
        btn_clear.setCursor(Qt.PointingHandCursor)
        btn_clear.clicked.connect(self.clear_history_data)
        control_layout.addWidget(btn_clear)
        control_layout.addStretch()
        layout.addLayout(control_layout)
        
        self.stacked_widget.addWidget(view) # Index 4

    # --- 6. SETTINGS VIEW ---
    def create_settings_view(self):
        view = QWidget()
        layout = QVBoxLayout(view)
        
        header_layout = QHBoxLayout()
        section_title = QLabel("Настройки")
        section_title.setObjectName("section_title")
        header_layout.addWidget(section_title)
        header_layout.addStretch()
        
        btn_back = QPushButton(" Назад")
        btn_back.setIcon(QIcon(get_asset_path("assets/back.svg")))
        btn_back.setIconSize(QSize(16, 16))
        btn_back.setCursor(Qt.PointingHandCursor)
        btn_back.clicked.connect(self.show_lobby)
        header_layout.addWidget(btn_back)
        
        layout.addLayout(header_layout)
        layout.addSpacing(20)
        
        card = QFrame()
        card.setObjectName("card_frame")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(25, 25, 25, 25)
        card_layout.setSpacing(15)
        
        # Option 1: Timer setting
        row_time = QHBoxLayout()
        lbl_time = QLabel("Секунд на один спринт:")
        lbl_time.setObjectName("card_title")
        row_time.addWidget(lbl_time)
        row_time.addStretch()
        
        self.time_combo = QComboBox()
        self.time_combo.setCursor(Qt.PointingHandCursor)
        self.time_combo.addItem("60 секунд (1 мин)", 60)
        self.time_combo.addItem("180 секунд (3 мин)", 180)
        self.time_combo.addItem("300 секунд (5 мин)", 300)
        self.time_combo.addItem("600 секунд (10 мин)", 600)
        self.time_combo.addItem("900 секунд (15 мин)", 900)
        row_time.addWidget(self.time_combo)
        card_layout.addLayout(row_time)
        
        # Option 2: Scale/Zoom setting
        row_zoom = QHBoxLayout()
        lbl_zoom = QLabel("Размер интерфейса (масштаб):")
        lbl_zoom.setObjectName("card_title")
        row_zoom.addWidget(lbl_zoom)
        row_zoom.addStretch()
        
        self.zoom_spinbox = QSpinBox()
        self.zoom_spinbox.setRange(80, 180)
        self.zoom_spinbox.setSingleStep(20)
        self.zoom_spinbox.setValue(100)
        self.zoom_spinbox.setSuffix("%")
        self.zoom_spinbox.valueChanged.connect(self.on_zoom_spinbox_changed)
        row_zoom.addWidget(self.zoom_spinbox)
        card_layout.addLayout(row_zoom)
        
        # Option 3: Animations Enabled Toggle
        row_animations = QHBoxLayout()
        lbl_animations = QLabel("Праздничные анимации побед:")
        lbl_animations.setObjectName("card_title")
        row_animations.addWidget(lbl_animations)
        row_animations.addStretch()
        
        self.animations_combo = QComboBox()
        self.animations_combo.addItems(["✅ Включены", "❌ Выключены"])
        row_animations.addWidget(self.animations_combo)
        card_layout.addLayout(row_animations)
        
        card_layout.addSpacing(10)
        
        # PRO DYNAMIC REWARDS OPTION: Opens the interactive GIF Manager screen!
        btn_manage_gifs = QPushButton(" 🖼️ Настройка GIF-анимаций наград...")
        btn_manage_gifs.setIcon(QIcon(get_asset_path("assets/folder.svg")))
        btn_manage_gifs.setIconSize(QSize(15, 15))
        btn_manage_gifs.setCursor(Qt.PointingHandCursor)
        btn_manage_gifs.clicked.connect(self.show_gif_manager_screen)
        card_layout.addWidget(btn_manage_gifs)
        
        desc_label = QLabel(
            "Подсказка: Вы также можете масштабировать размер шрифта в любой момент\n"
            "из любого окна программы, зажав клавишу CTRL и прокручивая колесико мыши!"
        )
        desc_label.setStyleSheet("color: #65676B; font-size: 13px; line-height: 1.4;")
        card_layout.addWidget(desc_label)
        
        layout.addWidget(card)
        layout.addSpacing(15)
        
        self.btn_save_settings = QPushButton("Сохранить настройки")
        self.btn_save_settings.setObjectName("primary_button")
        self.btn_save_settings.setCursor(Qt.PointingHandCursor)
        self.btn_save_settings.clicked.connect(self.save_settings_data)
        layout.addWidget(self.btn_save_settings)
        
        layout.addStretch()
        self.stacked_widget.addWidget(view) # Index 5

    # --- 7. ADMIN PANEL VIEW ---
    def create_admin_view(self):
        view = QWidget()
        layout = QVBoxLayout(view)
        
        header_layout = QHBoxLayout()
        section_title = QLabel("Панель Администратора")
        section_title.setObjectName("section_title")
        header_layout.addWidget(section_title)
        header_layout.addStretch()
        
        if BACKUPS_ENABLED:
            self.btn_admin_backup = QPushButton(" Резервные копии")
            self.btn_admin_backup.setIcon(QIcon(get_asset_path("assets/settings.svg")))
            self.btn_admin_backup.setIconSize(QSize(16, 16))
            self.btn_admin_backup.setCursor(Qt.PointingHandCursor)
            self.btn_admin_backup.clicked.connect(self.show_backup_dialog)
            header_layout.addWidget(self.btn_admin_backup)
            header_layout.addSpacing(10)
        
        btn_back = QPushButton(" Назад в лобби")
        btn_back.setIcon(QIcon(get_asset_path("assets/back.svg")))
        btn_back.setIconSize(QSize(16, 16))
        btn_back.setCursor(Qt.PointingHandCursor)
        btn_back.clicked.connect(self.show_lobby)
        header_layout.addWidget(btn_back)
        
        layout.addLayout(header_layout)
        layout.addSpacing(15)
        
        columns_layout = QHBoxLayout()
        
        # --- LEFT PANEL (CLASSES & TOPICS) ---
        left_col = QFrame()
        left_col.setObjectName("card_frame")
        left_layout = QVBoxLayout(left_col)
        left_layout.setContentsMargins(15, 15, 15, 15)
        
        lbl_cl = QLabel("Класс / Раздел:")
        lbl_cl.setStyleSheet("font-weight: bold; font-size: 12px; color: #4E5968;")
        left_layout.addWidget(lbl_cl)
        
        cl_bar = QHBoxLayout()
        self.admin_class_combo = QComboBox()
        self.admin_class_combo.currentIndexChanged.connect(self.on_admin_class_changed)
        cl_bar.addWidget(self.admin_class_combo, stretch=1)
        
        btn_add_cl = QPushButton("")
        btn_add_cl.setObjectName("primary_button")
        btn_add_cl.setIcon(QIcon(get_asset_path("assets/plus.svg")))
        btn_add_cl.setIconSize(QSize(12, 12))
        btn_add_cl.setCursor(Qt.PointingHandCursor)
        btn_add_cl.setToolTip("Создать новый класс")
        btn_add_cl.clicked.connect(self.add_new_class)
        cl_bar.addWidget(btn_add_cl)
        
        btn_del_cl = QPushButton("")
        btn_del_cl.setObjectName("danger_button")
        btn_del_cl.setIcon(QIcon(get_asset_path("assets/trash.svg")))
        btn_del_cl.setIconSize(QSize(12, 12))
        btn_del_cl.setCursor(Qt.PointingHandCursor)
        btn_del_cl.setToolTip("Удалить выбранный класс")
        btn_del_cl.clicked.connect(self.delete_selected_class)
        cl_bar.addWidget(btn_del_cl)
        
        btn_up_cl = QPushButton("▲")
        btn_up_cl.setCursor(Qt.PointingHandCursor)
        btn_up_cl.setToolTip("Переместить класс выше")
        btn_up_cl.setStyleSheet("font-size: 11px; font-weight: bold; min-width: 22px; max-width: 22px; padding: 2px;")
        btn_up_cl.clicked.connect(self.move_class_up)
        cl_bar.addWidget(btn_up_cl)
        
        btn_down_cl = QPushButton("▼")
        btn_down_cl.setCursor(Qt.PointingHandCursor)
        btn_down_cl.setToolTip("Переместить класс ниже")
        btn_down_cl.setStyleSheet("font-size: 11px; font-weight: bold; min-width: 22px; max-width: 22px; padding: 2px;")
        btn_down_cl.clicked.connect(self.move_class_down)
        cl_bar.addWidget(btn_down_cl)
        
        btn_rename_cl = QPushButton("✏️")
        btn_rename_cl.setCursor(Qt.PointingHandCursor)
        btn_rename_cl.setToolTip("Переименовать выбранный класс")
        btn_rename_cl.setStyleSheet("font-size: 11px; font-weight: bold; min-width: 22px; max-width: 22px; padding: 2px;")
        btn_rename_cl.clicked.connect(self.rename_selected_class)
        cl_bar.addWidget(btn_rename_cl)
        
        left_layout.addLayout(cl_bar)
        
        left_layout.addSpacing(10)
        
        lbl_topics = QLabel("Тематики спринтов")
        lbl_topics.setObjectName("card_title")
        left_layout.addWidget(lbl_topics)
        
        # QHBoxLayout for topics list and its ordering controls!
        topics_list_layout = QHBoxLayout()
        self.admin_topics_list = QListWidget()
        self.admin_topics_list.itemSelectionChanged.connect(self.on_admin_topic_selected)
        topics_list_layout.addWidget(self.admin_topics_list, stretch=1)
        
        topic_order_layout = QVBoxLayout()
        topic_order_layout.setSpacing(5)
        
        btn_up_topic = QPushButton("▲")
        btn_up_topic.setCursor(Qt.PointingHandCursor)
        btn_up_topic.setToolTip("Переместить тему выше")
        btn_up_topic.setStyleSheet("font-size: 13px; font-weight: bold; min-width: 26px; max-width: 26px; padding: 4px;")
        btn_up_topic.clicked.connect(self.move_topic_up)
        
        btn_down_topic = QPushButton("▼")
        btn_down_topic.setCursor(Qt.PointingHandCursor)
        btn_down_topic.setToolTip("Переместить тему ниже")
        btn_down_topic.setStyleSheet("font-size: 13px; font-weight: bold; min-width: 26px; max-width: 26px; padding: 4px;")
        btn_down_topic.clicked.connect(self.move_topic_down)
        
        topic_order_layout.addWidget(btn_up_topic)
        topic_order_layout.addWidget(btn_down_topic)
        topic_order_layout.addStretch()
        topics_list_layout.addLayout(topic_order_layout)
        
        left_layout.addLayout(topics_list_layout)
        
        self.new_topic_input = QLineEdit()
        self.new_topic_input.setPlaceholderText("Название новой темы...")
        left_layout.addWidget(self.new_topic_input)
        
        topic_btn_layout = QHBoxLayout()
        btn_add_topic = QPushButton(" Добавить")
        btn_add_topic.setObjectName("primary_button")
        btn_add_topic.setIcon(QIcon(get_asset_path("assets/plus.svg")))
        btn_add_topic.setIconSize(QSize(14, 14))
        btn_add_topic.setCursor(Qt.PointingHandCursor)
        btn_add_topic.clicked.connect(self.add_new_topic)
        topic_btn_layout.addWidget(btn_add_topic)
        
        btn_del_topic = QPushButton(" Удалить тему")
        btn_del_topic.setObjectName("danger_button")
        btn_del_topic.setIcon(QIcon(get_asset_path("assets/trash.svg")))
        btn_del_topic.setIconSize(QSize(14, 14))
        btn_del_topic.setCursor(Qt.PointingHandCursor)
        btn_del_topic.clicked.connect(self.delete_selected_topic)
        topic_btn_layout.addWidget(btn_del_topic)
        
        btn_rename_topic = QPushButton(" ✏️ Имя")
        btn_rename_topic.setIcon(QIcon(get_asset_path("assets/settings.svg")))
        btn_rename_topic.setIconSize(QSize(14, 14))
        btn_rename_topic.setCursor(Qt.PointingHandCursor)
        btn_rename_topic.setToolTip("Переименовать выбранную тему")
        btn_rename_topic.clicked.connect(self.rename_selected_topic)
        topic_btn_layout.addWidget(btn_rename_topic)
        
        left_layout.addLayout(topic_btn_layout)
        
        columns_layout.addWidget(left_col, stretch=2)
        
        # --- RIGHT PANEL (QUESTIONS) ---
        right_col = QFrame()
        right_col.setObjectName("card_frame")
        right_layout = QVBoxLayout(right_col)
        right_layout.setContentsMargins(15, 15, 15, 15)
        
        self.admin_questions_title = QLabel("Вопросы (выберите тему)")
        self.admin_questions_title.setObjectName("card_title")
        right_layout.addWidget(self.admin_questions_title)
        
        self.admin_questions_list = QListWidget()
        right_layout.addWidget(self.admin_questions_list)
        
        type_layout = QHBoxLayout()
        lbl_type = QLabel("Формат задания:")
        lbl_type.setStyleSheet("font-weight: bold; font-size: 12px; color: #4E5968;")
        
        self.q_type_combo = QComboBox()
        self.q_type_combo.setIconSize(QSize(16, 16))
        self.q_type_combo.addItem(QIcon(get_asset_path("assets/text.svg")), " Обычный текст")
        self.q_type_combo.addItem(QIcon(get_asset_path("assets/math.svg")), " Формула LaTeX (Дроби)")
        self.q_type_combo.addItem(QIcon(get_asset_path("assets/folder.svg")), " Загрузить фото задачи")
        
        self.q_type_combo.currentIndexChanged.connect(self.on_question_type_changed)
        type_layout.addWidget(lbl_type)
        type_layout.addWidget(self.q_type_combo, stretch=1)
        right_layout.addLayout(type_layout)
        
        self.admin_fields_stack = QStackedWidget()
        
        # Frame 1: Text type input
        self.field_text_frame = QWidget()
        lay_text = QVBoxLayout(self.field_text_frame)
        lay_text.setContentsMargins(0, 5, 0, 5)
        lbl_q_text = QLabel("Текст вопроса:")
        lbl_q_text.setStyleSheet("font-size: 11px; color: #65676B;")
        self.input_q_text = QLineEdit()
        self.input_q_text.setPlaceholderText("Например: 5 * 5 = ?")
        lay_text.addWidget(lbl_q_text)
        lay_text.addWidget(self.input_q_text)
        self.admin_fields_stack.addWidget(self.field_text_frame)
        
        # Frame 2: LaTeX type input
        self.field_latex_frame = QWidget()
        lay_latex = QVBoxLayout(self.field_latex_frame)
        lay_latex.setContentsMargins(0, 5, 0, 5)
        lbl_q_latex = QLabel("Формула LaTeX (дробь пишется как \\frac{1}{2}):")
        lbl_q_latex.setStyleSheet("font-size: 11px; color: #65676B;")
        self.input_q_latex = QLineEdit()
        self.input_q_latex.setPlaceholderText("Например: \\frac{3}{4} + \\frac{1}{4} = ?")
        
        btn_preview_latex = QPushButton(" Показать предпросмотр")
        btn_preview_latex.setIcon(QIcon(get_asset_path("assets/eye.svg")))
        btn_preview_latex.setIconSize(QSize(15, 15))
        btn_preview_latex.setCursor(Qt.PointingHandCursor)
        btn_preview_latex.clicked.connect(self.on_preview_latex_clicked)
        
        self.latex_preview_label = QLabel("[Превью вертикальной дроби]")
        self.latex_preview_label.setAlignment(Qt.AlignCenter)
        self.latex_preview_label.setStyleSheet("background-color: #F8FAFC; border: 1px solid #E4E6EB; padding: 10px; border-radius: 6px;")
        
        lay_latex.addWidget(lbl_q_latex)
        lay_latex.addWidget(self.input_q_latex)
        lay_latex.addWidget(btn_preview_latex)
        lay_latex.addWidget(self.latex_preview_label)
        self.admin_fields_stack.addWidget(self.field_latex_frame)
        
        # Frame 3: Image / Photo Task type input
        self.field_image_frame = QWidget()
        lay_image = QVBoxLayout(self.field_image_frame)
        lay_image.setContentsMargins(0, 5, 0, 5)
        lbl_q_image = QLabel("Загрузка фотографии задачи:")
        lbl_q_image.setStyleSheet("font-size: 11px; color: #65676B;")
        
        btn_choose_image = QPushButton(" Выбрать файл на компьютере")
        btn_choose_image.setIcon(QIcon(get_asset_path("assets/folder.svg")))
        btn_choose_image.setIconSize(QSize(15, 15))
        btn_choose_image.setCursor(Qt.PointingHandCursor)
        btn_choose_image.clicked.connect(self.on_choose_image_clicked)
        
        self.admin_image_path_label = QLineEdit()
        self.admin_image_path_label.setReadOnly(True)
        self.admin_image_path_label.setPlaceholderText("Файл не выбран")
        
        self.admin_image_thumbnail_label = QLabel("[Превью фото]")
        self.admin_image_thumbnail_label.setAlignment(Qt.AlignCenter)
        self.admin_image_thumbnail_label.setStyleSheet("background-color: #F8FAFC; border: 1px solid #E4E6EB; padding: 10px; border-radius: 6px;")
        self.admin_image_thumbnail_label.setFixedHeight(95)
        
        lay_image.addWidget(lbl_q_image)
        lay_image.addWidget(btn_choose_image)
        lay_image.addWidget(self.admin_image_path_label)
        lay_image.addWidget(self.admin_image_thumbnail_label)
        self.admin_fields_stack.addWidget(self.field_image_frame)
        
        right_layout.addWidget(self.admin_fields_stack)
        
        ans_layout = QVBoxLayout()
        ans_layout.setSpacing(3)
        lbl_ans = QLabel("Правильный ответ к заданию:")
        lbl_ans.setStyleSheet("font-weight: bold; font-size: 12px; color: #4E5968;")
        self.input_correct_answer = QLineEdit()
        self.input_correct_answer.setPlaceholderText("Например: 1/2 или 25")
        ans_layout.addWidget(lbl_ans)
        ans_layout.addWidget(self.input_correct_answer)
        right_layout.addLayout(ans_layout)
        right_layout.addSpacing(10)
        
        q_btn_layout = QHBoxLayout()
        self.btn_add_q = QPushButton(" Добавить вопрос")
        self.btn_add_q.setObjectName("primary_button")
        self.btn_add_q.setIcon(QIcon(get_asset_path("assets/plus.svg")))
        self.btn_add_q.setIconSize(QSize(14, 14))
        self.btn_add_q.setCursor(Qt.PointingHandCursor)
        self.btn_add_q.clicked.connect(self.add_new_question)
        q_btn_layout.addWidget(self.btn_add_q)
        
        self.btn_cancel_q_edit = QPushButton(" Отмена")
        self.btn_cancel_q_edit.setCursor(Qt.PointingHandCursor)
        self.btn_cancel_q_edit.clicked.connect(self.reset_question_edit_mode)
        self.btn_cancel_q_edit.hide()
        q_btn_layout.addWidget(self.btn_cancel_q_edit)
        
        btn_del_q = QPushButton(" Удалить")
        btn_del_q.setObjectName("danger_button")
        btn_del_q.setIcon(QIcon(get_asset_path("assets/trash.svg")))
        btn_del_q.setIconSize(QSize(14, 14))
        btn_del_q.setCursor(Qt.PointingHandCursor)
        btn_del_q.clicked.connect(self.delete_selected_question)
        q_btn_layout.addWidget(btn_del_q)
        right_layout.addLayout(q_btn_layout)
        
        self.admin_questions_list.itemSelectionChanged.connect(self.on_admin_question_selected)
        
        columns_layout.addWidget(right_col, stretch=3)
        layout.addLayout(columns_layout)
        self.stacked_widget.addWidget(view) # Index 6

    # --- 8. LEADERBOARD VIEW ---
    def create_leaderboard_view(self):
        view = QWidget()
        layout = QVBoxLayout(view)
        
        header_layout = QHBoxLayout()
        title_icon_lbl = QLabel()
        title_icon_lbl.setPixmap(QPixmap(get_asset_path("assets/trophy.svg")).scaled(28, 28, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        header_layout.addWidget(title_icon_lbl)
        
        section_title = QLabel("Таблица лидеров")
        section_title.setObjectName("section_title")
        header_layout.addWidget(section_title)
        header_layout.addStretch()
        
        btn_back = QPushButton(" Назад")
        btn_back.setIcon(QIcon(get_asset_path("assets/back.svg")))
        btn_back.setIconSize(QSize(16, 16))
        btn_back.setCursor(Qt.PointingHandCursor)
        btn_back.clicked.connect(self.show_lobby)
        header_layout.addWidget(btn_back)
        
        layout.addLayout(header_layout)
        layout.addSpacing(15)
        
        topic_select_layout = QHBoxLayout()
        lbl_class_sel = QLabel("Раздел:")
        lbl_class_sel.setStyleSheet("font-weight: bold; font-size: 14px; color: #1C1E21;")
        
        self.leaderboard_class_combo = QComboBox()
        self.leaderboard_class_combo.setCursor(Qt.PointingHandCursor)
        self.leaderboard_class_combo.currentIndexChanged.connect(self.on_leaderboard_class_changed)
        
        lbl_topic_sel = QLabel("Тема:")
        lbl_topic_sel.setStyleSheet("font-weight: bold; font-size: 14px; color: #1C1E21;")
        
        self.leaderboard_topic_combo = QComboBox()
        self.leaderboard_topic_combo.setCursor(Qt.PointingHandCursor)
        self.leaderboard_topic_combo.currentIndexChanged.connect(self.on_leaderboard_topic_changed)
        
        lbl_time_sel = QLabel("Время:")
        lbl_time_sel.setStyleSheet("font-weight: bold; font-size: 14px; color: #1C1E21;")
        
        self.leaderboard_time_combo = QComboBox()
        self.leaderboard_time_combo.setCursor(Qt.PointingHandCursor)
        self.leaderboard_time_combo.addItem("Все результаты", "any")
        self.leaderboard_time_combo.addItem("60 секунд", 60)
        self.leaderboard_time_combo.addItem("180 секунд", 180)
        self.leaderboard_time_combo.addItem("300 секунд", 300)
        self.leaderboard_time_combo.addItem("600 секунд", 600)
        self.leaderboard_time_combo.addItem("900 секунд", 900)
        self.leaderboard_time_combo.currentIndexChanged.connect(self.on_leaderboard_topic_changed)
        
        topic_select_layout.addWidget(lbl_class_sel)
        topic_select_layout.addWidget(self.leaderboard_class_combo, stretch=1)
        topic_select_layout.addSpacing(10)
        topic_select_layout.addWidget(lbl_topic_sel)
        topic_select_layout.addWidget(self.leaderboard_topic_combo, stretch=2)
        topic_select_layout.addSpacing(10)
        topic_select_layout.addWidget(lbl_time_sel)
        topic_select_layout.addWidget(self.leaderboard_time_combo, stretch=1)
        layout.addLayout(topic_select_layout)
        layout.addSpacing(15)
        
        self.leaderboard_table = QTableWidget()
        self.leaderboard_table.setColumnCount(5)
        self.leaderboard_table.setHorizontalHeaderLabels(["Место", "Ученик", "Результат", "Время (сек)", "Дата"])
        
        header = self.leaderboard_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        
        self.leaderboard_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        
        self.leaderboard_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.leaderboard_table.setSelectionMode(QAbstractItemView.NoSelection)
        layout.addWidget(self.leaderboard_table)
        
        layout.addSpacing(15)
        
        self.btn_lobby_leaderboard = QPushButton("Вернуться в Главное Меню")
        self.btn_lobby_leaderboard.setObjectName("primary_button")
        self.btn_lobby_leaderboard.setCursor(Qt.PointingHandCursor)
        self.btn_lobby_leaderboard.clicked.connect(self.show_lobby)
        layout.addWidget(self.btn_lobby_leaderboard)
        
        self.stacked_widget.addWidget(view) # Index 7

    # --- 9. DYNAMIC REWARDS GIF MANAGER VIEW (INDEX 8) ---
    def create_gif_manager_view(self):
        view = QWidget()
        layout = QVBoxLayout(view)
        
        header_layout = QHBoxLayout()
        section_title = QLabel("🖼️ Настройка GIF-анимаций")
        section_title.setObjectName("section_title")
        header_layout.addWidget(section_title)
        header_layout.addStretch()
        
        btn_back = QPushButton(" Назад")
        btn_back.setIcon(QIcon(get_asset_path("assets/back.svg")))
        btn_back.setIconSize(QSize(16, 16))
        btn_back.setCursor(Qt.PointingHandCursor)
        btn_back.clicked.connect(self.on_gif_manager_back_clicked)
        header_layout.addWidget(btn_back)
        layout.addLayout(header_layout)
        layout.addSpacing(15)
        
        columns_layout = QHBoxLayout()
        
        # --- LEFT PANEL (LIST OF ALL GIFs) ---
        left_col = QFrame()
        left_col.setObjectName("card_frame")
        left_layout = QVBoxLayout(left_col)
        left_layout.setContentsMargins(15, 15, 15, 15)
        
        lbl_list = QLabel("Зарегистрированные гифки:")
        lbl_list.setStyleSheet("font-weight: bold; font-size: 13px; color: #4E5968;")
        left_layout.addWidget(lbl_list)
        
        self.gif_manager_list = QListWidget()
        self.gif_manager_list.itemSelectionChanged.connect(self.on_gif_manager_selection_changed)
        left_layout.addWidget(self.gif_manager_list)
        
        btn_bar = QHBoxLayout()
        self.btn_manager_add_gif = QPushButton(" Добавить GIF...")
        self.btn_manager_add_gif.setObjectName("primary_button")
        self.btn_manager_add_gif.setIcon(QIcon(get_asset_path("assets/plus.svg")))
        self.btn_manager_add_gif.setIconSize(QSize(13, 13))
        self.btn_manager_add_gif.setCursor(Qt.PointingHandCursor)
        self.btn_manager_add_gif.clicked.connect(self.on_manager_add_gif_clicked)
        btn_bar.addWidget(self.btn_manager_add_gif, stretch=1)
        
        self.btn_manager_del_gif = QPushButton(" Удалить")
        self.btn_manager_del_gif.setObjectName("danger_button")
        self.btn_manager_del_gif.setIcon(QIcon(get_asset_path("assets/trash.svg")))
        self.btn_manager_del_gif.setIconSize(QSize(13, 13))
        self.btn_manager_del_gif.setCursor(Qt.PointingHandCursor)
        self.btn_manager_del_gif.clicked.connect(self.on_manager_delete_gif_clicked)
        btn_bar.addWidget(self.btn_manager_del_gif)
        left_layout.addLayout(btn_bar)
        
        columns_layout.addWidget(left_col, stretch=2)
        
        # --- RIGHT PANEL (REAL-TIME PREVIEW PLAYER & MULTI-ATTRIBUTES EDITOR) ---
        right_col = QFrame()
        right_col.setObjectName("card_frame")
        right_layout = QVBoxLayout(right_col)
        right_layout.setContentsMargins(15, 15, 15, 15)
        
        lbl_det = QLabel("Параметры и предпросмотр анимации:")
        lbl_det.setStyleSheet("font-weight: bold; font-size: 13px; color: #4E5968;")
        right_layout.addWidget(lbl_det)
        
        # REAL-TIME QMOVIE PLAYER!
        self.gif_manager_preview_label = QLabel("[Выберите GIF из списка]")
        self.gif_manager_preview_label.setAlignment(Qt.AlignCenter)
        self.gif_manager_preview_label.setStyleSheet("background-color: #F8FAFC; border: 1px solid #E4E6EB; border-radius: 8px; padding: 5px;")
        self.gif_manager_preview_label.setFixedHeight(150)
        right_layout.addWidget(self.gif_manager_preview_label)
        
        grid_edit = QVBoxLayout()
        grid_edit.setSpacing(6)
        
        # Filename (read only)
        lbl_f = QLabel("Имя файла:")
        lbl_f.setStyleSheet("font-size: 11px; color: #65676B; font-weight: bold;")
        self.gif_manager_filename_label = QLineEdit()
        self.gif_manager_filename_label.setReadOnly(True)
        grid_edit.addWidget(lbl_f)
        grid_edit.addWidget(self.gif_manager_filename_label)
        
        # Event Combo
        lbl_ev = QLabel("Событие серии (триггер):")
        lbl_ev.setStyleSheet("font-size: 11px; color: #65676B; font-weight: bold;")
        self.gif_manager_event_combo = QComboBox()
        self.gif_manager_event_combo.addItem("5 правильных подряд (score_3)", "score_3")
        self.gif_manager_event_combo.addItem("5 неправильных подряд (unscore_3)", "unscore_3")
        self.gif_manager_event_combo.addItem("10 правильных подряд (score_5)", "score_5")
        self.gif_manager_event_combo.addItem("10 неправильных подряд (unscore_5)", "unscore_5")
        self.gif_manager_event_combo.addItem("15 правильных подряд (score_10)", "score_10")
        self.gif_manager_event_combo.addItem("15 неправильных подряд (unscore_10)", "unscore_10")
        grid_edit.addWidget(lbl_ev)
        grid_edit.addWidget(self.gif_manager_event_combo)
        
        # Gender Combo
        lbl_gen = QLabel("Для какого пола ученика:")
        lbl_gen.setStyleSheet("font-size: 11px; color: #65676B; font-weight: bold;")
        self.gif_manager_gender_combo = QComboBox()
        self.gif_manager_gender_combo.addItem("Для всех полов (all)", "all")
        self.gif_manager_gender_combo.addItem("Для мальчиков 👦 (boys)", "boys")
        self.gif_manager_gender_combo.addItem("Для девочек 👧 (girl)", "girl")
        grid_edit.addWidget(lbl_gen)
        grid_edit.addWidget(self.gif_manager_gender_combo)
        
        # Checkboxes for AGE Multi-attributes!
        lbl_age = QLabel("Допустимые возрастные категории (Классы):")
        lbl_age.setStyleSheet("font-size: 11px; color: #65676B; font-weight: bold;")
        grid_edit.addWidget(lbl_age)
        
        self.chk_old1 = QCheckBox("1-4 классы (old_1)")
        self.chk_old2 = QCheckBox("5-9 классы (old_2)")
        self.chk_old3 = QCheckBox("10-11 классы (old_3)")
        
        chk_lay = QHBoxLayout()
        chk_lay.addWidget(self.chk_old1)
        chk_lay.addWidget(self.chk_old2)
        chk_lay.addWidget(self.chk_old3)
        grid_edit.addLayout(chk_lay)
        
        right_layout.addLayout(grid_edit)
        right_layout.addSpacing(10)
        
        # Save Button
        self.btn_manager_save = QPushButton(" 💾 Сохранить параметры")
        self.btn_manager_save.setObjectName("primary_button")
        self.btn_manager_save.setIcon(QIcon(get_asset_path("assets/plus.svg")))
        self.btn_manager_save.setIconSize(QSize(14, 14))
        self.btn_manager_save.setCursor(Qt.PointingHandCursor)
        self.btn_manager_save.clicked.connect(self.on_manager_save_clicked)
        right_layout.addWidget(self.btn_manager_save)
        
        columns_layout.addWidget(right_col, stretch=3)
        layout.addLayout(columns_layout)
        
        self.stacked_widget.addWidget(view) # Index 8


    # ==========================================
    # NAVIGATION AND REFRESH LOGIC (HIERARCHY)
    # ==========================================
    def show_lobby(self):
        self.stacked_widget.setCurrentIndex(0)

    def show_topic_selection(self):
        """Builds and opens Page 0 (Classes selection area) inside the Topic Selector stack."""
        self.topic_section_title.setText("Выберите класс")
        self.btn_topic_back.setText(" Назад")
        self.btn_start_sprint.hide()
        
        # Clear Class selection page
        for i in reversed(range(self.class_grid_layout.count())): 
            self.class_grid_layout.itemAt(i).widget().setParent(None)
            
        classes = self.db.get_classes()
        scale = self.current_zoom_percent / 100.0
        
        for cid, name in classes:
            # Dynamic Icon Selector - Completely removes unstable emojis!
            icon_path = "assets/book.svg"
            if "10-11" in name: icon_path = "assets/cap.svg"
            elif "9" in name: icon_path = "assets/ruler.svg"
            elif "8" in name: icon_path = "assets/book.svg"
            elif "7" in name: icon_path = "assets/calculator.svg"
            elif "6" in name: icon_path = "assets/pie.svg"
            elif "5" in name: icon_path = "assets/abacus.svg"
            
            btn_class = QPushButton(f"  {name}")
            btn_class.setObjectName("lobby_action_button")
            btn_class.setIcon(QIcon(get_asset_path(icon_path)))
            btn_class.setIconSize(QSize(int(20 * scale), int(20 * scale)))
            btn_class.setCursor(Qt.PointingHandCursor)
            btn_class.setMinimumHeight(int(45 * scale))
            # Hook the class id trigger
            btn_class.clicked.connect(lambda checked, c_id=cid, c_name=name: self.on_class_selected_clicked(c_id, c_name))
            self.class_grid_layout.addWidget(btn_class)
            
        self.topic_selector_stack.setCurrentIndex(0)
        self.stacked_widget.setCurrentIndex(1)

    def on_class_selected_clicked(self, class_id, class_name):
        """Builds and opens Page 1 (Topics selection list) under the selected class."""
        self.selected_class_id = class_id
        self.topic_section_title.setText(f"Раздел: {class_name}")
        self.btn_topic_back.setText(" Назад к классам")
        
        self.topics_list_widget.clear()
        
        # Inject Grade Cumulative Test dynamically!
        self.topics_list_widget.addItem(f"🏆 Итоговый тест за {class_name}")
        
        topics = self.db.get_topics_by_class(class_id)
        for t_id, name in topics:
            self.topics_list_widget.addItem(name)
            
        if self.topics_list_widget.count() > 0:
            self.topics_list_widget.setCurrentRow(0)
            
        self.topic_selector_stack.setCurrentIndex(1)
        self.btn_start_sprint.show()

    def on_topic_selection_back_clicked(self):
        if self.topic_selector_stack.currentIndex() == 1:
            self.show_topic_selection()
        else:
            self.show_lobby()

    def show_history(self):
        self.refresh_history_table()
        self.stacked_widget.setCurrentIndex(4)

    def show_settings(self):
        idx = self.time_combo.findData(self.sprint_total_time)
        if idx >= 0:
            self.time_combo.setCurrentIndex(idx)
        else:
            self.time_combo.setCurrentIndex(0) # fallback to 60s
        self.zoom_spinbox.setValue(self.current_zoom_percent)
        if self.animations_enabled:
            self.animations_combo.setCurrentIndex(0)
        else:
            self.animations_combo.setCurrentIndex(1)
        self.stacked_widget.setCurrentIndex(5)

    def show_leaderboard_screen(self):
        self.leaderboard_class_combo.disconnect() if hasattr(self.leaderboard_class_combo, 'currentIndexChanged') else None
        self.leaderboard_class_combo.clear()
        
        classes = self.db.get_classes()
        for cid, name in classes:
            self.leaderboard_class_combo.addItem(name, cid)
            
        self.leaderboard_class_combo.currentIndexChanged.connect(self.on_leaderboard_class_changed)
        
        if self.leaderboard_class_combo.count() > 0:
            self.leaderboard_class_combo.setCurrentIndex(0)
            self.on_leaderboard_class_changed()
            
        self.stacked_widget.setCurrentIndex(7)

    def on_leaderboard_class_changed(self):
        class_id = self.leaderboard_class_combo.currentData()
        if class_id is None:
            return
            
        class_name = self.leaderboard_class_combo.currentText()
        
        # Temporarily disconnect the topic combo changed signal
        try:
            self.leaderboard_topic_combo.currentIndexChanged.disconnect(self.on_leaderboard_topic_changed)
        except Exception:
            pass
            
        self.leaderboard_topic_combo.clear()
        
        # Add cumulative test as the first option
        self.leaderboard_topic_combo.addItem(f"🏆 Итоговый тест за {class_name}")
        
        # Add topics for this class
        topics = self.db.get_topics_by_class(class_id)
        for t_id, name in topics:
            self.leaderboard_topic_combo.addItem(name)
            
        # Reconnect
        self.leaderboard_topic_combo.currentIndexChanged.connect(self.on_leaderboard_topic_changed)
        
        if self.leaderboard_topic_combo.count() > 0:
            self.leaderboard_topic_combo.setCurrentIndex(0)
            
        self.refresh_leaderboard_table()

    def attempt_admin_access(self):
        # Lazy load dialogs for instant startup!
        from dialogs import AdminLoginDialog
        dialog = AdminLoginDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.show_admin_panel()

    def show_backup_dialog(self):
        # Lazy load backup dialog for instant startup!
        from dialogs import DatabaseBackupDialog
        dialog = DatabaseBackupDialog(self)
        dialog.exec_()

    def trigger_daily_auto_backup(self):
        token = self.db.get_yandex_token()
        if not token:
            return
            
        from datetime import datetime
        today_str = datetime.now().strftime("%Y-%m-%d")
        last_backup = self.db.get_last_auto_backup()
        
        if last_backup == today_str:
            return
            
        from dialogs import YandexDiskWorker
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        remote_name = f"sprint_backup_auto_{timestamp}.db"
        
        self.auto_backup_worker = YandexDiskWorker(token, 'create_backup', self.db.db_path, remote_name)
        
        def on_auto_backup_finished(operation, success, result):
            if success and operation == 'create_backup':
                self.db.update_last_auto_backup(today_str)
                print(f"[AUTO BACKUP] Silent daily backup successful: {result}")
            else:
                print(f"[AUTO BACKUP] Silent daily backup failed: {result}")
                
        self.auto_backup_worker.finished.connect(on_auto_backup_finished)
        self.auto_backup_worker.start()

    def show_admin_panel(self):
        # Refresh Classes combo box inside Admin Panel!
        self.admin_class_combo.clear()
        classes = self.db.get_classes()
        for cid, name in classes:
            self.admin_class_combo.addItem(name, cid)
            
        self.new_topic_input.clear()
        self.input_q_text.clear()
        self.input_q_latex.clear()
        self.input_correct_answer.clear()
        self.admin_selected_image_path = None
        self.admin_image_path_label.clear()
        self.admin_image_thumbnail_label.setText("[Превью фото]")
        self.admin_image_thumbnail_label.setPixmap(QPixmap())
        self.latex_preview_label.setText("[Превью вертикальной дроби]")
        self.latex_preview_label.setPixmap(QPixmap())
        self.stacked_widget.setCurrentIndex(6)

    def show_gif_manager_screen(self):
        self.refresh_gif_manager_list()
        self.stacked_widget.setCurrentIndex(8)

    def on_gif_manager_back_clicked(self):
        # Stop preview player before returning
        if self.manager_preview_movie:
            self.manager_preview_movie.stop()
            self.manager_preview_movie = None
        self.gif_manager_preview_label.clear()
        self.gif_manager_preview_label.setText("[Выберите GIF из списка]")
        self.stacked_widget.setCurrentIndex(5)

    # ==========================================
    # LOGIC: DYNAMIC REWARDS GIF MANAGER
    # ==========================================
    def refresh_gif_manager_list(self):
        self.gif_manager_list.clear()
        self.active_manager_gif_id = None
        self.gif_manager_filename_label.clear()
        
        # Reset checkboxes & combos
        self.gif_manager_event_combo.setCurrentIndex(0)
        self.gif_manager_gender_combo.setCurrentIndex(0)
        self.chk_old1.setChecked(False)
        self.chk_old2.setChecked(False)
        self.chk_old3.setChecked(False)
        
        if self.manager_preview_movie:
            self.manager_preview_movie.stop()
            self.manager_preview_movie = None
        self.gif_manager_preview_label.clear()
        self.gif_manager_preview_label.setText("[Выберите GIF из списка]")
        
        gifs = self.db.get_reward_gifs()
        for g_id, filename, ev_type, gen, o1, o2, o3 in gifs:
            self.gif_manager_list.addItem(filename)

    def on_gif_manager_selection_changed(self):
        selected_item = self.gif_manager_list.currentItem()
        if not selected_item:
            return
            
        filename = selected_item.text()
        
        # Query DB to get attributes of selected GIF
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, event_type, gender, old_1, old_2, old_3 FROM reward_gifs WHERE filename = ?", (filename,))
            row = cursor.fetchone()
            
        if not row:
            return
            
        gif_id, ev_type, gender, o1, o2, o3 = row
        self.active_manager_gif_id = gif_id
        
        # Update display values
        self.gif_manager_filename_label.setText(filename)
        
        # Find index in Event combo
        # Find by user data
        for i in range(self.gif_manager_event_combo.count()):
            if self.gif_manager_event_combo.itemData(i) == ev_type:
                self.gif_manager_event_combo.setCurrentIndex(i)
                break
            
        # Find index in Gender combo
        for i in range(self.gif_manager_gender_combo.count()):
            if self.gif_manager_gender_combo.itemData(i) == gender:
                self.gif_manager_gender_combo.setCurrentIndex(i)
                break
            
        # Set Age category checkboxes
        self.chk_old1.setChecked(o1 == 1)
        self.chk_old2.setChecked(o2 == 1)
        self.chk_old3.setChecked(o3 == 1)
        
        # --- PLAY SELECTED GIF IN PREVIEW PLAYER ---
        if self.manager_preview_movie:
            self.manager_preview_movie.stop()
            
        abs_path = get_asset_path(os.path.join("assets", filename))
        if os.path.exists(abs_path):
            self.manager_preview_movie = QMovie(abs_path)
            # Scale beautifully to fit the container
            scale = self.current_zoom_percent / 100.0
            self.manager_preview_movie.setScaledSize(QSize(int(160 * scale), int(100 * scale)))
            
            self.gif_manager_preview_label.setMovie(self.manager_preview_movie)
            self.manager_preview_movie.start()
        else:
            self.gif_manager_preview_label.setText("⚠️ Файл не найден на диске!")

    def on_manager_save_clicked(self):
        if self.active_manager_gif_id is None:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, сначала выберите GIF из списка на левой панели.")
            return
            
        ev_type = self.gif_manager_event_combo.currentData()
        gender = self.gif_manager_gender_combo.currentData()
        
        o1 = 1 if self.chk_old1.isChecked() else 0
        o2 = 1 if self.chk_old2.isChecked() else 0
        o3 = 1 if self.chk_old3.isChecked() else 0
        
        # Update attributes in DB!
        self.db.update_reward_gif(self.active_manager_gif_id, ev_type, gender, o1, o2, o3)
        QMessageBox.information(self, "Успех", "Параметры гифки успешно сохранены!")
        
        # Refresh lists
        selected_row = self.gif_manager_list.currentRow()
        self.refresh_gif_manager_list()
        self.gif_manager_list.setCurrentRow(selected_row)

    def on_manager_add_gif_clicked(self):
        file_filter = "Анимированные гифки (*.gif)"
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите файл GIF-анимации", "", file_filter)
        
        if file_path:
            orig_filename = os.path.basename(file_path)
            # Clean filename to prevent spaces or weird symbols
            safe_name = "".join([c if c.isalnum() or c in ['.', '_', '-'] else '_' for c in orig_filename])
            
            # Save file inside assets
            assets_dir = get_asset_path("assets")
            os.makedirs(assets_dir, exist_ok=True)
            copied_dest_path = os.path.join(assets_dir, safe_name)
            
            try:
                shutil.copy(file_path, copied_dest_path)
            except Exception as e:
                QMessageBox.critical(self, "Ошибка копирования", f"Не удалось скопировать гифку в проект: {e}")
                return
                
            # Insert into database with default all/all flags
            gif_id, err = self.db.add_reward_gif(safe_name, "score_3", "all", 1, 1, 1)
            if err:
                QMessageBox.warning(self, "Ошибка", err)
                return
                
            QMessageBox.information(
                self, 
                "Успех", 
                f"Гифка '{safe_name}' успешно добавлена в проект!\n"
                "Вы можете настроить её параметры и просмотреть её на панели справа."
            )
            
            self.refresh_gif_manager_list()
            # Select newly added item
            for i in range(self.gif_manager_list.count()):
                if self.gif_manager_list.item(i).text() == safe_name:
                    self.gif_manager_list.setCurrentRow(i)
                    break

    def on_manager_delete_gif_clicked(self):
        selected_item = self.gif_manager_list.currentItem()
        if not selected_item or self.active_manager_gif_id is None:
            QMessageBox.warning(self, "Ошибка", "Выберите GIF-анимацию для удаления.")
            return
            
        filename = selected_item.text()
        reply = QMessageBox.question(
            self, 
            "Удаление гифки", 
            f"Вы действительно хотите полностью стереть гифку '{filename}' из базы данных и файлов проекта?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Delete physical file
            abs_path = get_asset_path(os.path.join("assets", filename))
            if os.path.exists(abs_path):
                try:
                    os.remove(abs_path)
                except Exception as e:
                    print(f"Error removing file {abs_path}: {e}")
                    
            # Delete record
            self.db.delete_reward_gif(self.active_manager_gif_id)
            self.refresh_gif_manager_list()

    # ==========================================
    # LOGIC: RESULTS HOVER POPUPS
    # ==========================================
    def on_result_table_hover(self, row, column):
        """Displays a beautiful floating math/image popup next to the hovered row!"""
        if row >= 0 and row < len(self.sprint_responses_log):
            log = self.sprint_responses_log[row]
            q_text = log.get("orig_question_text", "")
            q_type = log.get("orig_question_type", "text")
            q_image_path = log.get("orig_image_path", None)
            
            # Hide if no valid data
            if not q_text and not q_image_path:
                self.hover_popup.hide()
                return
                
            self.hover_popup.clear()
            self.hover_popup.setMovie(None)
            
            if q_type == 'text':
                self.hover_popup.setText(f"Задание:\n{q_text}")
                self.hover_popup.setStyleSheet("background-color: white; border: 2px solid #2688EB; border-radius: 8px; padding: 12px; font-weight: bold; font-size: 14px;")
            elif q_type == 'latex':
                if q_text in self.latex_cache:
                    pix = self.latex_cache[q_text]
                else:
                    pix = render_latex_to_pixmap(q_text)
                    if pix:
                        self.latex_cache[q_text] = pix
                if pix:
                    self.hover_popup.setPixmap(pix)
                else:
                    self.hover_popup.setText(q_text)
                self.hover_popup.setStyleSheet("background-color: white; border: 2px solid #2688EB; border-radius: 8px; padding: 5px;")
            elif q_type == 'image':
                if q_image_path and os.path.exists(get_user_file_path(q_image_path)):
                    pix = QPixmap(get_user_file_path(q_image_path))
                    scaled = pix.scaled(280, 160, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.hover_popup.setPixmap(scaled)
                    self.hover_popup.setStyleSheet("background-color: white; border: 2px solid #2688EB; border-radius: 8px; padding: 3px;")
                else:
                    self.hover_popup.setText("[Фото-задание]")
                    
            # Position floating popup next to mouse cursor
            self.hover_popup.adjustSize()
            self.hover_popup.move(QCursor.pos() + QPoint(15, 10))
            self.hover_popup.show()
        else:
            self.hover_popup.hide()

    def leaveEvent(self, event):
        """Hide floating hover popup whenever mouse cursor leaves the Main window."""
        self.hover_popup.hide()
        super().leaveEvent(event)

    # ==========================================
    # LOGIC: LEADERBOARD
    # ==========================================
    def on_leaderboard_topic_changed(self):
        self.refresh_leaderboard_table()

    def refresh_leaderboard_table(self):
        self.leaderboard_table.setRowCount(0)
        active_topic = self.leaderboard_topic_combo.currentText()
        if not active_topic:
            return
            
        time_filter = self.leaderboard_time_combo.currentData()
        ranked_records = self.db.get_leaderboard(active_topic, time_filter)
        for index, record in enumerate(ranked_records):
            student, score, spent, date_time = record
            self.leaderboard_table.insertRow(index)
            
            item_rank = QTableWidgetItem()
            if index == 0:
                item_rank.setIcon(QIcon(get_asset_path("assets/medal_1.svg")))
                item_rank.setText(" 1 место")
            elif index == 1:
                item_rank.setIcon(QIcon(get_asset_path("assets/medal_2.svg")))
                item_rank.setText(" 2 место")
            elif index == 2:
                item_rank.setIcon(QIcon(get_asset_path("assets/medal_3.svg")))
                item_rank.setText(" 3 место")
            else:
                item_rank.setText(f"   {index + 1}")
                
            items = [
                item_rank,
                QTableWidgetItem(student),
                QTableWidgetItem(score),
                QTableWidgetItem(str(spent)),
                QTableWidgetItem(date_time)
            ]
            
            for col_idx, item in enumerate(items):
                item.setTextAlignment(Qt.AlignCenter)
                if index < 3:
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
                    if col_idx == 1:
                        item.setForeground(QColor("#2688EB"))
                        
                self.leaderboard_table.setItem(index, col_idx, item)
                
        self.leaderboard_table.resizeRowsToContents()

    # ==========================================
    # LOGIC: START SPRINT (WITH GRADES TEST)
    # ==========================================
    def start_sprint_on_selected_topic(self):
        selected_item = self.topics_list_widget.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Внимание", "Пожалуйста, выберите тему спринта.")
            return
            
        topic_name = selected_item.text()
        
        # Check if they select the Grade Cumulative Test!
        is_cumulative_test = topic_name.startswith("🏆 Итоговый тест")
        
        if is_cumulative_test:
            # Gather questions from all topics in selected Class!
            questions = self.db.get_all_questions_by_class(self.selected_class_id)
        else:
            # Gather questions from specific topic
            topics = self.db.get_topics_by_class(self.selected_class_id)
            topic_id = None
            for t_id, name in topics:
                if name == topic_name:
                    topic_id = t_id
                    break
            if topic_id is None:
                return
            questions = self.db.get_questions(topic_id)
            
        if not questions:
            QMessageBox.warning(
                self, 
                "Пустая тема", 
                "В этой теме пока нет вопросов. Сначала добавьте их в панели администратора."
            )
            return
            
        # Lazy load dialogs for instant startup!
        from dialogs import StudentNameDialog
        name_dialog = StudentNameDialog(self)
        if name_dialog.exec_() != QDialog.Accepted:
            return
            
        self.active_student_name = name_dialog.student_name
        self.active_student_gender = name_dialog.student_gender
        
        # PRO AGE RESOLVER WIN: Determine age category (old_1, old_2, old_3) automatically!
        section_txt = self.topic_section_title.text().lower()
        combined_txt = (topic_name + " " + section_txt).lower()
        
        self.active_age_cat = "old_2" # Default fallback
        if "10-11" in combined_txt:
            self.active_age_cat = "old_3"
        elif any(c in combined_txt for c in ["5", "6", "7", "8", "9"]):
            self.active_age_cat = "old_2"
        elif any(c in combined_txt for c in ["1", "2", "3", "4"]):
            self.active_age_cat = "old_1"
            
        # Start Sprint Setup
        self.selected_topic_name = topic_name
        self.sprint_questions = list(questions)
        random.shuffle(self.sprint_questions)
        
        self.current_question_index = 0
        self.correct_answers_count = 0
        self.questions_answered_total_count = 0
        self.sprint_responses_log = []
        
        self.current_streak = 0
        self.wrong_streak = 0
        
        self.sprint_time_remaining = self.sprint_total_time
        self.sprint_start_time = datetime.now()
        
        self.quiz_topic_label.setText(f"Тема: {self.selected_topic_name} | Ученик: {self.active_student_name}")
        self.update_quiz_question_ui()
        
        self.timer.start(1000)
        self.stacked_widget.setCurrentIndex(2)

    # ==========================================
    # LOGIC: SPRINT QUIZ (INFINITE LOOP & COMBOS)
    # ==========================================
    def update_quiz_question_ui(self):
        current_num = self.questions_answered_total_count + 1
        self.quiz_counter_label.setText(f"Верно: {self.correct_answers_count} | Задание {current_num}")
        mins = self.sprint_time_remaining // 60
        secss = self.sprint_time_remaining % 60
        self.quiz_timer_label.setText(f"Осталось: {mins}:{secss:02d}")
        
        q_id, q_text, q_answer, q_type, q_image_path = self.sprint_questions[self.current_question_index]
        
        self.quiz_question_label.clear()
        self.quiz_math_label.clear()
        self.quiz_image_label.clear()
        
        self.quiz_question_label.hide()
        self.quiz_math_label.hide()
        self.quiz_image_label.hide()
        
        if q_type == 'text':
            self.quiz_question_label.setText(q_text)
            self.quiz_question_label.show()
            
        elif q_type == 'latex':
            if q_text in self.latex_cache:
                pix = self.latex_cache[q_text]
            else:
                pix = render_latex_to_pixmap(q_text)
                if pix:
                    self.latex_cache[q_text] = pix
            
            if pix:
                self.quiz_math_label.setPixmap(pix)
                self.quiz_math_label.show()
            else:
                self.quiz_question_label.setText(q_text)
                self.quiz_question_label.show()
            
        elif q_type == 'image':
            if q_image_path and os.path.exists(get_user_file_path(q_image_path)):
                pix = QPixmap(get_user_file_path(q_image_path))
                scale = self.current_zoom_percent / 100.0
                max_w = int(850 * scale)
                max_h = int(360 * scale)
                scaled_pix = pix.scaled(max_w, max_h, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.quiz_image_label.setPixmap(scaled_pix)
                self.quiz_image_label.show()
            else:
                self.quiz_question_label.setText(f"[Рисунок не найден]: {q_text}")
                self.quiz_question_label.show()
                
        self.quiz_answer_input.clear()
        self.quiz_answer_input.setFocus()

    def on_timer_tick(self):
        self.sprint_time_remaining -= 1
        if self.sprint_time_remaining <= 0:
            self.quiz_timer_label.setText("Осталось: 0:00")
            self.end_sprint(timeout=True)
        else:
            mins = self.sprint_time_remaining // 60
            secss = self.sprint_time_remaining % 60
            self.quiz_timer_label.setText(f"Осталось: {mins}:{secss:02d}")

    def on_submit_answer(self):
        user_ans = self.quiz_answer_input.text().strip()
        q_id, q_text, correct_ans, q_type, q_image_path = self.sprint_questions[self.current_question_index]
        
        is_correct = (user_ans.lower() == correct_ans.strip().lower())
        
        # PRO REWARD ANIMATIONS ALGORITHM WIN!
        if is_correct:
            self.correct_answers_count += 1
            self.current_streak += 1
            self.wrong_streak = 0 # Reset wrong answers streak!
            
            if self.animations_enabled:
                # 1. Flame lights up at 3 correct streak
                if self.current_streak >= 3:
                    self.on_fire_timer_tick()
                    self.fire_timer.start()
                    
                # 2. Dynamic age & gender based GIF selector triggers!
                if self.current_streak == 5:
                    self.play_reward_animation("score_3", "Серия из 5 верных ответов!!!", is_success=True)
                elif self.current_streak == 10:
                    self.play_reward_animation("score_5", "Серия из 10 верных ответов!!!", is_success=True)
                elif self.current_streak == 15:
                    self.play_reward_animation("score_10", "Серия из 15 верных ответов!!!", is_success=True)
        else:
            self.current_streak = 0
            self.wrong_streak += 1
            
            # Reset fire animation immediately
            self.fire_timer.stop()
            scale = self.current_zoom_percent / 100.0
            blank_pix = QPixmap(int(40 * scale), int(40 * scale))
            blank_pix.fill(Qt.transparent)
            self.quiz_fire_label.setPixmap(blank_pix)
            
            if self.animations_enabled:
                # 3. Dynamic unscore mistake streak animations trigger!
                if self.wrong_streak == 5:
                    self.play_reward_animation("unscore_3", "Серия неправильных ответов. Соберись. Ты сможешь!!!", is_success=False)
                elif self.wrong_streak == 10:
                    self.play_reward_animation("unscore_5", "Серия неправильных ответов. Соберись. Ты сможешь!!!", is_success=False)
                else:
                    self.hide_streak_banner()
            else:
                self.hide_streak_banner()
            
        display_question = q_text
        if q_type == 'image':
            display_question = "[Фото-задание]" if not q_text else f"[Фото] {q_text}"
        elif q_type == 'latex':
            display_question = f"[LaTeX] {q_text}"
            
        self.sprint_responses_log.append({
            "question": f"Задание №{self.questions_answered_total_count + 1}", # Clean simple Index instead of Latex Code!
            "your": user_ans if user_ans else "[пропущено]",
            "correct": correct_ans,
            "is_correct": is_correct,
            # Cache original question data inside log for hover popup previews!
            "orig_question_text": q_text,
            "orig_question_type": q_type,
            "orig_image_path": q_image_path
        })
        
        self.questions_answered_total_count += 1
        self.current_question_index += 1
        
        if self.current_question_index >= len(self.sprint_questions):
            random.shuffle(self.sprint_questions)
            self.current_question_index = 0
            
        self.update_quiz_question_ui()

    # ==========================================
    # LOGIC: STREAK ANIMATIONS CONTROLLERS
    # ==========================================
    def on_fire_timer_tick(self):
        self.fire_frame_index = (self.fire_frame_index + 1) % 10
        path = get_asset_path(f"assets/fire_{self.fire_frame_index + 1}.svg")
        scale = self.current_zoom_percent / 100.0
        pix = QPixmap(path).scaled(int(40 * scale), int(40 * scale), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.quiz_fire_label.setPixmap(pix)

    def play_reward_animation(self, event_type, label_message, is_success=True):
        """
        DYNAMIC REWARDS ALGORITHM:
        Queries the database to find a matching GIF, and returns its absolute path.
        If multiple matches exist, picks one randomly!
        """
        # Clear previous movies
        self.quiz_streak_movie_label.setMovie(None)
        
        gif_path = select_reward_gif_file(self.db, self.active_age_cat, self.active_student_gender, event_type)
        scale = self.current_zoom_percent / 100.0
        
        if gif_path and os.path.exists(gif_path):
            movie = QMovie(gif_path)
            movie.setScaledSize(QSize(int(160 * scale), int(100 * scale)))
            
            self.quiz_streak_movie_label.setMovie(movie)
            movie.start()
            self.quiz_streak_movie_label.show()
            
            # Draw encouraging detail text under the movie cleanly!
            color = "#10B981" if is_success else "#E11D48" # Green for win, red for mistake
            font_px = int(14 * scale)
            self.quiz_streak_text_label.setText(label_message)
            self.quiz_streak_text_label.setStyleSheet(f"font-size: {font_px}px; font-weight: 800; color: {color};")
            self.quiz_streak_text_label.show()
        else:
            # Fallback to bold text congrats banner if no matching GIF is found
            font_px = int(18 * scale)
            padding_px = int(10 * scale)
            radius_px = int(8 * scale)
            color = "#10B981" if is_success else "#E11D48"
            
            self.quiz_streak_movie_label.hide()
            self.quiz_streak_text_label.setText(label_message)
            self.quiz_streak_text_label.setStyleSheet(f"""
                font-size: {font_px}px;
                font-weight: 800;
                color: {color};
                background-color: #FFFFFF;
                border: 2px dashed {color};
                border-radius: {radius_px}px;
                padding: {padding_px}px;
            """)
            self.quiz_streak_text_label.show()
            
        self.banner_hide_timer.start(10000) # Auto-hide in 10 seconds!

    def hide_streak_banner(self):
        # Stop movie if running
        movie = self.quiz_streak_movie_label.movie()
        if movie:
            movie.stop()
        self.quiz_streak_movie_label.clear()
        self.quiz_streak_text_label.clear()
        self.quiz_streak_movie_label.hide()
        self.quiz_streak_text_label.hide()


    # ==========================================
    # LOGIC: FINISHING SPRINT
    # ==========================================
    def confirm_quit_sprint(self):
        reply = QMessageBox.question(
            self, "Закончить спринт", "Вы действительно хотите досрочно закончить спринт и сохранить результаты?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.end_sprint(timeout=False)

    def end_sprint(self, timeout=False):
        self.timer.stop()
        
        self.fire_timer.stop()
        self.banner_hide_timer.stop()
        # Set to transparent to maintain perfect layout alignment without shifting widgets!
        scale = self.current_zoom_percent / 100.0
        blank_pix = QPixmap(int(40 * scale), int(40 * scale))
        blank_pix.fill(Qt.transparent)
        self.quiz_fire_label.setPixmap(blank_pix)
        self.hide_streak_banner()
        self.current_streak = 0
        self.wrong_streak = 0
        
        score_val = str(self.correct_answers_count)
        time_spent = self.sprint_total_time - self.sprint_time_remaining
        if time_spent < 0:
            time_spent = self.sprint_total_time
            
        # Save to DB history
        self.db.add_history(self.selected_topic_name, score_val, time_spent, self.active_student_name)
        
        self.result_score_label.setText(score_val)
        self.result_time_label.setText(f"{time_spent} сек")
        
        self.result_table.setRowCount(0)
        for idx, log in enumerate(self.sprint_responses_log):
            self.result_table.insertRow(idx)
            
            q_item = QTableWidgetItem(log["question"])
            u_item = QTableWidgetItem(log["your"])
            c_item = QTableWidgetItem(log["correct"])
            
            q_item.setTextAlignment(Qt.AlignCenter)
            u_item.setTextAlignment(Qt.AlignCenter)
            c_item.setTextAlignment(Qt.AlignCenter)
            
            status_item = QTableWidgetItem()
            status_item.setTextAlignment(Qt.AlignCenter)
            
            if log["is_correct"]:
                status_item.setText("✅ Верно")
                status_item.setForeground(QColor("#2E7D32"))
                u_item.setForeground(QColor("#2E7D32"))
            else:
                status_item.setText("❌ Неверно")
                status_item.setForeground(QColor("#D32F2F"))
                u_item.setForeground(QColor("#D32F2F"))
                
            self.result_table.setItem(idx, 0, q_item)
            self.result_table.setItem(idx, 1, u_item)
            self.result_table.setItem(idx, 2, c_item)
            self.result_table.setItem(idx, 3, status_item)
            
        self.result_table.resizeRowsToContents()
        self.stacked_widget.setCurrentIndex(3)

    # ==========================================
    # LOGIC: HISTORY
    # ==========================================
    def refresh_history_table(self):
        self.history_table.setRowCount(0)
        records = self.db.get_history()
        for idx, r in enumerate(records):
            topic_name, score, time_spent, date_time, student_name = r
            self.history_table.insertRow(idx)
            
            items = [
                QTableWidgetItem(date_time),
                QTableWidgetItem(student_name),
                QTableWidgetItem(topic_name),
                QTableWidgetItem(score),
                QTableWidgetItem(str(time_spent))
            ]
            for i, item in enumerate(items):
                item.setTextAlignment(Qt.AlignCenter)
                self.history_table.setItem(idx, i, item)
                
        self.history_table.resizeRowsToContents()

    def clear_history_data(self):
        from dialogs import AdminLoginDialog
        reply = QMessageBox.question(
            self, "Очистить историю", "Вы действительно хотите полностью стереть историю результатов?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            dialog = AdminLoginDialog(self)
            dialog.setWindowTitle("Подтверждение удаления")
            if dialog.exec_() == QDialog.Accepted:
                self.db.clear_history()
                self.refresh_history_table()
                QMessageBox.information(self, "Успешно", "История результатов была полностью очищена.")

    # ==========================================
    # LOGIC: SETTINGS & DYNAMIC SAVES
    # ==========================================
    def on_zoom_spinbox_changed(self, value):
        self.current_zoom_percent = value
        self.apply_zoom_scale(self.current_zoom_percent)

    def save_settings_data(self):
        new_time = self.time_combo.currentData()
        new_zoom = self.zoom_spinbox.value()
        animations_enabled = 1 if self.animations_combo.currentIndex() == 0 else 0
        
        self.sprint_total_time = new_time
        self.current_zoom_percent = new_zoom
        self.animations_enabled = (animations_enabled == 1)
        
        self.db.update_settings(new_time, new_zoom, animations_enabled)
        self.apply_zoom_scale(new_zoom)
        
        QMessageBox.information(
            self, 
            "Успех", 
            f"Настройки успешно сохранены!\nВремя: {new_time} сек.\nМасштаб: {new_zoom}%.\nАнимации: {'Включены' if self.animations_enabled else 'Выключены'}."
        )
        self.show_lobby()

    # ==========================================
    # LOGIC: ADMIN PANEL (CLASSES & TOPICS)
    # ==========================================
    def on_admin_class_changed(self):
        selected_idx = self.admin_class_combo.currentIndex()
        if selected_idx < 0:
            self.admin_topics_list.clear()
            return
            
        class_id = self.admin_class_combo.currentData()
        self.refresh_admin_topics_by_class(class_id)

    def refresh_admin_topics_by_class(self, class_id):
        self.admin_topics_list.clear()
        self.admin_questions_list.clear()
        self.admin_questions_title.setText("Questions")
        self.input_q_text.clear()
        self.input_q_latex.clear()
        self.input_correct_answer.clear()
        
        topics = self.db.get_topics_by_class(class_id)
        for t_id, name in topics:
            self.admin_topics_list.addItem(name)
            
        if self.admin_topics_list.count() > 0:
            self.admin_topics_list.setCurrentRow(0)

    def refresh_admin_topics(self):
        self.admin_class_combo.blockSignals(True)
        self.admin_class_combo.clear()
        
        classes = self.db.get_classes()
        for cid, name in classes:
            self.admin_class_combo.addItem(name, cid)
            
        self.admin_class_combo.blockSignals(False)
        
        if self.admin_class_combo.count() > 0:
            self.admin_class_combo.setCurrentIndex(0)
            self.on_admin_class_changed()

    def on_admin_topic_selected(self):
        selected_item = self.admin_topics_list.currentItem()
        if not selected_item:
            self.admin_questions_list.clear()
            self.admin_questions_title.setText("Questions")
            return
            
        topic_name = selected_item.text()
        self.admin_questions_title.setText(f"Вопросы в теме: {topic_name}")
        self.refresh_admin_questions(topic_name)

    def refresh_admin_questions(self, topic_name):
        self.admin_questions_list.clear()
        
        topics = self.db.get_topics_by_class(self.admin_class_combo.currentData())
        topic_id = None
        for t_id, name in topics:
            if name == topic_name:
                topic_id = t_id
                break
        if topic_id is None:
            return
            
        questions = self.db.get_questions(topic_id)
        self.admin_active_topic_id = topic_id
        self.admin_current_questions = questions
        
        for q_id, text, answer, q_type, q_image_path in questions:
            type_symbol = "📝"
            if q_type == 'latex':
                type_symbol = "🧮 LaTeX:"
            elif q_type == 'image':
                type_symbol = "🖼️ Фото:"
                
            display_text = f"{type_symbol} {text} | Ответ: {answer}"
            self.admin_questions_list.addItem(display_text)

    # Class Management
    def add_new_class(self):
        name, ok = QInputDialog.getText(self, "Создать класс/раздел", "Введите название нового класса (например, 7 класс):")
        if ok and name.strip():
            cid, err = self.db.add_class(name.strip())
            if err:
                QMessageBox.warning(self, "Ошибка", err)
                return
            self.refresh_admin_topics()
            for i in range(self.admin_class_combo.count()):
                if self.admin_class_combo.itemText(i) == name.strip():
                    self.admin_class_combo.setCurrentIndex(i)
                    break

    def delete_selected_class(self):
        selected_idx = self.admin_class_combo.currentIndex()
        if selected_idx < 0:
            return
            
        class_name = self.admin_class_combo.currentText()
        class_id = self.admin_class_combo.currentData()
        
        reply = QMessageBox.question(
            self, "Удалить класс", f"Вы уверены, что хотите полностью стереть класс '{class_name}' и ВСЕ его темы и вопросы?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.db.delete_class(class_id)
            self.refresh_admin_topics()

    def move_class_up(self):
        idx = self.admin_class_combo.currentIndex()
        if idx <= 0 or idx >= self.admin_class_combo.count():
            return
        class_id = self.admin_class_combo.itemData(idx)
        prev_class_id = self.admin_class_combo.itemData(idx - 1)
        self.db.swap_class_order(class_id, prev_class_id)
        self.refresh_admin_topics()
        self.admin_class_combo.setCurrentIndex(idx - 1)

    def move_class_down(self):
        idx = self.admin_class_combo.currentIndex()
        if idx < 0 or idx >= self.admin_class_combo.count() - 1:
            return
        class_id = self.admin_class_combo.itemData(idx)
        next_class_id = self.admin_class_combo.itemData(idx + 1)
        self.db.swap_class_order(class_id, next_class_id)
        self.refresh_admin_topics()
        self.admin_class_combo.setCurrentIndex(idx + 1)

    # Topic Management
    def add_new_topic(self):
        class_idx = self.admin_class_combo.currentIndex()
        if class_idx < 0:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, сначала выберите класс.")
            return
            
        class_id = self.admin_class_combo.currentData()
        name = self.new_topic_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Ошибка", "Название темы не может быть пустым.")
            return
            
        topic_id, err = self.db.add_topic(name, class_id)
        if err:
            QMessageBox.warning(self, "Ошибка", err)
            return
            
        self.new_topic_input.clear()
        self.refresh_admin_topics_by_class(class_id)
        
        for i in range(self.admin_topics_list.count()):
            if self.admin_topics_list.item(i).text() == name:
                self.admin_topics_list.setCurrentRow(i)
                break

    def delete_selected_topic(self):
        selected_item = self.admin_topics_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Ошибка", "Выберите тему для удаления.")
            return
            
        topic_name = selected_item.text()
        reply = QMessageBox.question(
            self, "Удаление темы", f"Вы уверены, что хотите полностью стереть тему '{topic_name}' и ВСЕ её вопросы?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            class_id = self.admin_class_combo.currentData()
            topics = self.db.get_topics_by_class(class_id)
            topic_id = None
            for t_id, name in topics:
                if name == topic_name:
                    topic_id = t_id
                    break
            if topic_id is not None:
                self.db.delete_topic(topic_id)
                self.refresh_admin_topics_by_class(class_id)

    def move_topic_up(self):
        row = self.admin_topics_list.currentRow()
        if row <= 0 or row >= self.admin_topics_list.count():
            return
        class_id = self.admin_class_combo.currentData()
        topics = self.db.get_topics_by_class(class_id)
        topic_id = topics[row][0]
        prev_topic_id = topics[row - 1][0]
        self.db.swap_topic_order(topic_id, prev_topic_id)
        self.refresh_admin_topics_by_class(class_id)
        self.admin_topics_list.setCurrentRow(row - 1)

    def move_topic_down(self):
        row = self.admin_topics_list.currentRow()
        if row < 0 or row >= self.admin_topics_list.count() - 1:
            return
        class_id = self.admin_class_combo.currentData()
        topics = self.db.get_topics_by_class(class_id)
        topic_id = topics[row][0]
        next_topic_id = topics[row + 1][0]
        self.db.swap_topic_order(topic_id, next_topic_id)
        self.refresh_admin_topics_by_class(class_id)
        self.admin_topics_list.setCurrentRow(row + 1)

    def rename_selected_class(self):
        selected_idx = self.admin_class_combo.currentIndex()
        if selected_idx < 0:
            return
        class_name = self.admin_class_combo.currentText()
        class_id = self.admin_class_combo.currentData()
        
        new_name, ok = QInputDialog.getText(self, "Переименовать раздел", "Введите новое название раздела:", QLineEdit.Normal, class_name)
        if ok and new_name.strip() and new_name.strip() != class_name:
            success, err = self.db.rename_class(class_id, new_name.strip())
            if not success:
                QMessageBox.warning(self, "Ошибка", err)
                return
            self.refresh_admin_topics()
            for i in range(self.admin_class_combo.count()):
                if self.admin_class_combo.itemText(i) == new_name.strip():
                    self.admin_class_combo.setCurrentIndex(i)
                    break

    def rename_selected_topic(self):
        selected_item = self.admin_topics_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Ошибка", "Выберите тему для переименования.")
            return
        topic_name = selected_item.text()
        class_id = self.admin_class_combo.currentData()
        
        topics = self.db.get_topics_by_class(class_id)
        topic_id = None
        for t_id, name in topics:
            if name == topic_name:
                topic_id = t_id
                break
                
        if topic_id is None:
            return
            
        new_name, ok = QInputDialog.getText(self, "Переименовать тему", "Введите новое название темы:", QLineEdit.Normal, topic_name)
        if ok and new_name.strip() and new_name.strip() != topic_name:
            success, err = self.db.rename_topic(topic_id, new_name.strip())
            if not success:
                QMessageBox.warning(self, "Ошибка", err)
                return
            self.refresh_admin_topics_by_class(class_id)
            for i in range(self.admin_topics_list.count()):
                if self.admin_topics_list.item(i).text() == new_name.strip():
                    self.admin_topics_list.setCurrentRow(i)
                    break

    def on_admin_question_selected(self):
        if not hasattr(self, 'admin_current_questions') or not self.admin_current_questions:
            return
            
        row = self.admin_questions_list.currentRow()
        if row < 0 or row >= len(self.admin_current_questions):
            self.admin_selected_question_id = None
            self.btn_add_q.setText(" Добавить вопрос")
            self.btn_cancel_q_edit.hide()
            return
            
        q_data = self.admin_current_questions[row]
        q_id, question_text, correct_answer, q_type, image_path = q_data
        
        self.admin_selected_question_id = q_id
        self.btn_add_q.setText(" Сохранить изменения")
        self.btn_cancel_q_edit.show()
        
        self.q_type_combo.blockSignals(True)
        self.input_correct_answer.setText(correct_answer)
        
        if q_type == 'text':
            self.q_type_combo.setCurrentIndex(0)
            self.admin_fields_stack.setCurrentIndex(0)
            self.input_q_text.setText(question_text)
        elif q_type == 'latex':
            self.q_type_combo.setCurrentIndex(1)
            self.admin_fields_stack.setCurrentIndex(1)
            self.input_q_latex.setText(question_text)
            self.on_preview_latex_clicked()
        elif q_type == 'image':
            self.q_type_combo.setCurrentIndex(2)
            self.admin_fields_stack.setCurrentIndex(2)
            self.admin_selected_image_path = image_path
            self.admin_image_path_label.setText(image_path if image_path else "Файл не выбран")
            
            if image_path:
                abs_path = get_user_file_path(image_path)
                if os.path.exists(abs_path):
                    pix = QPixmap(abs_path)
                    scaled = pix.scaled(150, 90, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.admin_image_thumbnail_label.setPixmap(scaled)
                else:
                    self.admin_image_thumbnail_label.setText("[Фото не найдено]")
                    self.admin_image_thumbnail_label.setPixmap(QPixmap())
            else:
                self.admin_image_thumbnail_label.setText("[Превью фото]")
                self.admin_image_thumbnail_label.setPixmap(QPixmap())
                
        self.q_type_combo.blockSignals(False)

    def reset_question_edit_mode(self):
        self.admin_selected_question_id = None
        self.admin_questions_list.clearSelection()
        self.btn_add_q.setText(" Добавить вопрос")
        self.btn_cancel_q_edit.hide()
        
        self.input_q_text.clear()
        self.input_q_latex.clear()
        self.input_correct_answer.clear()
        self.admin_selected_image_path = None
        self.admin_image_path_label.clear()
        self.admin_image_thumbnail_label.setText("[Превью фото]")
        self.admin_image_thumbnail_label.setPixmap(QPixmap())
        self.latex_preview_label.setText("[Превью вертикальной дроби]")
        self.latex_preview_label.setPixmap(QPixmap())

    # Questions Management
    def on_question_type_changed(self, index):
        self.admin_fields_stack.setCurrentIndex(index)

    def on_preview_latex_clicked(self):
        formula = self.input_q_latex.text().strip()
        if not formula:
            QMessageBox.warning(self, "Внимание", "Пожалуйста, введите формулу LaTeX для предпросмотра.")
            return
            
        pix = render_latex_to_pixmap(formula)
        if pix:
            self.latex_preview_label.setPixmap(pix)
        else:
            self.latex_preview_label.setText("❌ Ошибка в формуле LaTeX!")

    def on_choose_image_clicked(self):
        file_filter = "Изображения (*.png *.jpg *.jpeg *.bmp *.gif)"
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите картинку задачи", "", file_filter)
        
        if file_path:
            self.admin_selected_image_path = file_path
            self.admin_image_path_label.setText(os.path.basename(file_path))
            
            pix = QPixmap(file_path)
            scaled = pix.scaled(150, 90, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.admin_image_thumbnail_label.setPixmap(scaled)
            
            reply = QMessageBox.question(
                self, 
                "Распознать формулу?", 
                "Считать текст формулы и перевести в LaTeX код автоматически?",
                QMessageBox.Yes | QMessageBox.No, 
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                QApplication.setOverrideCursor(Qt.WaitCursor)
                latex_text = image_to_latex_ocr(file_path)
                QApplication.restoreOverrideCursor()
                
                if latex_text:
                    self.q_type_combo.setCurrentIndex(1)
                    self.input_q_latex.setText(latex_text)
                    self.on_preview_latex_clicked()
                    QMessageBox.information(self, "Успех", "Формула успешно распознана в LaTeX код!")
                else:
                    QMessageBox.warning(
                        self, 
                        "OCR Ошибка", 
                        "Не удалось распознать формулу. Пожалуйста, введите код вручную или используйте изображение напрямую."
                    )

    def add_new_question(self):
        selected_item = self.admin_topics_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, сначала выберите тему в левой колонке.")
            return
            
        topic_name = selected_item.text()
        correct_ans = self.input_correct_answer.text().strip()
        
        if not correct_ans:
            QMessageBox.warning(self, "Ошибка", "Поле правильного ответа не может быть пустым.")
            return
            
        selected_type_index = self.q_type_combo.currentIndex()
        
        q_text = ""
        q_type = 'text'
        copied_image_path = None
        
        if selected_type_index == 0:
            q_text = self.input_q_text.text().strip()
            q_type = 'text'
            if not q_text:
                QMessageBox.warning(self, "Ошибка", "Пожалуйста, введите текст вопроса.")
                return
                
        elif selected_type_index == 1:
            q_text = self.input_q_latex.text().strip()
            q_type = 'latex'
            if not q_text:
                QMessageBox.warning(self, "Ошибка", "Пожалуйста, введите формулу LaTeX.")
                return
                
        elif selected_type_index == 2:
            q_type = 'image'
            if not self.admin_selected_image_path:
                QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите файл изображения с компьютера.")
                return
                
            if self.admin_selected_image_path.startswith("sprint_images"):
                copied_image_path = self.admin_selected_image_path
                q_text = f"Рисунок: {os.path.basename(copied_image_path)}"
            else:
                os.makedirs(get_user_file_path("sprint_images"), exist_ok=True)
                orig_filename = os.path.basename(self.admin_selected_image_path)
                unique_filename = f"task_{int(time.time())}_{orig_filename}"
                copied_image_path = os.path.join("sprint_images", unique_filename)
                
                try:
                    shutil.copy(self.admin_selected_image_path, get_user_file_path(copied_image_path))
                    q_text = f"Рисунок: {orig_filename}"
                except Exception as e:
                    QMessageBox.critical(self, "Ошибка копирования", f"Не удалось сохранить фото: {e}")
                    return
                    
        class_id = self.admin_class_combo.currentData()
        topics = self.db.get_topics_by_class(class_id)
        topic_id = None
        for t_id, name in topics:
            if name == topic_name:
                topic_id = t_id
                break
                
        if topic_id is None:
            return
            
        if hasattr(self, 'admin_selected_question_id') and self.admin_selected_question_id is not None:
            # EDIT MODE
            self.db.update_question(self.admin_selected_question_id, topic_id, q_text, correct_ans, q_type, copied_image_path)
            QMessageBox.information(self, "Успешно", "Задание успешно обновлено!")
            self.reset_question_edit_mode()
        else:
            # ADD MODE
            self.db.add_question(topic_id, q_text, correct_ans, q_type, copied_image_path)
            QMessageBox.information(self, "Успешно", "Новое задание успешно добавлено!")
            self.reset_question_edit_mode()
            
        self.refresh_admin_questions(topic_name)
        
        if q_type == 'text':
            self.input_q_text.setFocus()
        elif q_type == 'latex':
            self.input_q_latex.setFocus()

    def delete_selected_question(self):
        selected_topic = self.admin_topics_list.currentItem()
        selected_q_item = self.admin_questions_list.currentItem()
        
        if not selected_topic or not selected_q_item:
            QMessageBox.warning(self, "Ошибка", "Выберите вопрос для удаления.")
            return
            
        topic_name = selected_topic.text()
        q_row = self.admin_questions_list.currentRow()
        
        class_id = self.admin_class_combo.currentData()
        topics = self.db.get_topics_by_class(class_id)
        topic_id = None
        for t_id, name in topics:
            if name == topic_name:
                topic_id = t_id
                break
                
        if topic_id is None:
            return
            
        questions = self.db.get_questions(topic_id)
        if q_row < 0 or q_row >= len(questions):
            return
            
        q_id = questions[q_row][0]
        q_image_path = questions[q_row][4]
        
        reply = QMessageBox.question(
            self, "Удаление вопроса", "Удалить выбранное задание?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            if q_image_path and os.path.exists(q_image_path):
                try:
                    os.remove(q_image_path)
                except Exception as e:
                    print(f"Error removing file {q_image_path}: {e}")
                    
            self.db.delete_question(q_id)
            self.refresh_admin_questions(topic_name)


# ==========================================
# REWARD GIF ROUTER ALGORITHM
# ==========================================
def select_reward_gif_file(db_manager, age_cat, gender, event_type):
    """
    DYNAMIC REWARDS MAPPING ENGINE:
    Queries the SQLite database to find a matching GIF file path,
    and if multiple matches exist, chooses one randomly!
    """
    import os
    import random
    
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        
        # Determine the target age category column dynamically!
        age_col = "old_1"
        if age_cat == "old_2": age_col = "old_2"
        elif age_cat == "old_3": age_col = "old_3"
        
        # Build strict matching query:
        # 1. Event type matches (e.g. score_3, unscore_3, etc.)
        # 2. Gender is either 'all' or matches the student's gender
        # 3. Target age column value is 1 (Active)
        query = f"""
            SELECT filename FROM reward_gifs 
            WHERE event_type = ? 
              AND (gender = 'all' OR gender = ?) 
              AND {age_col} = 1
        """
        cursor.execute(query, (event_type, gender))
        rows = cursor.fetchall()
        
    if rows:
        chosen_filename = random.choice(rows)[0]
        abs_path = get_asset_path(os.path.join("assets", chosen_filename))
        print(f"AI Reward Router: Chosen {chosen_filename} for {age_cat}, {gender}, {event_type}")
        return abs_path
        
    return None


# ==========================================
# MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SprintApp()
    window.show()
    sys.exit(app.exec_())
