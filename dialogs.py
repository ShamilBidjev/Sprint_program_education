import os
import sys
import time
import shutil
import sqlite3
try:
    import requests
except ImportError:
    requests = None
from datetime import datetime

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, 
    QComboBox, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, 
    QStackedWidget, QWidget, QFrame, QAbstractItemView, QProgressDialog,
    QApplication
)
from PyQt5.QtCore import Qt, QSize, QTimer, QThread, pyqtSignal, QUrl
from PyQt5.QtGui import QIcon, QPixmap, QDesktopServices

from assets_manager import get_asset_path, get_user_file_path

# ==========================================
# CUSTOM MODAL DIALOGS (VK STYLE)
# ==========================================
class AdminLoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Доступ администратора")
        self.resize(350, 180)
        self.setModal(True)
        self.setStyleSheet(parent.styleSheet() if parent else "")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        lbl_title = QLabel("Введите код доступа:")
        lbl_title.setStyleSheet("font-weight: bold; font-size: 15px; color: #1C1E21;")
        layout.addWidget(lbl_title)
        
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("Введите пин-код...")
        self.code_input.setEchoMode(QLineEdit.Password)
        self.code_input.setMaxLength(10)
        self.code_input.setAlignment(Qt.AlignCenter)
        self.code_input.setStyleSheet("font-size: 18px; font-weight: bold; tracking: 4px; padding: 10px;")
        self.code_input.returnPressed.connect(self.on_submit)
        layout.addWidget(self.code_input)
        
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #E11D48; font-size: 12px; font-weight: 600;")
        self.error_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.error_label)
        
        btn_layout = QHBoxLayout()
        self.btn_ok = QPushButton(" Войти")
        self.btn_ok.setObjectName("primary_button")
        self.btn_ok.setIcon(QIcon(get_asset_path("assets/gear.svg")))
        self.btn_ok.setIconSize(QSize(14, 14))
        self.btn_ok.setCursor(Qt.PointingHandCursor)
        self.btn_ok.clicked.connect(self.on_submit)
        
        self.btn_cancel = QPushButton("Отмена")
        self.btn_cancel.setCursor(Qt.PointingHandCursor)
        self.btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_ok)
        layout.addLayout(btn_layout)
        
        self.code_input.setFocus()

    def on_submit(self):
        entered_pin = self.code_input.text().strip()
        if entered_pin == "0000":
            self.accept()
        else:
            self.error_label.setText("❌ Неверный код доступа (попробуйте 0000)")
            self.code_input.clear()
            self.code_input.setFocus()


class StudentNameDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Регистрация на Спринт")
        self.resize(380, 240) # Increased height to accommodate Gender Selection!
        self.setModal(True)
        self.setStyleSheet(parent.styleSheet() if parent else "")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        # 1. Student Name Input
        lbl_title = QLabel("Укажите ваше имя:")
        lbl_title.setStyleSheet("font-weight: bold; font-size: 14px; color: #1C1E21;")
        layout.addWidget(lbl_title)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Например: Иван Смирнов...")
        self.name_input.setStyleSheet("font-size: 14px; padding: 8px;")
        self.name_input.returnPressed.connect(self.on_submit)
        layout.addWidget(self.name_input)
        
        # 2. Gender Selection Combo Box
        lbl_gender = QLabel("Укажите ваш пол:")
        lbl_gender.setStyleSheet("font-weight: bold; font-size: 14px; color: #1C1E21;")
        layout.addWidget(lbl_gender)
        
        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["Мальчик 👦", "Девочка 👧"])
        self.gender_combo.setStyleSheet("font-size: 14px; padding: 6px;")
        layout.addWidget(self.gender_combo)
        
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #E11D48; font-size: 12px; font-weight: 600;")
        self.error_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.error_label)
        
        btn_layout = QHBoxLayout()
        self.btn_start = QPushButton(" Поехали!")
        self.btn_start.setObjectName("primary_button")
        self.btn_start.setIcon(QIcon(get_asset_path("assets/rocket.svg")))
        self.btn_start.setIconSize(QSize(15, 15))
        self.btn_start.setCursor(Qt.PointingHandCursor)
        self.btn_start.clicked.connect(self.on_submit)
        
        self.btn_cancel = QPushButton("Отмена")
        self.btn_cancel.setCursor(Qt.PointingHandCursor)
        self.btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_start)
        layout.addLayout(btn_layout)
        
        self.name_input.setFocus()
        self.student_name = ""
        self.student_gender = "boys"

    def on_submit(self):
        val = self.name_input.text().strip()
        if len(val) >= 2:
            self.student_name = val
            self.student_gender = "boys" if self.gender_combo.currentIndex() == 0 else "girl"
            self.accept()
        else:
            self.error_label.setText("❌ Имя должно содержать хотя бы 2 буквы")


# ==========================================
# ASYNCHRONOUS YANDEX DISK BACKUP WORKERS
# ==========================================
class YandexDiskWorker(QThread):
    finished = pyqtSignal(str, bool, object)

    def __init__(self, token, operation, *args, **kwargs):
        super().__init__()
        self.token = token
        self.operation = operation  # 'check_auth', 'list_backups', 'create_backup', 'restore_backup', 'delete_backup'
        self.args = args
        self.kwargs = kwargs

    def run(self):
        if requests is None:
            self.finished.emit(self.operation, False, "Библиотека requests не установлена.")
            return

        headers = {
            'Authorization': f'OAuth {self.token}',
            'Accept': 'application/json'
        }
        base_url = 'https://cloud-api.yandex.net/v1/disk'

        try:
            if self.operation == 'check_auth':
                # Check if token is valid and get disk space
                resp = requests.get(base_url, headers=headers, timeout=10)
                if resp.status_code == 200:
                    data = resp.json()
                    total = data.get('total_space', 0)
                    used = data.get('used_space', 0)
                    free = total - used
                    self.finished.emit('check_auth', True, {'total': total, 'used': used, 'free': free})
                else:
                    self.finished.emit('check_auth', False, f"Ошибка {resp.status_code}: Недействительный токен")

            elif self.operation == 'list_backups':
                # First ensure folder exists
                path = '/Sprint Backup'
                resp = requests.get(f"{base_url}/resources?path={path}", headers=headers, timeout=10)
                if resp.status_code == 404:
                    # Create the folder
                    create_resp = requests.put(f"{base_url}/resources?path={path}", headers=headers, timeout=10)
                    if create_resp.status_code != 201:
                        self.finished.emit('list_backups', False, f"Не удалось создать папку для бэкапов: {create_resp.text}")
                        return
                    items = []
                elif resp.status_code == 200:
                    data = resp.json()
                    items = data.get('_embedded', {}).get('items', [])
                else:
                    self.finished.emit('list_backups', False, f"Ошибка получения списка: {resp.text}")
                    return

                # Filter and parse backup files
                backups = []
                for item in items:
                    if item.get('type') == 'file' and item.get('name', '').startswith('sprint_backup_') and item.get('name', '').endswith('.db'):
                        backups.append({
                            'name': item.get('name'),
                            'path': item.get('path'),
                            'size': item.get('size', 0),
                            'created': item.get('created', '')
                        })
                # Sort descending by name (chronological)
                backups.sort(key=lambda x: x['name'], reverse=True)
                self.finished.emit('list_backups', True, backups)

            elif self.operation == 'create_backup':
                local_db_path = self.args[0]
                remote_name = self.args[1]
                temp_backup_path = "sprint_backup_temp.db"

                # 1. Vacuum DB to temporary file
                if os.path.exists(temp_backup_path):
                    try:
                        os.remove(temp_backup_path)
                    except Exception:
                        pass

                conn = sqlite3.connect(local_db_path)
                try:
                    conn.execute(f'VACUUM INTO "{temp_backup_path}"')
                finally:
                    conn.close()

                if not os.path.exists(temp_backup_path):
                    self.finished.emit('create_backup', False, "Не удалось создать локальную копию базы данных")
                    return

                # Ensure main folder and subfolders exist on Yandex.Disk
                for folder in ['/Sprint Backup', '/Sprint Backup/sprint_images', '/Sprint Backup/results', '/Sprint Backup/assignments']:
                    r = requests.get(f"{base_url}/resources?path={folder}", headers=headers, timeout=10)
                    if r.status_code == 404:
                        requests.put(f"{base_url}/resources?path={folder}", headers=headers, timeout=10)

                # 2. Upload timestamped backup
                remote_path = f"/Sprint Backup/{remote_name}"
                upload_url_endpoint = f"{base_url}/resources/upload?path={remote_path}&overwrite=true"
                resp = requests.get(upload_url_endpoint, headers=headers, timeout=10)
                if resp.status_code == 200:
                    upload_url = resp.json().get('href')
                    with open(temp_backup_path, 'rb') as f:
                        requests.put(upload_url, data=f, timeout=45)

                # 3. Upload active database for Mobile Sync
                active_remote_path = "/Sprint Backup/sprint_backup_active.db"
                upload_url_active = f"{base_url}/resources/upload?path={active_remote_path}&overwrite=true"
                resp_active = requests.get(upload_url_active, headers=headers, timeout=10)
                if resp_active.status_code == 200:
                    upload_url = resp_active.json().get('href')
                    with open(temp_backup_path, 'rb') as f:
                        requests.put(upload_url, data=f, timeout=45)

                # Clean up local temporary file
                if os.path.exists(temp_backup_path):
                    try:
                        os.remove(temp_backup_path)
                    except Exception:
                        pass

                # 4. Sync all local task images to Yandex.Disk
                local_images_dir = get_user_file_path("sprint_images")
                if os.path.exists(local_images_dir):
                    r_files = requests.get(f"{base_url}/resources?path=/Sprint Backup/sprint_images&limit=1000", headers=headers, timeout=10)
                    cloud_files = []
                    if r_files.status_code == 200:
                        items = r_files.json().get('_embedded', {}).get('items', [])
                        cloud_files = [item.get('name') for item in items]

                    for img_name in os.listdir(local_images_dir):
                        if img_name not in cloud_files:
                            local_img_path = os.path.join(local_images_dir, img_name)
                            remote_img_path = f"/Sprint Backup/sprint_images/{img_name}"
                            r_url = requests.get(f"{base_url}/resources/upload?path={remote_img_path}&overwrite=true", headers=headers, timeout=10)
                            if r_url.status_code == 200:
                                up_url = r_url.json().get('href')
                                with open(local_img_path, 'rb') as f:
                                    requests.put(up_url, data=f, timeout=30)

                self.finished.emit('create_backup', True, remote_name)

            elif self.operation == 'restore_backup':
                remote_name = self.args[0]
                temp_restore_path = "sprint_restore_temp.db"

                # 1. Get download URL from Yandex.Disk
                remote_path = f"/Sprint Backup/{remote_name}"
                download_url_endpoint = f"{base_url}/resources/download?path={remote_path}"
                resp = requests.get(download_url_endpoint, headers=headers, timeout=10)
                if resp.status_code != 200:
                    self.finished.emit('restore_backup', False, f"Не удалось получить URL для скачивания: {resp.text}")
                    return

                download_url = resp.json().get('href')

                # 2. Download file content
                get_resp = requests.get(download_url, stream=True, timeout=45)
                if get_resp.status_code == 200:
                    with open(temp_restore_path, 'wb') as f:
                        for chunk in get_resp.iter_content(chunk_size=8192):
                            f.write(chunk)
                    self.finished.emit('restore_backup', True, temp_restore_path)
                else:
                    self.finished.emit('restore_backup', False, f"Ошибка скачивания: {get_resp.status_code}")

            elif self.operation == 'delete_backup':
                remote_name = self.args[0]
                remote_path = f"/Sprint Backup/{remote_name}"
                delete_endpoint = f"{base_url}/resources?path={remote_path}&permanently=true"
                resp = requests.delete(delete_endpoint, headers=headers, timeout=10)
                if resp.status_code in (200, 202, 204):
                    self.finished.emit('delete_backup', True, remote_name)
                else:
                    self.finished.emit('delete_backup', False, f"Ошибка удаления: {resp.status_code}")

            elif self.operation == 'sync_student_results':
                local_db_path = self.args[0]
                results_path = '/Sprint Backup/results'
                
                # Ensure results folder exists
                requests.put(f"{base_url}/resources?path={results_path}", headers=headers, timeout=10)
                
                # List results files
                r = requests.get(f"{base_url}/resources?path={results_path}&limit=1000", headers=headers, timeout=10)
                if r.status_code != 200:
                    self.finished.emit('sync_student_results', False, f"Не удалось прочитать папку результатов: {r.text}")
                    return
                    
                items = r.json().get('_embedded', {}).get('items', [])
                results_merged_count = 0
                
                if items:
                    conn = sqlite3.connect(local_db_path)
                    cursor = conn.cursor()
                    
                    try:
                        for item in items:
                            if item.get('type') == 'file' and item.get('name', '').endswith('.json'):
                                file_name = item.get('name')
                                remote_file_path = f"/Sprint Backup/results/{file_name}"
                                
                                # Get download URL
                                r_down = requests.get(f"{base_url}/resources/download?path={remote_file_path}", headers=headers, timeout=10)
                                if r_down.status_code == 200:
                                    down_url = r_down.json().get('href')
                                    r_content = requests.get(down_url, timeout=10)
                                    if r_content.status_code == 200:
                                        data = r_content.json()
                                        
                                        # Insert into history table with time_limit
                                        cursor.execute("""
                                            INSERT INTO history (topic_name, score, time_spent, date_time, student_name, time_limit)
                                            VALUES (?, ?, ?, ?, ?, ?)
                                        """, (
                                            data.get('topic_name'),
                                            data.get('score'),
                                            int(data.get('time_spent', 0)),
                                            data.get('date_time'),
                                            data.get('student_name'),
                                            int(data.get('time_limit', 60))
                                        ))
                                        
                                        # Delete file from Yandex.Disk
                                        requests.delete(f"{base_url}/resources?path={remote_file_path}&permanently=true", headers=headers, timeout=10)
                                        results_merged_count += 1
                        conn.commit()
                    except Exception as merge_err:
                        conn.rollback()
                        conn.close()
                        self.finished.emit('sync_student_results', False, f"Ошибка слияния результатов: {str(merge_err)}")
                        return
                    finally:
                        conn.close()
                        
                self.finished.emit('sync_student_results', True, results_merged_count)

            elif self.operation == 'send_assignment':
                topic_name = self.args[0]
                class_name = self.args[1]
                target_class = self.args[2]
                target_student = self.args[3]
                
                assignment_data = {
                    "topic_name": topic_name,
                    "class_name": class_name,
                    "target_class": target_class,
                    "target_student": target_student,
                    "assigned_at": datetime.now().strftime("%d.%m.%Y %H:%M")
                }
                
                # Ensure assignments folder exists
                requests.put(f"{base_url}/resources?path=/Sprint Backup/assignments", headers=headers, timeout=10)
                
                remote_path = "/Sprint Backup/assignments/active_assignment.json"
                upload_endpoint = f"{base_url}/resources/upload?path={remote_path}&overwrite=true"
                resp = requests.get(upload_endpoint, headers=headers, timeout=10)
                if resp.status_code == 200:
                    upload_url = resp.json().get('href')
                    resp_put = requests.put(upload_url, json=assignment_data, timeout=10)
                    if resp_put.status_code in (200, 201):
                        self.finished.emit('send_assignment', True, topic_name)
                        return
                self.finished.emit('send_assignment', False, "Не удалось сохранить задание на Яндекс.Диск")
        except requests.exceptions.RequestException as e:
            self.finished.emit(self.operation, False, f"Ошибка сети: {str(e)}")
        except Exception as e:
            self.finished.emit(self.operation, False, f"Внутренняя ошибка: {str(e)}")


class YandexAuthWorker(QThread):
    code_received = pyqtSignal(bool, str, str, str)
    auth_finished = pyqtSignal(bool, str)

    def __init__(self, client_id, client_secret):
        super().__init__()
        self.client_id = client_id
        self.client_secret = client_secret
        self.device_code = None
        self.is_running = True

    def run(self):
        if requests is None:
            self.code_received.emit(False, "", "", "")
            self.auth_finished.emit(False, "Библиотека requests не установлена.")
            return

        # Step 1: Get confirmation codes
        url = 'https://oauth.yandex.ru/device/code'
        payload = {'client_id': self.client_id}
        try:
            resp = requests.post(url, data=payload, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                self.device_code = data.get('device_code')
                user_code = data.get('user_code')
                verification_url = data.get('verification_url', 'https://ya.ru/device')
                interval = data.get('interval', 5)
                expires_in = data.get('expires_in', 300)
                self.code_received.emit(True, user_code, self.device_code, verification_url)
            else:
                self.code_received.emit(False, "", "", "")
                return
        except Exception:
            self.code_received.emit(False, "", "", "")
            return

        # Step 2: Poll for token
        poll_url = 'https://oauth.yandex.ru/token'
        poll_payload = {
            'grant_type': 'device_code',
            'code': self.device_code,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }

        start_time = time.time()
        while self.is_running and (time.time() - start_time) < expires_in:
            time.sleep(interval)
            if not self.is_running:
                break
            try:
                token_resp = requests.post(poll_url, data=poll_payload, timeout=10)
                token_data = token_resp.json()
                
                if token_resp.status_code == 200:
                    access_token = token_data.get('access_token')
                    if access_token:
                        self.auth_finished.emit(True, access_token)
                        return
                    else:
                        self.auth_finished.emit(False, "Не удалось получить токен из ответа")
                        return
                elif token_resp.status_code == 400:
                    error = token_data.get('error')
                    if error == 'authorization_pending':
                        continue
                    elif error == 'slow_down':
                        interval += 5
                        continue
                    else:
                        self.auth_finished.emit(False, token_data.get('error_description', error))
                        return
                else:
                    self.auth_finished.emit(False, f"Ошибка авторизации: {token_resp.status_code}")
                    return
            except Exception:
                continue

        self.auth_finished.emit(False, "Время ожидания подтверждения истекло.")

    def stop(self):
        self.is_running = False


# ==========================================
# DATABASE BACKUP DIALOG (CLOUD INTEGRATION)
# ==========================================
class DatabaseBackupDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Резервное копирование Яндекс.Диск")
        
        self.parent_app = parent
        self.client_id = "88e564b2b6af425c87b90293aeb33f15"
        self.client_secret = "b888435e70104f5691ea208545dfadb8"
        self.token = None
        
        self.auth_worker = None
        self.disk_worker = None
        
        # Load token if it exists
        if self.parent_app and hasattr(self.parent_app, 'db'):
            self.token = self.parent_app.db.get_yandex_token()
            
        # Responsive scale
        self.scale = 1.0
        if self.parent_app and hasattr(self.parent_app, 'current_zoom_percent'):
            self.scale = self.parent_app.current_zoom_percent / 100.0
            
        self.resize(int(780 * self.scale), int(480 * self.scale))
        self.setModal(True)
        self.setStyleSheet(parent.styleSheet() if parent else "")
        
        self.init_ui()
        
        if requests is None:
            self.lbl_mgr_status.setText("Ошибка: отсутствует библиотека requests.")
            self.set_controls_enabled(False)
            self.btn_start_auth.setEnabled(False)
            self.btn_start_auth.setText("Ошибка: требуется requests")
            QTimer.singleShot(100, lambda: QMessageBox.critical(
                self,
                "Критическая ошибка",
                "Библиотека 'requests' не установлена на этом компьютере.\n\n"
                "Для работы резервного копирования закройте программу и установите библиотеку, выполнив команду в терминале:\n"
                "pip install requests"
            ))
            return
            
        # If token exists, check auth and list backups, else show auth page
        if self.token:
            self.show_loading_status("Проверка авторизации в Яндекс.Диске...")
            self.run_disk_operation('check_auth')
        else:
            self.stacked_widget.setCurrentIndex(0)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(int(20 * self.scale), int(20 * self.scale), int(20 * self.scale), int(20 * self.scale))
        layout.setSpacing(int(15 * self.scale))
        
        # Stacked Widget to support two views (Auth vs Backups Manager)
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)
        
        # ================= PAGE 0: AUTHORIZATION =================
        page_auth = QWidget()
        lay_auth = QVBoxLayout(page_auth)
        lay_auth.setContentsMargins(0, 0, 0, 0)
        lay_auth.setSpacing(int(15 * self.scale))
        
        lbl_auth_title = QLabel("☁️ Подключение Яндекс.Диска")
        lbl_auth_title.setObjectName("section_title")
        lay_auth.addWidget(lbl_auth_title)
        
        card_auth = QFrame()
        card_auth.setObjectName("card_frame")
        lay_card = QVBoxLayout(card_auth)
        lay_card.setContentsMargins(int(25 * self.scale), int(25 * self.scale), int(25 * self.scale), int(25 * self.scale))
        lay_card.setSpacing(int(15 * self.scale))
        
        self.lbl_auth_desc = QLabel(
            "Для автоматического создания резервных копий базы данных Спринт "
            "необходимо связать программу с вашим аккаунтом Яндекс.\n\n"
            "После авторизации все бэкапы будут безопасно храниться в вашей личной "
            "папке Яндекс.Диска (папка 'Sprint Backup') и вы сможете восстановить "
            "или удалить бэкап в любой момент."
        )
        self.lbl_auth_desc.setWordWrap(True)
        self.lbl_auth_desc.setStyleSheet("font-size: %dpx; color: #4E5968; line-height: 1.4;" % int(14 * self.scale))
        lay_card.addWidget(self.lbl_auth_desc)
        
        # Nested stack inside card to toggle between "Authorize" button and "Polling/Instructions"
        self.nested_auth_stack = QStackedWidget()
        
        # State A: Start Button
        state_start = QWidget()
        lay_state_start = QHBoxLayout(state_start)
        lay_state_start.setContentsMargins(0, 0, 0, 0)
        self.btn_start_auth = QPushButton(" Связать с Яндекс.Диском")
        self.btn_start_auth.setObjectName("primary_button")
        self.btn_start_auth.setIcon(QIcon(get_asset_path("assets/plus.svg")))
        self.btn_start_auth.setIconSize(QSize(int(16 * self.scale), int(16 * self.scale)))
        self.btn_start_auth.setCursor(Qt.PointingHandCursor)
        self.btn_start_auth.setMinimumHeight(int(45 * self.scale))
        self.btn_start_auth.clicked.connect(self.start_device_auth_flow)
        lay_state_start.addWidget(self.btn_start_auth)
        self.nested_auth_stack.addWidget(state_start)
        
        # State B: Display user code & link
        state_code = QWidget()
        lay_state_code = QVBoxLayout(state_code)
        lay_state_code.setContentsMargins(0, 0, 0, 0)
        lay_state_code.setSpacing(int(10 * self.scale))
        
        lbl_code_inst = QLabel("Перейдите на страницу авторизации и введите следующий код:")
        lbl_code_inst.setStyleSheet("font-weight: 600; font-size: %dpx;" % int(13 * self.scale))
        lbl_code_inst.setAlignment(Qt.AlignCenter)
        lay_state_code.addWidget(lbl_code_inst)
        
        self.lbl_user_code = QLabel("XXXX-XXXX")
        self.lbl_user_code.setStyleSheet("font-size: %dpx; font-weight: 800; color: #2688EB; background-color: #F0F2F5; border-radius: 6px; padding: 10px; border: 1px dashed #CCD0D5;" % int(24 * self.scale))
        self.lbl_user_code.setAlignment(Qt.AlignCenter)
        self.lbl_user_code.setTextInteractionFlags(Qt.TextSelectableByMouse)
        lay_state_code.addWidget(self.lbl_user_code)
        
        btn_auth_layout = QHBoxLayout()
        btn_auth_layout.setSpacing(10)
        
        self.btn_open_ya_link = QPushButton(" Открыть ya.ru/device")
        self.btn_open_ya_link.setIcon(QIcon(get_asset_path("assets/play.svg")))
        self.btn_open_ya_link.setIconSize(QSize(int(14 * self.scale), int(14 * self.scale)))
        self.btn_open_ya_link.setCursor(Qt.PointingHandCursor)
        self.btn_open_ya_link.clicked.connect(self.open_auth_page_in_browser)
        btn_auth_layout.addWidget(self.btn_open_ya_link, stretch=1)
        
        self.btn_copy_user_code = QPushButton(" 📋 Копировать код")
        self.btn_copy_user_code.setIcon(QIcon(get_asset_path("assets/plus.svg")))
        self.btn_copy_user_code.setIconSize(QSize(int(14 * self.scale), int(14 * self.scale)))
        self.btn_copy_user_code.setCursor(Qt.PointingHandCursor)
        self.btn_copy_user_code.clicked.connect(self.copy_user_code_to_clipboard)
        btn_auth_layout.addWidget(self.btn_copy_user_code, stretch=1)
        
        lay_state_code.addLayout(btn_auth_layout)
        
        self.lbl_auth_status = QLabel("🕒 Ожидание подтверждения в браузере...")
        self.lbl_auth_status.setStyleSheet("color: #65676B; font-weight: bold; font-size: %dpx;" % int(12 * self.scale))
        self.lbl_auth_status.setAlignment(Qt.AlignCenter)
        lay_state_code.addWidget(self.lbl_auth_status)
        
        self.nested_auth_stack.addWidget(state_code)
        
        lay_card.addWidget(self.nested_auth_stack)
        lay_auth.addWidget(card_auth)
        
        lay_auth.addStretch()
        
        # Bottom controls for Page 0
        lay_auth_bottom = QHBoxLayout()
        lay_auth_bottom.addStretch()
        btn_close_auth = QPushButton("Закрыть")
        btn_close_auth.setCursor(Qt.PointingHandCursor)
        btn_close_auth.clicked.connect(self.reject)
        lay_auth_bottom.addWidget(btn_close_auth)
        lay_auth.addLayout(lay_auth_bottom)
        
        self.stacked_widget.addWidget(page_auth) # Index 0
        
        # ================= PAGE 1: BACKUPS MANAGER =================
        page_manager = QWidget()
        lay_mgr = QVBoxLayout(page_manager)
        lay_mgr.setContentsMargins(0, 0, 0, 0)
        lay_mgr.setSpacing(int(12 * self.scale))
        
        # Page 1 Header
        lay_mgr_header = QHBoxLayout()
        lbl_mgr_title = QLabel("☁️ Резервные копии (Яндекс.Диск)")
        lbl_mgr_title.setObjectName("section_title")
        lay_mgr_header.addWidget(lbl_mgr_title)
        lay_mgr_header.addStretch()
        
        self.lbl_disk_space = QLabel("Загрузка данных диска...")
        self.lbl_disk_space.setStyleSheet("color: #65676B; font-size: %dpx; font-weight: 600;" % int(13 * self.scale))
        lay_mgr_header.addWidget(self.lbl_disk_space)
        lay_mgr.addLayout(lay_mgr_header)
        
        # Page 1 Content split (Table left, Buttons right)
        lay_mgr_columns = QHBoxLayout()
        lay_mgr_columns.setSpacing(int(15 * self.scale))
        
        # Left Side: Table of backups
        self.backups_table = QTableWidget()
        self.backups_table.setColumnCount(3)
        self.backups_table.setHorizontalHeaderLabels(["Имя резервной копии", "Дата создания", "Размер"])
        self.backups_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.backups_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.backups_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.backups_table.setAlternatingRowColors(True)
        self.backups_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #E4E6EB;
                border: 1px solid #E4E6EB;
                border-radius: %dpx;
            }
        """ % int(8 * self.scale))
        
        header = self.backups_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.backups_table.itemSelectionChanged.connect(self.on_backup_selection_changed)
        lay_mgr_columns.addWidget(self.backups_table, stretch=3)
        
        # Right Side: Action panel card
        card_actions = QFrame()
        card_actions.setObjectName("card_frame")
        lay_actions = QVBoxLayout(card_actions)
        lay_actions.setContentsMargins(int(15 * self.scale), int(15 * self.scale), int(15 * self.scale), int(15 * self.scale))
        lay_actions.setSpacing(int(10 * self.scale))
        
        lbl_act_title = QLabel("Действия:")
        lbl_act_title.setObjectName("card_title")
        lay_actions.addWidget(lbl_act_title)
        
        self.btn_create_b = QPushButton(" Создать бэкап")
        self.btn_create_b.setObjectName("primary_button")
        self.btn_create_b.setIcon(QIcon(get_asset_path("assets/plus.svg")))
        self.btn_create_b.setIconSize(QSize(int(14 * self.scale), int(14 * self.scale)))
        self.btn_create_b.setCursor(Qt.PointingHandCursor)
        self.btn_create_b.clicked.connect(self.create_new_backup)
        lay_actions.addWidget(self.btn_create_b)
        
        self.btn_restore_b = QPushButton(" Восстановить")
        self.btn_restore_b.setIcon(QIcon(get_asset_path("assets/play.svg")))
        self.btn_restore_b.setIconSize(QSize(int(14 * self.scale), int(14 * self.scale)))
        self.btn_restore_b.setCursor(Qt.PointingHandCursor)
        self.btn_restore_b.clicked.connect(self.restore_selected_backup)
        self.btn_restore_b.setEnabled(False)
        lay_actions.addWidget(self.btn_restore_b)
        
        self.btn_delete_b = QPushButton(" Удалить бэкап")
        self.btn_delete_b.setObjectName("danger_button")
        self.btn_delete_b.setIcon(QIcon(get_asset_path("assets/trash.svg")))
        self.btn_delete_b.setIconSize(QSize(int(14 * self.scale), int(14 * self.scale)))
        self.btn_delete_b.setCursor(Qt.PointingHandCursor)
        self.btn_delete_b.clicked.connect(self.delete_selected_backup)
        self.btn_delete_b.setEnabled(False)
        lay_actions.addWidget(self.btn_delete_b)
        
        # New Mobile Sync buttons
        self.btn_sync_results = QPushButton(" Слияние ответов")
        self.btn_sync_results.setIcon(QIcon(get_asset_path("assets/history.svg")))
        self.btn_sync_results.setIconSize(QSize(int(14 * self.scale), int(14 * self.scale)))
        self.btn_sync_results.setCursor(Qt.PointingHandCursor)
        self.btn_sync_results.setToolTip("Синхронизировать и объединить результаты учеников из мобильного приложения")
        self.btn_sync_results.clicked.connect(self.sync_student_results_clicked)
        lay_actions.addWidget(self.btn_sync_results)
        
        self.btn_send_assignment = QPushButton(" Назначить тест")
        self.btn_send_assignment.setIcon(QIcon(get_asset_path("assets/trophy.svg")))
        self.btn_send_assignment.setIconSize(QSize(int(14 * self.scale), int(14 * self.scale)))
        self.btn_send_assignment.setCursor(Qt.PointingHandCursor)
        self.btn_send_assignment.setToolTip("Опубликовать выбранную тему админ-панели как домашнее задание")
        self.btn_send_assignment.clicked.connect(self.send_assignment_clicked)
        lay_actions.addWidget(self.btn_send_assignment)
        
        self.btn_copy_token = QPushButton(" 📋 Копировать ключ")
        self.btn_copy_token.setIcon(QIcon(get_asset_path("assets/settings.svg")))
        self.btn_copy_token.setIconSize(QSize(int(14 * self.scale), int(14 * self.scale)))
        self.btn_copy_token.setCursor(Qt.PointingHandCursor)
        self.btn_copy_token.setToolTip("Копировать секретный ключ подключения для отправки ученикам")
        self.btn_copy_token.clicked.connect(self.copy_teacher_token_to_clipboard)
        lay_actions.addWidget(self.btn_copy_token)
        
        lay_actions.addSpacing(int(15 * self.scale))
        lay_actions.addStretch()
        
        self.btn_logout = QPushButton(" Выйти из аккаунта")
        self.btn_logout.setIcon(QIcon(get_asset_path("assets/back.svg")))
        self.btn_logout.setIconSize(QSize(int(14 * self.scale), int(14 * self.scale)))
        self.btn_logout.setCursor(Qt.PointingHandCursor)
        self.btn_logout.clicked.connect(self.logout_yandex)
        lay_actions.addWidget(self.btn_logout)
        
        lay_mgr_columns.addWidget(card_actions, stretch=1)
        lay_mgr.addLayout(lay_mgr_columns)
        
        # Bottom controls for Page 1
        lay_mgr_bottom = QHBoxLayout()
        self.lbl_mgr_status = QLabel("Загрузка резервных копий...")
        self.lbl_mgr_status.setStyleSheet("color: #65676B; font-size: %dpx;" % int(12 * self.scale))
        lay_mgr_bottom.addWidget(self.lbl_mgr_status)
        lay_mgr_bottom.addStretch()
        
        btn_close_mgr = QPushButton("Закрыть")
        btn_close_mgr.setCursor(Qt.PointingHandCursor)
        btn_close_mgr.clicked.connect(self.reject)
        lay_mgr_bottom.addWidget(btn_close_mgr)
        lay_mgr.addLayout(lay_mgr_bottom)
        
        self.stacked_widget.addWidget(page_manager) # Index 1

    # ==========================================
    # AUTHORIZATION LOGIC FLOW (DEVICE FLOW)
    # ==========================================
    def start_device_auth_flow(self):
        self.btn_start_auth.setEnabled(False)
        self.btn_start_auth.setText("Подключение к OAuth...")
        
        self.auth_worker = YandexAuthWorker(self.client_id, self.client_secret)
        self.auth_worker.code_received.connect(self.on_device_code_received)
        self.auth_worker.auth_finished.connect(self.on_device_auth_finished)
        self.auth_worker.start()

    def on_device_code_received(self, success, user_code, device_code, verification_url):
        if success:
            self.lbl_user_code.setText(user_code)
            self.verification_url = verification_url
            self.nested_auth_stack.setCurrentIndex(1)
        else:
            self.btn_start_auth.setEnabled(True)
            self.btn_start_auth.setText(" Связать с Яндекс.Диском")
            QMessageBox.critical(self, "Ошибка подключения", "Не удалось связаться с сервером авторизации Яндекс. Проверьте интернет-соединение.")

    def open_auth_page_in_browser(self):
        if hasattr(self, 'verification_url'):
            QDesktopServices.openUrl(QUrl(self.verification_url))
        else:
            QDesktopServices.openUrl(QUrl("https://ya.ru/device"))

    def copy_user_code_to_clipboard(self):
        code_text = self.lbl_user_code.text().strip()
        if code_text and code_text != "XXXX-XXXX":
            QApplication.clipboard().setText(code_text)
            QMessageBox.information(self, "Код скопирован", f"Код авторизации '{code_text}' успешно скопирован в буфер обмена!\n\nВставьте его на странице ya.ru/device.")

    def on_device_auth_finished(self, success, access_token_or_error):
        if success:
            self.token = access_token_or_error
            if self.parent_app and hasattr(self.parent_app, 'db'):
                self.parent_app.db.update_yandex_token(self.token)
                
            QMessageBox.information(self, "Авторизация успешна", "Программа успешно связана с вашим Яндекс.Диском!")
            self.show_loading_status("Подключение к диску...")
            self.stacked_widget.setCurrentIndex(1)
            self.run_disk_operation('check_auth')
        else:
            QMessageBox.warning(self, "Ошибка авторизации", access_token_or_error)
            self.nested_auth_stack.setCurrentIndex(0)
            self.btn_start_auth.setEnabled(True)
            self.btn_start_auth.setText(" Связать с Яндекс.Диском")

    # ==========================================
    # WORKER CONTROLLER (DISK OPERATIONS)
    # ==========================================
    def run_disk_operation(self, operation, *args):
        self.set_controls_enabled(False)
        self.disk_worker = YandexDiskWorker(self.token, operation, *args)
        self.disk_worker.finished.connect(self.on_disk_operation_finished)
        self.disk_worker.start()

    def on_disk_operation_finished(self, operation, success, result):
        self.set_controls_enabled(True)
        
        if not success:
            if operation == 'check_auth':
                is_auth_failure = ("Недействительный токен" in str(result) or "401" in str(result) or "Unauthorized" in str(result))
                
                if is_auth_failure:
                    self.token = None
                    if self.parent_app and hasattr(self.parent_app, 'db'):
                        self.parent_app.db.update_yandex_token(None)
                    self.stacked_widget.setCurrentIndex(0)
                    self.nested_auth_stack.setCurrentIndex(0)
                    self.btn_start_auth.setEnabled(True)
                    self.btn_start_auth.setText(" Связать с Яндекс.Диском")
                    QMessageBox.warning(self, "Ошибка авторизации", f"Сессия Яндекс.Диска устарела или недействительна.\nПожалуйста, авторизуйтесь заново.")
                else:
                    self.stacked_widget.setCurrentIndex(1)
                    self.lbl_disk_space.setText("Офлайн режим")
                    self.lbl_mgr_status.setText("Ошибка соединения с Яндекс.Диском.")
                    self.set_controls_enabled(False)
                    QMessageBox.warning(self, "Ошибка соединения", "Не удалось установить связь с Яндекс.Диском.\n\nПроверьте ваше интернет-подключение.\nКлюч авторизации сохранен и активен.")
            else:
                QMessageBox.critical(self, "Ошибка диска", f"Операция '{operation}' не удалась: {result}")
                self.lbl_mgr_status.setText("Ошибка операции.")
            return

        if operation == 'check_auth':
            free = result.get('free', 0)
            total = result.get('total', 0)
            self.lbl_disk_space.setText(f"Свободно: {self.format_size(free)} из {self.format_size(total)}")
            
            self.show_loading_status("Загрузка резервных копий...")
            self.run_disk_operation('list_backups')

        elif operation == 'list_backups':
            self.populate_backups_table(result)
            self.lbl_mgr_status.setText(f"Готово. Всего бэкапов найдено: {len(result)}")

        elif operation == 'create_backup':
            QMessageBox.information(self, "Бэкап успешно создан", f"Резервная копия '{result}' создана и загружена в Яндекс.Диск!")
            self.run_disk_operation('check_auth')

        elif operation == 'restore_backup':
            self.perform_restore(result)

        elif operation == 'delete_backup':
            QMessageBox.information(self, "Бэкап удален", f"Резервная копия '{result}' успешно удалена с Яндекс.Диска.")
            self.run_disk_operation('check_auth')

        elif operation == 'sync_student_results':
            QMessageBox.information(self, "Результаты синхронизированы", f"Синхронизация результатов завершена! Успешно скачано и объединено результатов учеников: {result}")
            # Refresh parents lists and history
            if self.parent_app:
                try:
                    self.parent_app.refresh_history_table()
                except Exception:
                    pass
            self.run_disk_operation('check_auth')

        elif operation == 'send_assignment':
            QMessageBox.information(self, "Задание назначено", f"Тест '{result}' успешно опубликован на Яндекс.Диске! Все ученики на мобильных увидят его как активное задание.")
            self.run_disk_operation('check_auth')

    # ==========================================
    # ACTIONS IMPLEMENTATION
    # ==========================================
    def create_new_backup(self):
        if not self.parent_app or not hasattr(self.parent_app, 'db'):
            return
            
        local_db_path = self.parent_app.db.db_path
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        remote_name = f"sprint_backup_{timestamp}.db"
        
        self.show_loading_status("Создание и загрузка резервной копии базы данных...")
        self.run_disk_operation('create_backup', local_db_path, remote_name)

    def restore_selected_backup(self):
        selected_row = self.backups_table.currentRow()
        if selected_row < 0:
            return
            
        backup_name = self.backups_table.item(selected_row, 0).text()
        
        confirm = QMessageBox.question(
            self,
            "Восстановление базы данных",
            f"Вы действительно хотите восстановить базу данных из резервной копии {backup_name}?\n\n"
            "ВНИМАНИЕ: Все ваши текущие настройки, вопросы и результаты учеников будут безвозвратно "
            "заменены данными из бэкапа!",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            self.show_loading_status("Скачивание резервной копии...")
            self.run_disk_operation('restore_backup', backup_name)

    def perform_restore(self, temp_restore_path):
        if not self.parent_app or not hasattr(self.parent_app, 'db'):
            return
            
        local_db_path = self.parent_app.db.db_path
        safety_old_path = local_db_path + "_old_safety"
        
        if os.path.exists(safety_old_path):
            try:
                os.remove(safety_old_path)
            except Exception:
                pass
                
        try:
            shutil.copy(local_db_path, safety_old_path)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка восстановления", f"Не удалось создать резервную копию перед заменой: {str(e)}")
            if os.path.exists(temp_restore_path):
                try:
                    os.remove(temp_restore_path)
                except Exception:
                    pass
            return

        try:
            shutil.copy(temp_restore_path, local_db_path)
            
            for suffix in ['-wal', '-shm']:
                wal_file = local_db_path + suffix
                if os.path.exists(wal_file):
                    try:
                        os.remove(wal_file)
                    except Exception as remove_err:
                        print(f"Warning: could not delete {wal_file}: {remove_err}")
            
            test_conn = sqlite3.connect(local_db_path)
            try:
                test_conn.execute("SELECT COUNT(*) FROM settings")
                test_conn.close()
            except Exception as test_err:
                test_conn.close()
                raise Exception(f"Тест целостности новой базы данных не пройден: {str(test_err)}")
                
            if os.path.exists(safety_old_path):
                try:
                    os.remove(safety_old_path)
                except Exception:
                    pass
                
            if os.path.exists(temp_restore_path):
                try:
                    os.remove(temp_restore_path)
                except Exception:
                    pass
                
            QMessageBox.information(
                self, 
                "Успешное восстановление", 
                "База данных успешно восстановлена из резервной копии!\n"
                "Все данные программы были обновлены."
            )
            
            try:
                self.parent_app.sprint_total_time, self.parent_app.current_zoom_percent, animations_enabled_val = self.parent_app.db.get_settings()
                self.parent_app.animations_enabled = (animations_enabled_val == 1)
                self.parent_app.apply_zoom_scale(self.parent_app.current_zoom_percent)
                
                # Perform full and obvious visual reload to parent app!
                self.parent_app.refresh_history_table()
                self.parent_app.refresh_admin_topics()
                self.parent_app.show_lobby() # Return directly to Lobby so restored Classes are immediately visible!
            except Exception as refresh_err:
                print(f"Error post-restore refresh: {refresh_err}")
                
            QMessageBox.information(
                self, 
                "Восстановление завершено", 
                "База данных успешно импортирована!\n"
                "Все настройки, учебные темы, вопросы и результаты были мгновенно обновлены в реальном времени."
            )
            self.accept()
                
        except Exception as swap_err:
            try:
                shutil.copy(safety_old_path, local_db_path)
            except Exception:
                pass
            
            if os.path.exists(safety_old_path):
                try:
                    os.remove(safety_old_path)
                except Exception:
                    pass
                    
            if os.path.exists(temp_restore_path):
                try:
                    os.remove(temp_restore_path)
                except Exception:
                    pass
                    
            QMessageBox.critical(
                self, 
                "Ошибка восстановления", 
                f"Критическая ошибка при замене базы данных. Произведен откат к прежнему состоянию.\n\nДетали: {str(swap_err)}"
            )

    def delete_selected_backup(self):
        selected_row = self.backups_table.currentRow()
        if selected_row < 0:
            return
            
        backup_name = self.backups_table.item(selected_row, 0).text()
        
        confirm = QMessageBox.question(
            self,
            "Удаление резервной копии",
            f"Вы действительно хотите навсегда удалить резервную копию {backup_name} с Яндекс.Диска?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            self.show_loading_status("Удаление бэкапа...")
            self.run_disk_operation('delete_backup', backup_name)

    def logout_yandex(self):
        confirm = QMessageBox.question(
            self,
            "Выход из аккаунта",
            "Вы действительно хотите выйти из аккаунта Яндекс.Диск в программе?\n"
            "Токен авторизации будет удален.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            self.token = None
            if self.parent_app and hasattr(self.parent_app, 'db'):
                self.parent_app.db.update_yandex_token(None)
            
            self.stacked_widget.setCurrentIndex(0)
            self.nested_auth_stack.setCurrentIndex(0)
            self.btn_start_auth.setEnabled(True)
            self.btn_start_auth.setText(" Связать с Яндекс.Диском")
            QMessageBox.information(self, "Выход выполнен", "Вы успешно вышли из аккаунта Яндекс.Диска.")

    # ==========================================
    # HELPERS
    # ==========================================
    def show_loading_status(self, text):
        self.lbl_mgr_status.setText(text)

    def set_controls_enabled(self, enabled):
        self.btn_create_b.setEnabled(enabled)
        if enabled:
            has_selection = (self.backups_table.currentRow() >= 0)
            self.btn_restore_b.setEnabled(has_selection)
            self.btn_delete_b.setEnabled(has_selection)
            self.btn_sync_results.setEnabled(True)
            self.btn_send_assignment.setEnabled(True)
            self.btn_copy_token.setEnabled(True)
        else:
            self.btn_restore_b.setEnabled(False)
            self.btn_delete_b.setEnabled(False)
            self.btn_sync_results.setEnabled(False)
            self.btn_send_assignment.setEnabled(False)
            self.btn_copy_token.setEnabled(False)
            
        self.btn_logout.setEnabled(enabled)
        self.backups_table.setEnabled(enabled)

    def on_backup_selection_changed(self):
        has_selection = (self.backups_table.currentRow() >= 0)
        self.btn_restore_b.setEnabled(has_selection)
        self.btn_delete_b.setEnabled(has_selection)

    def populate_backups_table(self, backups):
        self.backups_table.itemSelectionChanged.disconnect(self.on_backup_selection_changed)
        self.backups_table.setRowCount(0)
        
        for b in backups:
            row = self.backups_table.rowCount()
            self.backups_table.insertRow(row)
            
            item_name = QTableWidgetItem(b['name'])
            item_name.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.backups_table.setItem(row, 0, item_name)
            
            formatted_date = self.format_iso_date(b['created'])
            item_date = QTableWidgetItem(formatted_date)
            item_date.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.backups_table.setItem(row, 1, item_date)
            
            formatted_size = self.format_size(b['size'])
            item_size = QTableWidgetItem(formatted_size)
            item_size.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.backups_table.setItem(row, 2, item_size)
            
        self.backups_table.itemSelectionChanged.connect(self.on_backup_selection_changed)
        self.btn_restore_b.setEnabled(False)
        self.btn_delete_b.setEnabled(False)

    def format_size(self, bytes_val):
        if bytes_val >= 1024**3:
            return f"{bytes_val / (1024**3):.2f} ГБ"
        elif bytes_val >= 1024**2:
            return f"{bytes_val / (1024**2):.1f} МБ"
        elif bytes_val >= 1024:
            return f"{bytes_val / 1024:.1f} КБ"
        else:
            return f"{bytes_val} Б"

    def format_iso_date(self, iso_str):
        try:
            clean_str = iso_str.replace('Z', '').split('.')[0]
            dt = datetime.strptime(clean_str, "%Y-%m-%dT%H:%M:%S")
            return dt.strftime("%d.%m.%Y %H:%M")
        except Exception:
            return iso_str

    def sync_student_results_clicked(self):
        if not self.parent_app or not hasattr(self.parent_app, 'db'):
            return
        self.show_loading_status("Синхронизация и слияние результатов...")
        self.run_disk_operation('sync_student_results', self.parent_app.db.db_path)

    def copy_teacher_token_to_clipboard(self):
        if self.token:
            QApplication.clipboard().setText(self.token)
            QMessageBox.information(self, "Ключ скопирован", "Секретный ключ подключения успешно скопирован в буфер обмена!\n\nОтправьте его ученикам, чтобы они ввели его в мобильном приложении.")
        else:
            QMessageBox.warning(self, "Ошибка", "Сначала привяжите Яндекс.Диск для генерации ключа.")

    def send_assignment_clicked(self):
        if not self.parent_app:
            return
        # Open the targeted PublishAssignmentDialog!
        dialog = PublishAssignmentDialog(self, self.parent_app)
        if dialog.exec_() == QDialog.Accepted:
            self.show_loading_status("Публикация задания в облаке...")
            self.run_disk_operation('send_assignment', dialog.topic_name, dialog.class_name, dialog.target_class, dialog.target_student)

    def closeEvent(self, event):
        if self.auth_worker and self.auth_worker.isRunning():
            self.auth_worker.stop()
            self.auth_worker.wait()
        if self.disk_worker and self.disk_worker.isRunning():
            self.disk_worker.terminate()
            self.disk_worker.wait()
        super().closeEvent(event)



# ==========================================
# TARGETED ASSIGNMENT DIALOG
# ==========================================
class PublishAssignmentDialog(QDialog):
    def __init__(self, parent_dialog, parent_app):
        super().__init__(parent_dialog)
        self.parent_dialog = parent_dialog
        self.parent_app = parent_app
        self.setWindowTitle("Назначить задание ученикам")
        
        self.scale = parent_dialog.scale
        self.resize(int(360 * self.scale), int(260 * self.scale))
        self.setStyleSheet(parent_dialog.styleSheet())
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        lbl_title = QLabel("Выберите тест и целевой класс:")
        lbl_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(lbl_title)
        
        # Class selection
        lbl_class = QLabel("Раздел:")
        lbl_class.setStyleSheet("font-size: 11px; color: #65676B;")
        layout.addWidget(lbl_class)
        self.class_combo = QComboBox()
        self.class_combo.currentIndexChanged.connect(self.on_class_changed)
        layout.addWidget(self.class_combo)
        
        # Topic selection
        lbl_topic = QLabel("Тема спринта:")
        lbl_topic.setStyleSheet("font-size: 11px; color: #65676B;")
        layout.addWidget(lbl_topic)
        self.topic_combo = QComboBox()
        layout.addWidget(self.topic_combo)
        
        # Target audience
        lbl_target = QLabel("Кому назначить задание (класс):")
        lbl_target.setStyleSheet("font-size: 11px; color: #65676B;")
        layout.addWidget(lbl_target)
        self.target_combo = QComboBox()
        layout.addWidget(self.target_combo)
        
        # Target student
        lbl_student = QLabel("Целевой ученик (ФИО или 'Все'):")
        lbl_student.setStyleSheet("font-size: 11px; color: #65676B;")
        layout.addWidget(lbl_student)
        self.student_input = QLineEdit()
        self.student_input.setText("Все")
        layout.addWidget(self.student_input)
        
        # Populate classes
        classes = self.parent_app.db.get_classes()
        for cid, name in classes:
            self.class_combo.addItem(name, cid)
            self.target_combo.addItem(name, cid)
            
        if self.class_combo.count() > 0:
            self.class_combo.setCurrentIndex(0)
            self.on_class_changed()
            
        # Buttons
        btn_layout = QHBoxLayout()
        self.btn_publish = QPushButton(" Опубликовать")
        self.btn_publish.setObjectName("primary_button")
        self.btn_publish.clicked.connect(self.on_publish)
        
        btn_cancel = QPushButton("Отмена")
        btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(self.btn_publish)
        layout.addLayout(btn_layout)
        
    def on_class_changed(self):
        class_id = self.class_combo.currentData()
        if class_id is None:
            return
        self.topic_combo.clear()
        
        # Add cumulative test
        class_name = self.class_combo.currentText()
        self.topic_combo.addItem(f"🏆 Итоговый тест за {class_name}")
        
        # Add actual topics
        topics = self.parent_app.db.get_topics_by_class(class_id)
        for tid, name in topics:
            self.topic_combo.addItem(name)
            
    def on_publish(self):
        self.topic_name = self.topic_combo.currentText()
        self.class_name = self.class_combo.currentText()
        self.target_class = self.target_combo.currentText()
        self.target_student = self.student_input.text().strip()
        self.accept()
