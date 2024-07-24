import tkinter as tk
from tkinter import filedialog, messagebox
import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import json

class AudioAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Analyzer")
        self.create_widgets()
        self.load_settings()

    def create_widgets(self):
        # Load Audio Button
        self.load_button = tk.Button(self.root, text="Load MP3 File", command=self.load_audio)
        self.load_button.pack(pady=10)

        # Plot Options
        self.plot_option = tk.StringVar(value="Waveform")
        self.plot_menu = tk.OptionMenu(self.root, self.plot_option, "Waveform", "Spectrogram", command=self.update_plot)
        self.plot_menu.pack(pady=10)

        # Generate Report Button
        self.report_button = tk.Button(self.root, text="Generate Report", command=self.generate_report, state=tk.DISABLED)
        self.report_button.pack(pady=10)

        # Display Audio Information
        self.info_label = tk.Label(self.root, text="Audio information will be displayed here")
        self.info_label.pack(pady=10)

        # Plot Area
        self.plot_frame = tk.Frame(self.root)
        self.plot_frame.pack(fill=tk.BOTH, expand=True)

    def load_audio(self):
        file_path = filedialog.askopenfilename(filetypes=[("MP3 Files", "*.mp3")])
        if file_path:
            try:
                self.audio, self.sr = librosa.load(file_path, sr=None)
                self.display_audio_info()
                self.update_plot()
                self.report_button.config(state=tk.NORMAL)
                self.last_file = file_path
                self.save_settings()
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")

    def display_audio_info(self):
        duration = librosa.get_duration(y=self.audio, sr=self.sr)
        zero_crossings = librosa.feature.zero_crossing_rate(self.audio).mean()
        rmse = librosa.feature.rms(y=self.audio).mean()
        spectral_centroid = librosa.feature.spectral_centroid(y=self.audio, sr=self.sr).mean()
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=self.audio, sr=self.sr).mean()
        mfccs = np.mean(librosa.feature.mfcc(y=self.audio, sr=self.sr, n_mfcc=13), axis=1)
        chroma = np.mean(librosa.feature.chroma_stft(y=self.audio, sr=self.sr), axis=1)

        info_text = (
            f"Sample Rate: {self.sr}\n"
            f"Duration: {duration:.2f} seconds\n"
            f"Zero-Crossing Rate: {zero_crossings:.2f}\n"
            f"Root Mean Square Energy: {rmse:.2f}\n"
            f"Spectral Centroid: {spectral_centroid:.2f}\n"
            f"Spectral Bandwidth: {spectral_bandwidth:.2f}\n"
            f"MFCCs: {', '.join(f'{c:.2f}' for c in mfccs)}\n"
            f"Chroma Features: {', '.join(f'{c:.2f}' for c in chroma)}"
        )
        self.info_label.config(text=info_text)

    def update_plot(self, *args):
        if hasattr(self, 'audio'):
            self.clear_plot()
            if self.plot_option.get() == "Waveform":
                self.plot_waveform()
            elif self.plot_option.get() == "Spectrogram":
                self.plot_spectrogram()

    def plot_waveform(self):
        fig, ax = plt.subplots(figsize=(8, 4), dpi=100)
        time = np.linspace(0, len(self.audio) / self.sr, num=len(self.audio))
        ax.plot(time, self.audio)
        ax.set_title("Waveform")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Amplitude")
        self.embed_plot(fig)

    def plot_spectrogram(self):
        fig, ax = plt.subplots(figsize=(8, 4), dpi=100)
        S_db = librosa.power_to_db(librosa.feature.melspectrogram(y=self.audio, sr=self.sr), ref=np.max)
        img = librosa.display.specshow(S_db, sr=self.sr, x_axis='time', y_axis='mel', ax=ax)
        ax.set_title("Spectrogram")
        ax.label_outer()
        self.embed_plot(fig)

    def clear_plot(self):
        for widget in self.plot_frame.winfo_children():
            widget.destroy()

    def embed_plot(self, fig):
        self.canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def generate_report(self):
        if hasattr(self, 'audio') and hasattr(self, 'sr'):
            try:
                duration = librosa.get_duration(y=self.audio, sr=self.sr)
                zero_crossings = librosa.feature.zero_crossing_rate(self.audio).mean()
                rmse = librosa.feature.rms(y=self.audio).mean()
                spectral_centroid = librosa.feature.spectral_centroid(y=self.audio, sr=self.sr).mean()
                spectral_bandwidth = librosa.feature.spectral_bandwidth(y=self.audio, sr=self.sr).mean()
                mfccs = np.mean(librosa.feature.mfcc(y=self.audio, sr=self.sr, n_mfcc=13), axis=1)
                chroma = np.mean(librosa.feature.chroma_stft(y=self.audio, sr=self.sr), axis=1)

                report_text = (
                    f"Audio Analysis Report\n"
                    f"====================\n\n"
                    f"Sample Rate: {self.sr}\n"
                    f"Duration: {duration:.2f} seconds\n"
                    f"Zero-Crossing Rate: {zero_crossings:.2f}\n"
                    f"Root Mean Square Energy: {rmse:.2f}\n"
                    f"Spectral Centroid: {spectral_centroid:.2f}\n"
                    f"Spectral Bandwidth: {spectral_bandwidth:.2f}\n"
                    f"MFCCs: {', '.join(f'{c:.2f}' for c in mfccs)}\n"
                    f"Chroma Features: {', '.join(f'{c:.2f}' for c in chroma)}\n\n"
                    f"Additional details and analysis can be added here."
                )

                file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                       filetypes=[("Text Files", "*.txt")],
                                                       initialfile="audio_analysis_report.txt")
                if file_path:
                    with open(file_path, 'w') as file:
                        file.write(report_text)
                    messagebox.showinfo("Report Generated", f"Report saved to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred while generating the report: {e}")
        else:
            messagebox.showwarning("No Audio", "Please load an audio file first.")

    def save_settings(self):
        settings = {
            'last_file': self.last_file if hasattr(self, 'last_file') else ''
        }
        with open('settings.json', 'w') as f:
            json.dump(settings, f)

    def load_settings(self):
        try:
            with open('settings.json', 'r') as f:
                settings = json.load(f)
                if 'last_file' in settings:
                    self.last_file = settings['last_file']
        except FileNotFoundError:
            pass

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioAnalyzerApp(root)
    root.mainloop()

