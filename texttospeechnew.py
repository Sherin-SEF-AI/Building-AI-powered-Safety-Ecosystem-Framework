import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QTextEdit, QFileDialog, QLabel, QSlider, QComboBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl
from gtts import gTTS

class TextToSpeechApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Text-to-Speech Application')
        self.setGeometry(100, 100, 800, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        self.text_edit = QTextEdit()
        self.text_edit.setFont(QFont('Arial', 12))
        layout.addWidget(self.text_edit)
        
        self.upload_button = QPushButton("Upload Text File")
        self.upload_button.clicked.connect(self.upload_text_file)
        layout.addWidget(self.upload_button)
        
        # Voice selection
        self.voice_combo = QComboBox()
        self.voice_combo.addItems([
            "English", "Spanish", "French", "German", "Chinese", 
            "Hindi", "Italian", "Japanese", "Korean", "Portuguese"
        ])  # Example languages
        layout.addWidget(QLabel("Select Voice:"))
        layout.addWidget(self.voice_combo)
        
        # Volume control
        self.volume_slider = QSlider()
        self.volume_slider.setOrientation(Qt.Horizontal)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(100)
        self.volume_slider.setTickInterval(10)
        self.volume_slider.setTickPosition(QSlider.TicksBelow)
        self.volume_slider.setSingleStep(10)
        layout.addWidget(QLabel("Volume:"))
        layout.addWidget(self.volume_slider)
        
        # Speech rate control
        self.rate_slider = QSlider()
        self.rate_slider.setOrientation(Qt.Horizontal)
        self.rate_slider.setMinimum(50)
        self.rate_slider.setMaximum(200)
        self.rate_slider.setValue(100)
        self.rate_slider.setTickInterval(10)
        self.rate_slider.setTickPosition(QSlider.TicksBelow)
        self.rate_slider.setSingleStep(10)
        layout.addWidget(QLabel("Speech Rate:"))
        layout.addWidget(self.rate_slider)
        
        self.speak_button = QPushButton("Speak")
        self.speak_button.clicked.connect(self.speak_text)
        layout.addWidget(self.speak_button)
        
        self.save_button = QPushButton("Save Audio")
        self.save_button.clicked.connect(self.save_audio)
        layout.addWidget(self.save_button)
        
        self.status_label = QLabel()
        layout.addWidget(self.status_label)

        # Add media player widget
        self.media_player = QMediaPlayer()
        layout.addWidget(QLabel("Audio Playback:"))
        
        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self.play_audio)
        layout.addWidget(self.play_button)
        
        self.pause_button = QPushButton("Pause")
        self.pause_button.clicked.connect(self.pause_audio)
        layout.addWidget(self.pause_button)
        
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_audio)
        layout.addWidget(self.stop_button)
    
    def upload_text_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Text File", "", "Text Files (*.txt);;All Files (*)", options=options)
        if file_name:
            try:
                with open(file_name, 'r') as file:
                    text = file.read()
                    self.text_edit.setPlainText(text)
                    self.status_label.setText(f"Loaded file: {file_name}")
            except Exception as e:
                self.status_label.setText(f"Error loading file: {e}")
    
    def speak_text(self):
        text = self.text_edit.toPlainText()
        if text:
            try:
                language = self.get_language_code(self.voice_combo.currentText())
                if language is None:
                    self.status_label.setText("Selected language is not supported.")
                    return
                
                self.audio_path = os.path.abspath("output.mp3")
                tts = gTTS(text=text, lang=language)
                tts.save(self.audio_path)
                
                self.status_label.setText("Audio saved. Click 'Play' to listen.")
                self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(self.audio_path)))
            except Exception as e:
                self.status_label.setText(f"Error: {e}")
    
    def save_audio(self):
        text = self.text_edit.toPlainText()
        if text:
            options = QFileDialog.Options()
            file_name, _ = QFileDialog.getSaveFileName(self, "Save Audio File", "", "MP3 Files (*.mp3)", options=options)
            if file_name:
                try:
                    language = self.get_language_code(self.voice_combo.currentText())
                    if language is None:
                        self.status_label.setText("Selected language is not supported.")
                        return
                    
                    tts = gTTS(text=text, lang=language)
                    tts.save(file_name)
                    self.status_label.setText("Audio saved successfully.")
                except Exception as e:
                    self.status_label.setText(f"Error: {e}")

    def play_audio(self):
        if self.media_player.media() is not None:
            self.media_player.play()
            self.status_label.setText("Playing audio...")
        else:
            self.status_label.setText("No audio file to play.")
    
    def pause_audio(self):
        if self.media_player.media() is not None:
            self.media_player.pause()
            self.status_label.setText("Audio paused.")
        else:
            self.status_label.setText("No audio file to pause.")
    
    def stop_audio(self):
        if self.media_player.media() is not None:
            self.media_player.stop()
            self.status_label.setText("Audio stopped.")
        else:
            self.status_label.setText("No audio file to stop.")
    
    def get_language_code(self, language_name):
        language_map = {
            "English": "en",
            "Spanish": "es",
            "French": "fr",
            "German": "de",
            "Chinese": "zh",
            "Hindi": "hi",
            "Italian": "it",
            "Japanese": "ja",
            "Korean": "ko",
            "Portuguese": "pt"
        }
        return language_map.get(language_name)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = TextToSpeechApp()
    ex.show()
    sys.exit(app.exec_())

