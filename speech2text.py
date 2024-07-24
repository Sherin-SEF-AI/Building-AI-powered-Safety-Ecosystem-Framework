import sys
import threading
import speech_recognition as sr
from PyQt5.QtWidgets import (QApplication, QVBoxLayout, QWidget, QPushButton, QTextEdit, QLabel,
                             QHBoxLayout, QFileDialog, QStatusBar, QMainWindow, QComboBox,
                             QDialog, QFormLayout, QCheckBox, QGroupBox, QSlider, QFontDialog, QAction, QMenu, QMenuBar)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from gtts import gTTS
import os
from translate import Translator

class HelpDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Help")
        layout = QFormLayout()
        self.help_text = QLabel(
            "Instructions:\n\n"
            "1. **Start Transcription**: Click the 'Start' button to begin listening and transcribing speech.\n"
            "2. **Stop Transcription**: Click the 'Stop' button to stop listening.\n"
            "3. **Clear Text**: Click 'Clear' to remove all transcribed text.\n"
            "4. **Save Text**: Click 'Save' to save the transcribed text to a file.\n"
            "5. **Play Audio**: Click 'Play Audio' to play the transcribed text as audio.\n"
            "6. **Export History**: Click 'Export History' to save the transcription history to a file.\n"
            "7. **Open Audio File**: Click 'Open Audio File' to load an audio file for transcription.\n"
            "8. **Font Settings**: Click 'Font Settings' to change the font of the transcribed text.\n"
            "9. **Enable Voice Commands**: Check the box to enable voice commands (functionality not implemented yet).\n"
            "10. **Translate Text**: Click 'Translate Text' to translate the transcribed text.\n",
            self
        )
        layout.addWidget(self.help_text)
        self.setLayout(layout)

class SpeechToTextApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.is_listening = False
        self.listen_thread = None
        self.transcription_history = []
        self.languages = {
            "English": "en",
            "Spanish": "es",
            "French": "fr",
            "German": "de",
            "Chinese": "zh"
        }
        self.selected_language = "en"
        self.translator = Translator(to_lang=self.selected_language)
        self.microphone_sensitivity = 1.0
        self.voice_commands_enabled = False
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Speech to Text')
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.label = QLabel('Real-time Speech Transcription', self)
        self.label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.label)

        self.language_label = QLabel('Select Language:', self)
        self.layout.addWidget(self.language_label)

        self.language_combo = QComboBox(self)
        self.language_combo.addItems(self.languages.keys())
        self.language_combo.currentIndexChanged.connect(self.change_language)
        self.layout.addWidget(self.language_combo)

        self.text_edit = QTextEdit(self)
        self.text_edit.setFont(QFont('Arial', 12))
        self.layout.addWidget(self.text_edit)

        self.text_formatting_group = QGroupBox("Text Formatting", self)
        formatting_layout = QHBoxLayout()

        self.bold_button = QPushButton("Bold", self)
        self.bold_button.clicked.connect(self.set_bold)
        formatting_layout.addWidget(self.bold_button)

        self.italic_button = QPushButton("Italic", self)
        self.italic_button.clicked.connect(self.set_italic)
        formatting_layout.addWidget(self.italic_button)

        self.underline_button = QPushButton("Underline", self)
        self.underline_button.clicked.connect(self.set_underline)
        formatting_layout.addWidget(self.underline_button)

        self.text_formatting_group.setLayout(formatting_layout)
        self.layout.addWidget(self.text_formatting_group)

        self.voice_commands_checkbox = QCheckBox("Enable Voice Commands", self)
        self.voice_commands_checkbox.stateChanged.connect(self.toggle_voice_commands)
        self.layout.addWidget(self.voice_commands_checkbox)

        self.translate_button = QPushButton('Translate Text', self)
        self.translate_button.clicked.connect(self.translate_text)
        self.layout.addWidget(self.translate_button)

        self.file_management_button = QPushButton('Open Audio File', self)
        self.file_management_button.clicked.connect(self.open_audio_file)
        self.layout.addWidget(self.file_management_button)

        self.button_layout = QHBoxLayout()

        self.start_button = QPushButton('Start', self)
        self.start_button.clicked.connect(self.start_transcription)
        self.button_layout.addWidget(self.start_button)

        self.stop_button = QPushButton('Stop', self)
        self.stop_button.clicked.connect(self.stop_transcription)
        self.button_layout.addWidget(self.stop_button)

        self.clear_button = QPushButton('Clear', self)
        self.clear_button.clicked.connect(self.clear_text)
        self.button_layout.addWidget(self.clear_button)

        self.save_button = QPushButton('Save', self)
        self.save_button.clicked.connect(self.save_text)
        self.button_layout.addWidget(self.save_button)

        self.play_button = QPushButton('Play Audio', self)
        self.play_button.clicked.connect(self.play_audio)
        self.button_layout.addWidget(self.play_button)

        self.export_button = QPushButton('Export History', self)
        self.export_button.clicked.connect(self.export_history)
        self.button_layout.addWidget(self.export_button)

        self.font_button = QPushButton('Font Settings', self)
        self.font_button.clicked.connect(self.open_font_settings)
        self.button_layout.addWidget(self.font_button)

        self.help_button = QPushButton('Help', self)
        self.help_button.clicked.connect(self.show_help)
        self.button_layout.addWidget(self.help_button)

        self.layout.addLayout(self.button_layout)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage('Status: Stopped')

        self.sensitivity_slider = QSlider(Qt.Horizontal, self)
        self.sensitivity_slider.setRange(1, 10)
        self.sensitivity_slider.setValue(10)
        self.sensitivity_slider.setTickInterval(1)
        self.sensitivity_slider.setTickPosition(QSlider.TicksBelow)
        self.sensitivity_slider.setToolTip('Adjust Microphone Sensitivity')
        self.sensitivity_slider.valueChanged.connect(self.adjust_sensitivity)
        self.layout.addWidget(self.sensitivity_slider)

        self.menu_bar = self.menuBar()
        self.file_menu = QMenu("File", self.menu_bar)
        self.help_menu = QMenu("Help", self.menu_bar)

        self.open_file_action = QAction('Open File', self)
        self.open_file_action.triggered.connect(self.open_audio_file)
        self.file_menu.addAction(self.open_file_action)

        self.save_file_action = QAction('Save Transcription', self)
        self.save_file_action.triggered.connect(self.save_text)
        self.file_menu.addAction(self.save_file_action)

        self.export_history_action = QAction('Export History', self)
        self.export_history_action.triggered.connect(self.export_history)
        self.file_menu.addAction(self.export_history_action)

        self.help_action = QAction('Help', self)
        self.help_action.triggered.connect(self.show_help)
        self.help_menu.addAction(self.help_action)

        self.menu_bar.addMenu(self.file_menu)
        self.menu_bar.addMenu(self.help_menu)

    def change_language(self, index):
        lang_name = self.language_combo.currentText()
        self.selected_language = self.languages[lang_name]
        self.translator = Translator(to_lang=self.selected_language)

    def start_transcription(self):
        if not self.is_listening:
            self.is_listening = True
            self.status_bar.showMessage("Status: Listening...")
            self.listen_thread = threading.Thread(target=self.listen, daemon=True)
            self.listen_thread.start()

    def stop_transcription(self):
        if self.is_listening:
            self.is_listening = False
            self.status_bar.showMessage("Status: Stopped")

    def listen(self):
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            while self.is_listening:
                try:
                    audio = self.recognizer.listen(source, timeout=10)  # Increased timeout
                    text = self.recognizer.recognize_google(audio, language=self.selected_language)
                    self.update_text_edit(text)
                except sr.UnknownValueError:
                    continue
                except sr.RequestError as e:
                    self.status_bar.showMessage(f"Error: {e}")
                    break
                except sr.WaitTimeoutError:
                    self.status_bar.showMessage("Timeout: No speech detected.")

    def update_text_edit(self, text):
        self.text_edit.append(text)
        self.transcription_history.append(text)

    def clear_text(self):
        self.text_edit.clear()

    def save_text(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Text", "", "Text Files (*.txt)", options=options)
        if file_name:
            with open(file_name, 'w') as file:
                file.write(self.text_edit.toPlainText())

    def play_audio(self):
        text = self.text_edit.toPlainText()
        if text:
            tts = gTTS(text=text, lang=self.selected_language)
            audio_file = "temp_audio.mp3"
            tts.save(audio_file)
            os.system(f"start {audio_file}")

    def export_history(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Export History", "", "Text Files (*.txt)", options=options)
        if file_name:
            with open(file_name, 'w') as file:
                for entry in self.transcription_history:
                    file.write(entry + "\n")

    def open_audio_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Audio File", "", "Audio Files (*.wav *.mp3)", options=options)
        if file_name:
            self.transcribe_audio_file(file_name)

    def transcribe_audio_file(self, file_path):
        with sr.AudioFile(file_path) as source:
            audio = self.recognizer.record(source)
            try:
                text = self.recognizer.recognize_google(audio, language=self.selected_language)
                self.update_text_edit(text)
            except sr.UnknownValueError:
                self.status_bar.showMessage("Could not understand audio.")
            except sr.RequestError as e:
                self.status_bar.showMessage(f"Error: {e}")

    def open_font_settings(self):
        font, ok = QFontDialog.getFont()
        if ok:
            self.text_edit.setFont(font)

    def toggle_voice_commands(self, state):
        self.voice_commands_enabled = state == Qt.Checked
        if self.voice_commands_enabled:
            self.status_bar.showMessage("Voice commands enabled (functionality not implemented yet).")
        else:
            self.status_bar.showMessage("Voice commands disabled.")

    def translate_text(self):
        text = self.text_edit.toPlainText()
        if text:
            translated = self.translator.translate(text)
            self.text_edit.setPlainText(translated)

    def set_bold(self):
        font = self.text_edit.font()
        font.setBold(not font.bold())
        self.text_edit.setFont(font)

    def set_italic(self):
        font = self.text_edit.font()
        font.setItalic(not font.italic())
        self.text_edit.setFont(font)

    def set_underline(self):
        font = self.text_edit.font()
        font.setUnderline(not font.underline())
        self.text_edit.setFont(font)

    def adjust_sensitivity(self, value):
        self.microphone_sensitivity = value / 10.0
        self.status_bar.showMessage(f"Microphone Sensitivity: {self.microphone_sensitivity:.1f}")

    def show_help(self):
        self.help_dialog = HelpDialog()
        self.help_dialog.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SpeechToTextApp()
    window.show()
    sys.exit(app.exec_())

