# Install Modules By: pip install -U gallery-dl PyQt6 PyQt6-WebEngine

import sys, os
from urllib.parse import urlparse
from PyQt6.QtCore import QUrl, QThread, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
    QWidget, QLineEdit, QPushButton, QLabel, QListWidget,
    QListWidgetItem, QTextEdit, QMessageBox,
    QStatusBar, QFrame, QTabWidget)
from PyQt6.QtWebEngineWidgets import QWebEngineView

# ── Config ────────────────────────────────────────────────────────────────────
URL_LIST_FILE = os.path.join(os.path.dirname(__file__), "urls.txt")
DOWNLOAD_DIR  = os.path.expanduser("~/Downloads/GalleryDL")
HOME_URL      = "https://www.google.com"


# ── Download worker ───────────────────────────────────────────────────────────
class DownloadWorker(QThread):
    log_line = pyqtSignal(str)
    done     = pyqtSignal(bool)

    def __init__(self, url_file: str, download_dir: str):
        super().__init__()                  # FIX 1: was super()._init()  ← crash cause
        self.urls_file    = url_file        # FIX 3: keep name consistent
        self.download_dir = download_dir

    def run(self):
        import subprocess
        try:
            proc = subprocess.Popen(
                [
                    "gallery-dl",                    # FIX 2: missing comma caused string concat bug
                    "--input-file", self.urls_file,  # FIX 3: was self.url_file (AttributeError)
                    "-d",           self.download_dir,
                    "--sleep",      "1",             # FIX 4: was "sleep","l" → wrong flag + typo
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


# ── Custom WebEngineView with tab support + right-click menu ──────────────────
class BrowserView(QWebEngineView):
    """WebView that supports right-click 'Open in New Tab' and target=_blank links."""

    def __init__(self, main_win: "SimpleBrowser", parent=None):
        super().__init__(parent)
        self._main_win    = main_win
        self._hovered_url = ""
        # Track whatever link the cursor is hovering over
        self.page().linkHovered.connect(self._on_link_hover)

    def _on_link_hover(self, url: str):
        self._hovered_url = url

    # Called by Qt when a page does window.open() or has target="_blank"
    def createWindow(self, win_type):
        return self._main_win._new_tab()

    # Right-click menu
    def contextMenuEvent(self, event):
        menu = self.createStandardContextMenu()
        if self._hovered_url:
            menu.addSeparator()
            act = menu.addAction("🔗  Open Link in New Tab")
            url = self._hovered_url          # capture for lambda
            act.triggered.connect(lambda: self._main_win._new_tab(url))
        menu.exec(event.globalPos())


# ── Main window ───────────────────────────────────────────────────────────────
class SimpleBrowser(QMainWindow):

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

    # ── Tab factory ───────────────────────────────────────────────────────────
    def _new_tab(self, url: str = HOME_URL) -> BrowserView:
        view = BrowserView(self)
        view.setUrl(QUrl(url))
        view.urlChanged.connect(self._on_url_changed)
        view.loadFinished.connect(self._on_load_finished)
        view.titleChanged.connect(self._on_title_changed)

        idx = self.tabs.addTab(view, "New Tab")
        self.tabs.setCurrentIndex(idx)
        return view

    def _close_tab(self, idx: int):
        if self.tabs.count() > 1:
            widget = self.tabs.widget(idx)
            self.tabs.removeTab(idx)
            if widget:
                widget.deleteLater()        # free memory
        else:
            # Keep at least one tab; just go home
            self.current_browser().setUrl(QUrl(HOME_URL))

    def current_browser(self) -> BrowserView | None:
        return self.tabs.currentWidget()

    # ── UI construction ───────────────────────────────────────────────────────
    def _build_ui(self):

        # ── Tab widget ───────────────────────────────────────────────────────
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self._close_tab)
        # NOTE: currentChanged connected AFTER url_bar is created below
        self._new_tab(HOME_URL)             # open first tab

        # ── Navigation bar ───────────────────────────────────────────────────
        self.btn_back    = QPushButton("◀")
        self.btn_forward = QPushButton("▶")
        self.btn_reload  = QPushButton("↺")
        self.url_bar     = QLineEdit(HOME_URL)
        self.tabs.currentChanged.connect(self._on_tab_changed)  # safe: url_bar now exists
        self.btn_go      = QPushButton("Go")
        self.btn_new_tab = QPushButton("＋")
        self.btn_add     = QPushButton("＋ Add to List")

        for btn in (self.btn_back, self.btn_forward, self.btn_reload, self.btn_new_tab):
            btn.setFixedWidth(36)

        self.btn_back.setToolTip("Back")
        self.btn_forward.setToolTip("Forward")
        self.btn_reload.setToolTip("Reload")
        self.btn_new_tab.setToolTip("Open New Tab")

        self.btn_back.clicked.connect(lambda: self.current_browser().back())
        self.btn_forward.clicked.connect(lambda: self.current_browser().forward())
        self.btn_reload.clicked.connect(lambda: self.current_browser().reload())
        self.url_bar.returnPressed.connect(self._navigate)
        self.btn_go.clicked.connect(self._navigate)
        self.btn_new_tab.clicked.connect(lambda: self._new_tab())
        self.btn_add.clicked.connect(self._add_to_list)

        nav = QHBoxLayout()
        nav.setSpacing(4)
        for w in (self.btn_back, self.btn_forward, self.btn_reload,
                  self.url_bar, self.btn_go, self.btn_new_tab, self.btn_add):
            nav.addWidget(w)

        nav_bar = QWidget()
        nav_bar.setLayout(nav)
        nav_bar.setFixedHeight(44)

        # ── Right panel ──────────────────────────────────────────────────────
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

        # ── Layout assembly ──────────────────────────────────────────────────
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.VLine)

        content = QHBoxLayout()
        content.setSpacing(0)
        content.addWidget(self.tabs, stretch=1)
        content.addWidget(divider)
        content.addWidget(side_widget)

        content_widget = QWidget()
        content_widget.setLayout(content)

        root = QVBoxLayout()
        root.setContentsMargins(6, 6, 6, 6)
        root.setSpacing(4)
        root.addWidget(nav_bar)
        root.addWidget(content_widget, stretch=1)

        container = QWidget()
        container.setLayout(root)
        self.setCentralWidget(container)

        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("Ready")

        self.btn_remove.clicked.connect(self._remove_selected)
        self.btn_clear.clicked.connect(self._clear_list)
        self.btn_dl.clicked.connect(self._download_all)

    # ── Tab events ────────────────────────────────────────────────────────────
    def _on_tab_changed(self, idx: int):
        view = self.tabs.widget(idx)
        if view:
            self.url_bar.setText(view.url().toString())

    def _on_title_changed(self, title: str):
        view = self.sender()
        idx  = self.tabs.indexOf(view)
        if idx >= 0:
            label = (title[:16] + "…") if len(title) > 18 else title
            self.tabs.setTabText(idx, label or "New Tab")

    # ── Navigation ────────────────────────────────────────────────────────────
    def _navigate(self):
        url = self.url_bar.text().strip()
        if not url.startswith(("http://", "https://")):
            if " " in url or "." not in url:
                url = f"https://www.google.com/search?q={url.replace(' ', '+')}"
            else:
                url = "https://" + url
        b = self.current_browser()
        if b:
            b.setUrl(QUrl(url))

    def _on_url_changed(self, q: QUrl):
        if self.sender() is self.current_browser():
            self.url_bar.setText(q.toString())

    def _on_load_finished(self, ok: bool):
        if self.sender() is self.current_browser():
            title = self.current_browser().page().title()
            self.status.showMessage(title if ok else "⚠ Page failed to load")

    # ── URL list helpers ──────────────────────────────────────────────────────
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
            item.setToolTip(url)
            item.setData(256, url)
            self.list_widget.addItem(item)
        self.lbl_count.setText(f"Queue ({len(urls)})")

    # ── Button actions ────────────────────────────────────────────────────────
    def _add_to_list(self):
        b = self.current_browser()
        if not b:
            return
        url = b.url().toString()
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
            self, "Clear list?", "Remove all queued URLs?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._write_urls([])
            self._refresh_list()
            self.status.showMessage("List cleared")

    # ── gallery-dl download ───────────────────────────────────────────────────
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
            QPushButton:hover   { background: #533483; }
            QPushButton:pressed { background: #e94560; }
            QPushButton:disabled{ background: #555; color: #999; }

            /* Tab bar */
            QTabWidget::pane  { border: 1px solid #0f3460; background: #1a1a2e; }
            QTabBar::tab {
                background: #0f3460; color: #aaa;
                padding: 5px 12px;
                border-radius: 4px 4px 0 0;
                margin-right: 2px; font-size: 11px;
            }
            QTabBar::tab:selected { background: #533483; color: #fff; }
            QTabBar::tab:hover    { background: #1e4a8a; }
            QTabBar::close-button {
                subcontrol-position: right;
                margin: 2px;
            }

            QListWidget {
                background: #16213e;
                border: 1px solid #0f3460;
                border-radius: 4px;
                color: #c0c0c0;
                font-size: 11px;
            }
            QListWidget::item:selected  { background: #533483; color: white; }
            QListWidget::item:alternate { background: #1a1a2e; }

            QTextEdit {
                background: #0d0d1a;
                color: #39ff14;
                border: 1px solid #0f3460;
                border-radius: 4px;
                font-size: 11px;
            }

            QMenu {
                background: #16213e;
                color: #e0e0e0;
                border: 1px solid #0f3460;
            }
            QMenu::item:selected { background: #533483; }
            QMenu::separator { background: #0f3460; height: 1px; }

            QStatusBar { background: #0f3460; color: #aaa; }
            QFrame[frameShape="5"] { color: #0f3460; }
        """)

        self.btn_add.setStyleSheet("""
            background: #27ae60; color: white; font-weight: bold;
            border-radius: 4px; padding: 6px 14px;
        """)
        self.btn_dl.setStyleSheet("""
            background: #2980b9; color: white; font-weight: bold;
            font-size: 13px; padding: 10px; border-radius: 4px;
        """)


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = SimpleBrowser()
    window.show()
    sys.exit(app.exec())
