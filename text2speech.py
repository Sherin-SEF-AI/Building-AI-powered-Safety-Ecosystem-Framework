import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QTextEdit, QFileDialog, QLabel)
from PyQt5.QtGui import QFont
from gtts import gTTS
import os
import platform

class TextToSpeechApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Text-to-Speech Application')
        self.setGeometry(100, 100, 600, 400)
        
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
        
        self.speak_button = QPushButton("Speak")
        self.speak_button.clicked.connect(self.speak_text)
        layout.addWidget(self.speak_button)
        
        self.save_button = QPushButton("Save Audio")
        self.save_button.clicked.connect(self.save_audio)
        layout.addWidget(self.save_button)
        
        self.status_label = QLabel()
        layout.addWidget(self.status_label)
    
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
                tts = gTTS(text=text, lang='en')
                audio_path = "output.mp3"
                tts.save(audio_path)
                
                # Play the audio based on the operating system
                if platform.system() == 'Windows':
                    os.system(f"start {audio_path}")
                elif platform.system() == 'Darwin':  # macOS
                    os.system(f"afplay {audio_path}")
                else:  # Linux
                    os.system(f"xdg-open {audio_path}")
                
                self.status_label.setText("Speaking...")
            except Exception as e:
                self.status_label.setText(f"Error: {e}")
    
    def save_audio(self):
        text = self.text_edit.toPlainText()
        if text:
            options = QFileDialog.Options()
            file_name, _ = QFileDialog.getSaveFileName(self, "Save Audio File", "", "MP3 Files (*.mp3)", options=options)
            if file_name:
                try:
                    tts = gTTS(text=text, lang='en')
                    tts.save(file_name)
                    self.status_label.setText("Audio saved successfully.")
                except Exception as e:
                    self.status_label.setText(f"Error: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = TextToSpeechApp()
    ex.show()
    sys.exit(app.exec_())

