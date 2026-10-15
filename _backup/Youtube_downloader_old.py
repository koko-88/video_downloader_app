import sys
from PySide6.QtGui import QMovie
from PySide6.QtWidgets import QLabel

import yt_dlp
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QFileDialog, QMessageBox, QComboBox, QHBoxLayout,
    QTextEdit, QProgressBar
)
from PySide6.QtCore import Qt, QThread, Signal




class YouTubeDownloader(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎬 YouTube Video Downloader")
        self.setFixedSize(550, 500)

        self.layout = QVBoxLayout(self)

        self.url_label = QLabel("Video URL:")
        self.url_input = QTextEdit()
        self.url_input.setPlaceholderText("Paste one or more YouTube links, each on a new line")
        self.url_input.setFixedHeight(80)

        self.path_label = QLabel("Download Folder:")
        self.path_input = QLineEdit()
        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.select_folder)

        path_layout = QHBoxLayout()
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(self.browse_button)

        self.res_label = QLabel("Resolution:")
        self.res_combo = QComboBox()
        self.res_combo.addItems(["360", "480", "720", "1080", "1440", "2160"])

        self.format_label = QLabel("Format:")
        self.format_combo = QComboBox()
        self.format_combo.addItems(["MP4", "MP3"])

        self.progress_bar = QProgressBar()
        self.progress_bar.setAlignment(Qt.AlignCenter)

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)

        self.download_btn = QPushButton("⬇ Start Download")
        self.download_btn.clicked.connect(self.start_download)
        self.loader = QLabel()
        self.loader_movie = QMovie("loader.gif")  # put path to an actual loading gif file here
        self.loader.setMovie(self.loader_movie)
        self.loader.hide()  # hide loader initially
        self.layout.addWidget(self.loader)

        # Add widgets to layout
        self.layout.addWidget(self.url_label)
        self.layout.addWidget(self.url_input)
        self.layout.addWidget(self.path_label)
        self.layout.addLayout(path_layout)
        self.layout.addWidget(self.res_label)
        self.layout.addWidget(self.res_combo)
        self.layout.addWidget(self.format_label)
        self.layout.addWidget(self.format_combo)
        self.layout.addWidget(self.progress_bar)
        self.layout.addWidget(QLabel("📄 Logs:"))
        self.layout.addWidget(self.log_box)
        self.layout.addWidget(self.download_btn)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Download Folder")
        if folder:
            self.path_input.setText(folder)

    def start_download(self):
        urls = self.url_input.toPlainText().strip().splitlines()
        urls = [u.strip() for u in urls if u.strip()]

        path = self.path_input.text().strip()
        resolution = self.res_combo.currentText()
        format_choice = self.format_combo.currentText()

        if not urls or not path:
            QMessageBox.warning(self, "Input Error", "Please fill in all fields.")
            return

        self.download_btn.setEnabled(False)
        self.loader.show()
        self.loader_movie.start()

        self.batch_queue = urls
        self.current_index = 0
        self.total_links = len(urls)
        self.path = path
        self.resolution = resolution
        self.format_choice = format_choice

        self.start_next_download()

    def update_log(self, message):
        self.log_box.append(message)
        if "✅ Download complete" in message or "❌ Error:" in message:
            self.download_btn.setEnabled(True)
            self.loader_movie.stop()
            self.loader.hide()

    def start_next_download(self):
        if self.current_index >= self.total_links:
            self.log_box.append("✅ All downloads finished.")
            self.download_btn.setEnabled(True)
            self.loader_movie.stop()
            self.loader.hide()
            return

        current_url = self.batch_queue[self.current_index]
        self.log_box.append(f"➡ Starting {self.current_index + 1}/{self.total_links}: {current_url}")
        self.thread = DownloaderThread(current_url, self.path, self.resolution, self.format_choice)
        self.thread.log_signal.connect(self.update_log)
        self.thread.progress_signal.connect(self.update_progress)
        self.thread.finished.connect(self.start_next_download)
        self.thread.start()

        self.current_index += 1

    def update_progress(self, value):
        self.progress_bar.setValue(value)


from PySide6.QtGui import QPalette, QColor

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, QColor(45, 45, 45))
    dark_palette.setColor(QPalette.WindowText, Qt.white)
    dark_palette.setColor(QPalette.Base, QColor(30, 30, 30))
    dark_palette.setColor(QPalette.AlternateBase, QColor(45, 45, 45))
    dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
    dark_palette.setColor(QPalette.ToolTipText, Qt.white)
    dark_palette.setColor(QPalette.Text, Qt.white)
    dark_palette.setColor(QPalette.Button, QColor(45, 45, 45))
    dark_palette.setColor(QPalette.ButtonText, Qt.white)
    dark_palette.setColor(QPalette.BrightText, Qt.red)
    dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.HighlightedText, Qt.black)

    app.setPalette(dark_palette)
    app.setStyle("Fusion")

    window = YouTubeDownloader()
    window.show()
    sys.exit(app.exec())
