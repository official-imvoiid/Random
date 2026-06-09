# Install Modules By: pip install PyQt6 PyQt6-WebEngine

# import Packages
import sys, os
from urllib.parse import urlparse
from PyQt6.QtCore import QUrl, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QColor, QPalette
from PyQt6.QtWidgets import(
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
    QWidget, QLineEdit, QPushButton, QLabel, QListWidget,
    QListWidgetItem, QTextEdit, QSplitter, QMessageBox,
    QStatusBar, QFrame)
from PyQt6.QtWebEngineWidgets import QWebEngineView

# Config
URL_LIST_FILE = os.path.join(os.path.dirname(__file__), "urls.txt")
DOWNLOAD_DIR  = os.path.expanduser("~/Downloads/GalleryDL")
HOME_URL      = "https://www.google.com"
    
# Background download worker (runs gallery-dl without freezing the UI)
class DownloadWorker(QThread):
    log_line = pyqtSignal(str) 
    done     = pyqtSignal(bool)
    
    def __init__(self, url_file: str, download_dir: str):
        super()._init()
        self.urls_file = url_file
        self.download_dir= download_dir


    def run(self):
        import subprocess
        try:
            proc = subprocess.Popen(
            [
                "gallery-dl"
                "--input-file", self.url_file,
                "-d",           self.download_dir,
                "sleep",        "l"     # be polite to servers
            ],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            for line in proc.stdout:
                self.log_line.emit(line.rstrip())
            proc.wait()
            self.done.emit(proc.returncode == 0)
        except FileNotFoundError:
            self.log_line.emit("❌ 'gallery-dl' not found. Install it: pip install gallery-dl")
            self.done.emit(False)
        except Exception as exc:
            self.log_line.emit(f"❌ Error: {exc}")
            self.done.emit(False)

class SimpleBrowser(QMainWindow):

    # Init
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gallery Browser")
        self.resize(1400, 860)
        self._worker: DownloadWorker | None = None

        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        if not os.path.exists(URL_LIST_FILE):
            open(URL_LIST_FILE, "w").close()

        self._build_ui()
        self._apply_dark_theme()
        self._refresh_list()

    # UI construction
    def _build_ui(self):
        # Web engine 
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl(HOME_URL))
        self.browser.urlChanged.connect(self._on_url_changed)
        self.browser.loadFinished.connect(self._on_load_finished)

        #  Navigation bar 
        self.btn_back    = QPushButton("◀")
        self.btn_forward = QPushButton("▶")
        self.btn_reload  = QPushButton("↺")
        self.url_bar     = QLineEdit(HOME_URL)
        self.btn_go      = QPushButton("Go")
        self.btn_add     = QPushButton("＋ Add to List")

        for btn in (self.btn_back, self.btn_forward, self.btn_reload):
            btn.setFixedWidth(36)

        self.btn_back.clicked.connect(self.browser.back)
        self.btn_forward.clicked.connect(self.browser.forward)
        self.btn_reload.clicked.connect(self.browser.reload)
        self.url_bar.returnPressed.connect(self._navigate)
        self.btn_go.clicked.connect(self._navigate)
        self.btn_add.clicked.connect(self._add_to_list)

        nav = QHBoxLayout()
        nav.setSpacing(4)
        nav.addWidget(self.btn_back)
        nav.addWidget(self.btn_forward)
        nav.addWidget(self.btn_reload)
        nav.addWidget(self.url_bar)
        nav.addWidget(self.btn_go)
        nav.addWidget(self.btn_add)

        nav_bar = QWidget()
        nav_bar.setLayout(nav)
        nav_bar.setFixedHeight(44)

        #  Right panel 
        self.lbl_count = QLabel("Queue (0)")
        self.lbl_count.setFont(QFont("Consolas", 10, QFont.Weight.Bold))

        self.list_widget = QListWidget()
        self.list_widget.setAlternatingRowColors(True)

        self.btn_remove = QPushButton("✕ Remove Selected")
        self.btn_clear  = QPushButton("🗑 Clear All")
        self.btn_dl     = QPushButton("⬇  Download All")

        btn_row = QHBoxLayout()
        btn_row.addWidget(self.btn_remove)
        btn_row.addWidget(self.btn_clear)

        self.lbl_log = QLabel("Download log")
        self.lbl_log.setFont(QFont("Consolas", 9))

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setFont(QFont("Consolas", 9))
        self.log_box.setFixedHeight(180)

        self.lbl_folder = QLabel(f"📁 {DOWNLOAD_DIR}")
        self.lbl_folder.setWordWrap(True)
        self.lbl_folder.setFont(QFont("Consolas", 8))

        side = QVBoxLayout()
        side.setSpacing(6)
        side.addWidget(self.lbl_count)
        side.addWidget(self.list_widget)
        side.addLayout(btn_row)
        side.addWidget(self.btn_dl)
        side.addWidget(self.lbl_log)
        side.addWidget(self.log_box)
        side.addWidget(self.lbl_folder)

        side_widget = QWidget()
        side_widget.setLayout(side)
        side_widget.setFixedWidth(340)

        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.VLine)

        # ── Content row ─────────────────────────────────────────
        content = QHBoxLayout()
        content.setSpacing(0)
        content.addWidget(self.browser, stretch=1)
        content.addWidget(divider)
        content.addWidget(side_widget)

        content_widget = QWidget()
        content_widget.setLayout(content)

        # ── Root layout ─────────────────────────────────────────
        root = QVBoxLayout()
        root.setContentsMargins(6, 6, 6, 6)
        root.setSpacing(4)
        root.addWidget(nav_bar)
        root.addWidget(content_widget, stretch=1)

        container = QWidget()
        container.setLayout(root)
        self.setCentralWidget(container)

        # ── Status bar ──────────────────────────────────────────
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("Ready")

        # ── Button signals ──────────────────────────────────────
        self.btn_remove.clicked.connect(self._remove_selected)
        self.btn_clear.clicked.connect(self._clear_list)
        self.btn_dl.clicked.connect(self._download_all)

    # ── Dark theme ────────────────────────────────────────────────────────────
    def _apply_dark_theme(self):
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background: #1a1a2e;
                color: #e0e0e0;
                font-family: 'Segoe UI', Consolas, monospace;
            }
            QLineEdit {
                background: #16213e;
                color: #e0e0e0;
                border: 1px solid #0f3460;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 13px;
            }
            QPushButton {
                background: #0f3460;
                color: #e0e0e0;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 12px;
            }
            QPushButton:hover  { background: #533483; }
            QPushButton:pressed{ background: #e94560; }

            /* Add-to-list button stands out */
            QPushButton#add_btn {
                background: #27ae60;
                font-weight: bold;
            }
            QPushButton#add_btn:hover   { background: #2ecc71; }
            QPushButton#add_btn:pressed { background: #1e8449; }

            /* Download button */
            QPushButton#dl_btn {
                background: #2980b9;
                font-weight: bold;
                font-size: 13px;
                padding: 10px;
            }
            QPushButton#dl_btn:hover   { background: #3498db; }
            QPushButton#dl_btn:disabled{ background: #555; color: #999; }

            QListWidget {
                background: #16213e;
                border: 1px solid #0f3460;
                border-radius: 4px;
                color: #c0c0c0;
                font-size: 11px;
            }
            QListWidget::item:selected {
                background: #533483;
                color: white;
            }
            QListWidget::item:alternate { background: #1a1a2e; }

            QTextEdit {
                background: #0d0d1a;
                color: #39ff14;
                border: 1px solid #0f3460;
                border-radius: 4px;
                font-size: 11px;
            }
            QStatusBar { background: #0f3460; color: #aaa; }
            QFrame[frameShape="5"] { color: #0f3460; }  /* VLine divider */
        """)

        self.btn_add.setObjectName("add_btn")
        self.btn_dl.setObjectName("dl_btn")
        # Re-apply after setObjectName so CSS picks up
        self.btn_add.setStyleSheet("""
            background: #27ae60; color: white; font-weight: bold;
            border-radius: 4px; padding: 6px 14px;
        """)
        self.btn_dl.setStyleSheet("""
            background: #2980b9; color: white; font-weight: bold;
            font-size: 13px; padding: 10px; border-radius: 4px;
        """)

    #  Navigation 
    def _navigate(self):
        url = self.url_bar.text().strip()
        if not url.startswith(("http://", "https://")):
            # Treat as search query if it has spaces or no dot
            if " " in url or "." not in url:
                url = f"https://www.google.com/search?q={url.replace(' ', '+')}"
            else:
                url = "https://" + url
        self.browser.setUrl(QUrl(url))

    def _on_url_changed(self, q: QUrl):
        self.url_bar.setText(q.toString())

    def _on_load_finished(self, ok: bool):
        title = self.browser.page().title()
        self.status.showMessage(title if ok else "⚠ Page failed to load")

    #  URL list helpers 
    def _read_urls(self) -> list[str]:
        with open(URL_LIST_FILE, "r") as f:
            return [line.strip() for line in f if line.strip()]

    def _write_urls(self, urls: list[str]):
        with open(URL_LIST_FILE, "w") as f:
            f.write("\n".join(urls) + ("\n" if urls else ""))

    def _refresh_list(self):
        urls = self._read_urls()
        self.list_widget.clear()
        for url in urls:
            domain = urlparse(url).netloc or url
            item   = QListWidgetItem(f"🔗 {domain}")
            item.setToolTip(url)           # full URL on hover
            item.setData(256, url)         # store full URL in UserRole
            self.list_widget.addItem(item)
        self.lbl_count.setText(f"Queue ({len(urls)})")

    #  Button actions 
    def _add_to_list(self):
        url = self.browser.url().toString()
        if url in ("about:blank", ""):
            return

        existing = self._read_urls()
        if url in existing:
            self.status.showMessage("Already in list ✓")
            return

        existing.append(url)
        self._write_urls(existing)
        self._refresh_list()

        domain = urlparse(url).netloc
        self.status.showMessage(f"Added → {domain}")
        self._log(f"✚ Added: {url}")

    def _remove_selected(self):
        selected = self.list_widget.currentItem()
        if not selected:
            return
        url  = selected.data(256)
        urls = [u for u in self._read_urls() if u != url]
        self._write_urls(urls)
        self._refresh_list()
        self.status.showMessage("Removed from list")

    def _clear_list(self):
        reply = QMessageBox.question(
            self, "Clear list?",
            "Remove all queued URLs?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._write_urls([])
            self._refresh_list()
            self.status.showMessage("List cleared")

    #  gallery-dl download 
    def _download_all(self):
        if not self._read_urls():
            QMessageBox.information(self, "Empty", "Add some URLs first!")
            return

        self.btn_dl.setEnabled(False)
        self.btn_dl.setText("⏳ Downloading …")
        self.log_box.clear()
        self._log(f"▶ gallery-dl starting …\n📁 Output: {DOWNLOAD_DIR}\n")

        self._worker = DownloadWorker(URL_LIST_FILE, DOWNLOAD_DIR)
        self._worker.log_line.connect(self._log)
        self._worker.done.connect(self._on_download_done)
        self._worker.start()

    def _on_download_done(self, success: bool):
        self.btn_dl.setEnabled(True)
        self.btn_dl.setText("⬇  Download All")
        if success:
            self._log(f"\n✅ Done!  Files saved to:\n   {DOWNLOAD_DIR}")
            self.status.showMessage("Download complete ✓")
        else:
            self._log("\n❌ Finished with errors — check log above.")
            self.status.showMessage("Download finished with errors")

    def _log(self, text: str):
        self.log_box.append(text)
        sb = self.log_box.verticalScrollBar()
        sb.setValue(sb.maximum())


#  Entry point 
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = SimpleBrowser()
    window.show()
    sys.exit(app.exec())