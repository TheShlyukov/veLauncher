from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import minecraft_launcher_lib
import subprocess
import sys
import logging
import os
import requests
import platform
import webbrowser

LAUNCHER_VERSION = str("alpha v0.1.4")

app = QApplication([])

main = QWidget()
main.setFixedSize(400, 250)  # Увеличен размер окна для удобства
main.setWindowTitle("veLauncher")

ver_label = "Select version:"
nick_label = "Enter username:"
version_combo = QComboBox()
username1 = QLineEdit()
username1.setFixedWidth(170)
username = ""
folder_b = QPushButton("Open folder")
start_b = QPushButton("Play!")
settings_b = QPushButton("Settings")  # Добавляем кнопку Settings
package = QLabel("waiting")
package.setFixedHeight(16)
progressbar = QProgressBar()

MLayout = QHBoxLayout()

MHLayout1 = QFormLayout()
MHLayout2 = QFormLayout()
MHLayout3 = QHBoxLayout()
MHLayout4 = QHBoxLayout()
MHLayout5 = QHBoxLayout()

MVLayout1 = QVBoxLayout()

MLayout.addLayout(MVLayout1)

MHLayout1.addRow(ver_label, version_combo)
MHLayout2.addRow(nick_label, username1)
MHLayout4.addWidget(progressbar)
MHLayout3.addWidget(package)
MHLayout5.addWidget(folder_b)
MHLayout5.addWidget(start_b)
MHLayout5.addWidget(settings_b)  # Кнопка Settings в главном окне

MVLayout1.addLayout(MHLayout1)
MVLayout1.addLayout(MHLayout2)
MVLayout1.addLayout(MHLayout3)
MVLayout1.addLayout(MHLayout4)
MVLayout1.addLayout(MHLayout5)

main.setLayout(MLayout)
main.show()

minecraft_directory = minecraft_launcher_lib.utils.get_minecraft_directory()

def maximum(max_value, value):
    max_value[0] = value

def show_error(title, message):
    logging.error(f"{title}: {message}")
    msg_box = QMessageBox()
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.exec()

def check_internet():
    try:
        requests.get('https://www.google.com', timeout=3)
        return True
    except requests.ConnectionError:
        return False

# Настройки с использованием QSettings
settings = QSettings("veLauncher", "SettingsApp")

# Загружаем настройки при старте
def load_settings():
    memory_size = settings.value("memory", 2048, type=int)
    show_alpha = settings.value("show_alpha", True, type=bool)
    show_beta = settings.value("show_beta", True, type=bool)
    show_snapshots = settings.value("show_snapshots", True, type=bool)
    show_installed_only = settings.value("show_installed_only", False, type=bool)
    return memory_size, show_alpha, show_beta, show_snapshots, show_installed_only

def save_settings(memory_size, show_alpha, show_beta, show_snapshots, show_installed_only):
    settings.setValue("memory", memory_size)
    settings.setValue("show_alpha", show_alpha)
    settings.setValue("show_beta", show_beta)
    settings.setValue("show_snapshots", show_snapshots)
    settings.setValue("show_installed_only", show_installed_only)

def is_version_installed(minecraft_directory, version_id):
    # Проверяем, существует ли папка с версией
    version_path = os.path.join(minecraft_directory, "versions", version_id)
    return os.path.exists(version_path)

def get_version_type(version_id):
    version_path = os.path.join(minecraft_directory, "versions", version_id)
    if not os.path.exists(version_path):
        return "Unknown"
    
    # Проверяем наличие fabric.mod.json
    fabric_mod_json = os.path.join(version_path, "META-INF", "fabric.mod.json")
    if os.path.exists(fabric_mod_json):
        return "Fabric"
    
    # Проверяем наличие forge_version.json или similar
    forge_version_json = os.path.join(version_path, "forge_version.json")
    if os.path.exists(forge_version_json):
        return "Forge"
    
    # По умолчанию считаем ванильной
    return "Vanilla"

def load_versions(show_alpha=True, show_beta=True, show_snapshots=True, show_installed_only=False):
    version_combo.clear()

    # Проверяем интернет-соединение
    online = check_internet()

    if not online and not show_installed_only:
        # Нет интернета и не включен режим только установленных версий
        show_error("Offline Mode", "Internet connection not detected. Switching to Offline Mode.")
        save_settings(memory_size, True, True, True, True)
        show_installed_only = True

    if not show_installed_only and online:
        try:
            # Получаем список доступных онлайн версий
            online_versions = minecraft_launcher_lib.utils.get_version_list()
            for version in online_versions:
                version_id = version['id']
                version_type = version.get('type', '')
                
                # Фильтруем версии по типу
                if version_type == 'old_alpha' and not show_alpha:
                    continue
                if version_type == 'old_beta' and not show_beta:
                    continue
                if version_type == 'snapshot' and not show_snapshots:
                    continue
                
                # Добавляем только ванильные версии из онлайн списка
                version_combo.addItem(version_id)
        except Exception as e:
            show_error("Error", f"Failed to load online versions: {e}")

    # Сканируем папку versions для установленных версий
    try:
        installed_versions = os.listdir(os.path.join(minecraft_directory, "versions"))
        for version_id in installed_versions:
            # Проверяем, это папка
            version_path = os.path.join(minecraft_directory, "versions", version_id)
            if not os.path.isdir(version_path):
                continue

            version_type = get_version_type(version_id)

            # Фильтруем по типу
            if version_type == 'Alpha' and not show_alpha:
                continue
            if version_type == 'Beta' and not show_beta:
                continue
            if version_type == 'snapshot' and not show_snapshots:
                continue

            # Добавляем установленную версию с типом
            version_combo.addItem(f"{version_id} ({version_type})")
    except Exception as e:
        show_error("Error", f"Failed to load installed versions: {e}")

def open_settings_dialog():
    dialog = QDialog(main)
    dialog.setWindowTitle("Settings")
    dialog.setFixedSize(400, 350)  # Увеличиваем размер окна настроек

    layout = QVBoxLayout()

    launcher_version = "Version: " + LAUNCHER_VERSION
    version_label = QLabel(str(launcher_version))

    # Ползунок для выделяемой памяти
    memory_label = QLabel(f"Current memory size: {memory_size} MB")
    memory_slider = QSlider(Qt.Orientation.Horizontal)
    memory_slider.setMinimum(512)
    memory_slider.setMaximum(8192)
    memory_slider.setValue(memory_size)
    
    memory_input = QLineEdit()
    memory_input.setValidator(QIntValidator(512, 8192))  # Ограничиваем ввод значений
    memory_input.setText(str(memory_size))

    def update_memory_label(value):
        memory_label.setText(f"Memory size: {value} MB")

    # Связь между слайдером и текстовым полем
    memory_slider.valueChanged.connect(lambda value: memory_input.setText(str(value)))
    
    # Применение изменения памяти только при нажатии Enter
    def on_memory_input_return_pressed():
        try:
            value = int(memory_input.text())
        except ValueError:
            value = memory_size
        if value < 512:
            value = 512
        elif value > 8192:
            value = 8192
        memory_slider.setValue(value)
    memory_input.returnPressed.connect(on_memory_input_return_pressed)

    layout.addWidget(version_label)
    layout.addWidget(memory_label)
    layout.addWidget(memory_slider)
    layout.addWidget(memory_input)

    # Чекбоксы для отображения версий
    alpha_checkbox = QCheckBox("Show Alpha versions")
    alpha_checkbox.setChecked(show_alpha)
    
    beta_checkbox = QCheckBox("Show Beta versions")
    beta_checkbox.setChecked(show_beta)

    snapshots_checkbox = QCheckBox("Show Snapshots")
    snapshots_checkbox.setChecked(show_snapshots)

    installed_only_checkbox = QCheckBox("Show Installed versions only")
    installed_only_checkbox.setChecked(show_installed_only)

    layout.addWidget(alpha_checkbox)
    layout.addWidget(beta_checkbox)
    layout.addWidget(snapshots_checkbox)
    layout.addWidget(installed_only_checkbox)

    # Кнопка для сброса памяти
    reset_memory_button = QPushButton("Reset memory to default (2048 MB)")
    layout.addWidget(reset_memory_button)

    def reset_memory():
        memory_slider.setValue(2048)
        memory_input.setText("2048")
    reset_memory_button.clicked.connect(reset_memory)

    # Кнопка для открытия GitHub
    def open_github():
        webbrowser.open('https://github.com/TheShlyukov/veLauncher')

    github_button = QPushButton("Open GitHub Page")
    layout.addWidget(github_button)
    github_button.clicked.connect(open_github)

    # Кнопки для сохранения и отмены
    button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
    layout.addWidget(button_box)

    # Функция для сохранения и проверки введённого значения
    def save_and_close():
        global memory_size, show_alpha, show_beta, show_snapshots, show_installed_only
        try:
            memory_value = int(memory_input.text())
            if memory_value < 512:
                memory_value = 512
            elif memory_value > 8192:
                memory_value = 8192
        except ValueError:
            memory_value = 2048  # Если что-то не так, установить значение по умолчанию

        memory_size = memory_value
        memory_slider.setValue(memory_size)
        
        show_alpha = alpha_checkbox.isChecked()
        show_beta = beta_checkbox.isChecked()
        show_snapshots = snapshots_checkbox.isChecked()
        show_installed_only = installed_only_checkbox.isChecked()

        save_settings(memory_size, show_alpha, show_beta, show_snapshots, show_installed_only)
        load_versions(show_alpha, show_beta, show_snapshots, show_installed_only)
        dialog.accept()

    # Обработка кнопок
    button_box.accepted.connect(save_and_close)
    button_box.rejected.connect(dialog.reject)

    dialog.setLayout(layout)
    dialog.exec()

settings_b.clicked.connect(open_settings_dialog)

saved_username = settings.value("username", "", type=str)
saved_version = settings.value("version", "", type=str)
username1.setText(saved_username)
if saved_version:
    index = version_combo.findText(saved_version)
    if index != -1:
        version_combo.setCurrentIndex(index)



def save_last_used():
    settings.setValue("username", username1.text())
    settings.setValue("version", version_combo.currentText())

def run_async(func):
    def wrapper(*args, **kwargs):
        QTimer.singleShot(0, lambda: func(*args, **kwargs))
    return wrapper

def start_game():
    selected_version = str(version_combo.currentText())
    username = str(username1.text())

    if " (" in selected_version:
        # Version has type info, e.g., "1.16.5 (Fabric)"
        version_id, version_type = selected_version.split(" (")
        version_type = version_type.rstrip(")")
    else:
        version_id = selected_version
        version_type = "Vanilla"

    if username != "":
        def package_get(pack):
            global package
            package.setText(str(pack))
            QCoreApplication.processEvents()

        def progress_update(progress):
            progressbar.setMaximum(100)
            progressbar.setValue(progress)
            QCoreApplication.processEvents()

        max_value = [100]  # set to 100 since we don't have progress info
        callback = {
            "setStatus": lambda text: package_get(text),
            "setProgress": lambda value: progress_update(value),
            "setMax": lambda value: maximum(max_value, value)
        }

        try:
            if not is_version_installed(minecraft_directory, version_id):
                # Устанавливаем версию, если она ещё не установлена
                minecraft_launcher_lib.install.install_minecraft_version(version_id, minecraft_directory, callback=callback)
        except Exception as e:
            show_error('download error', str(e))

        options = {
            'username': username,
            'jvmArguments': [f"-Xmx{memory_size}M"]
        }

        # Запуск Minecraft
        main.hide()
        try:
            subprocess.call(minecraft_launcher_lib.command.get_minecraft_command(version=version_id, minecraft_directory=minecraft_directory, options=options))
        except Exception as e:
            show_error('launch error', str(e))
        progressbar.reset()
        package.setText("waiting")
        main.show()
    else:
        show_error("Empty field", "Please, enter username first!")

start_b.clicked.connect(lambda: [start_game(), save_last_used()])

def open_folder():
    path = minecraft_directory
    path = os.path.realpath(path)
    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":  # macOS
        subprocess.Popen(["open", path])
    else:  # Linux
        subprocess.Popen(["xdg-open", path])

folder_b.clicked.connect(open_folder)

# Load settings and load versions accordingly
memory_size, show_alpha, show_beta, show_snapshots, show_installed_only = load_settings()
load_versions(show_alpha, show_beta, show_snapshots, show_installed_only)

sys.exit(app.exec())
