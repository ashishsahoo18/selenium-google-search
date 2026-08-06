"""AI Desktop Search Assistant application entry point."""
from __future__ import annotations

import logging
import os
import threading
from datetime import datetime
from pathlib import Path
import customtkinter as ctk
from PIL import Image

from automation.browser import BrowserRunner
from config import APP_NAME, DATABASE_PATH, EXPORTS_DIR, SCREENSHOTS_DIR
from database.repository import Repository
from search.engines import ENGINES
from services.ai import analyze_screenshot, improve_query
from services.exporter import export_history
from services.ocr import extract_text
from services.voice import listen
from services.notifications import notify
from utils.logging_setup import configure_logging

LOGGER = logging.getLogger(__name__)
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class SearchAssistant(ctk.CTk):
    """Professional desktop UI for search automation."""

    def __init__(self) -> None:
        super().__init__()
        configure_logging(); self.repo = Repository(DATABASE_PATH); self.last_screenshot: Path | None = None
        self.title(APP_NAME); self.geometry(self.repo.get_setting("window_size", "1180x720")); self.minsize(960, 620)
        self.grid_columnconfigure(1, weight=1); self.grid_rowconfigure(0, weight=1)
        self._build_sidebar(); self.content = ctk.CTkFrame(self, corner_radius=0); self.content.grid(row=0, column=1, sticky="nsew")
        self.show_page("Search")
        self.protocol("WM_DELETE_WINDOW", self._close)

    def _build_sidebar(self) -> None:
        sidebar = ctk.CTkFrame(self, width=205, corner_radius=0); sidebar.grid(row=0, column=0, sticky="ns"); sidebar.grid_propagate(False)
        ctk.CTkLabel(sidebar, text="AI SEARCH", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(30, 22))
        for name in ("Search", "History", "Gallery", "Analytics", "Bookmarks", "Settings", "About"):
            ctk.CTkButton(sidebar, text=name, anchor="w", fg_color="transparent", command=lambda n=name: self.show_page(n)).pack(fill="x", padx=14, pady=4)
        ctk.CTkOptionMenu(sidebar, values=["System", "Dark", "Light"], command=ctk.set_appearance_mode).pack(side="bottom", padx=14, pady=22, fill="x")

    def _clear(self) -> None:
        for child in self.content.winfo_children(): child.destroy()

    def show_page(self, page: str) -> None:
        self._clear(); getattr(self, f"_page_{page.lower()}")()

    def _page_search(self) -> None:
        frame = ctk.CTkFrame(self.content); frame.pack(expand=True, fill="both", padx=35, pady=30)
        ctk.CTkLabel(frame, text="Search the web intelligently", font=ctk.CTkFont(size=28, weight="bold")).pack(anchor="w", padx=26, pady=(26, 5))
        self.query = ctk.CTkEntry(frame, placeholder_text="What would you like to find?", height=44, font=ctk.CTkFont(size=16)); self.query.pack(fill="x", padx=26, pady=18); self.query.bind("<Return>", lambda _: self.run_search())
        options = ctk.CTkFrame(frame, fg_color="transparent"); options.pack(fill="x", padx=26)
        self.engine = ctk.CTkOptionMenu(options, values=list(ENGINES)); self.engine.pack(side="left", padx=(0, 10))
        self.browser = ctk.CTkOptionMenu(options, values=["Chrome", "Firefox", "Edge", "Brave"]); self.browser.pack(side="left", padx=10)
        self.headless = ctk.CTkCheckBox(options, text="Headless"); self.headless.pack(side="left", padx=15)
        self.incognito = ctk.CTkCheckBox(options, text="Private"); self.incognito.pack(side="left", padx=8)
        controls = ctk.CTkFrame(frame, fg_color="transparent"); controls.pack(fill="x", padx=26, pady=20)
        ctk.CTkButton(controls, text="Search", height=42, command=self.run_search).pack(side="left")
        ctk.CTkButton(controls, text="🎙 Voice", fg_color="transparent", border_width=1, command=self.voice_search).pack(side="left", padx=12)
        ctk.CTkButton(controls, text="☆ Bookmark", fg_color="transparent", border_width=1, command=self.bookmark_current).pack(side="left")
        self.status = ctk.CTkLabel(frame, text="Ready", text_color="#62c370"); self.status.pack(anchor="w", padx=26)
        self.progress = ctk.CTkProgressBar(frame); self.progress.pack(fill="x", padx=26, pady=10); self.progress.set(0)
        self.preview = ctk.CTkLabel(frame, text="Screenshot preview will appear here", height=260); self.preview.pack(expand=True, fill="both", padx=26, pady=(5, 26))

    def _screenshot_path(self, query: str) -> Path:
        now = datetime.now(); folder = SCREENSHOTS_DIR / str(now.year) / now.strftime("%B"); folder.mkdir(parents=True, exist_ok=True)
        safe = "".join(c if c.isalnum() else "_" for c in query)[:45]
        return folder / f"{now:%Y%m%d_%H%M%S}_{safe}.png"

    def run_search(self) -> None:
        query = self.query.get().strip()
        if query: threading.Thread(target=self._search_worker, args=(query,), daemon=True).start()

    def _search_worker(self, original: str) -> None:
        runner = None
        try:
            self.after(0, lambda: (self.status.configure(text="Improving query…", text_color="#f5b642"), self.progress.set(.2)))
            improved = improve_query(original); shot = self._screenshot_path(improved)
            runner = BrowserRunner(self.browser.get(), self.headless.get() == 1, self.incognito.get() == 1)
            self.after(0, lambda: (self.status.configure(text="Searching…"), self.progress.set(.45)))
            url = runner.search(self.engine.get(), improved, shot); self.last_screenshot = shot
            self.repo.add_history(browser=self.browser.get(), engine=self.engine.get(), original_query=original, improved_query=improved, screenshot=str(shot), current_url=url, status="Completed")
            self.after(0, lambda: self._finish_search(improved, shot, "Search completed"))
        except Exception as exc:
            LOGGER.exception("Search failed")
            self.repo.add_history(browser=self.browser.get(), engine=self.engine.get(), original_query=original, improved_query="", screenshot="", current_url="", status=f"Failed: {exc}")
            self.after(0, lambda: self._finish_search("", None, f"Search failed: {exc}"))
        finally:
            if runner: runner.close()

    def _finish_search(self, improved: str, shot: Path | None, message: str) -> None:
        self.progress.set(1); self.status.configure(text=message, text_color="#62c370" if shot else "#ed6a5a")
        notify(APP_NAME, message)
        if shot:
            image = ctk.CTkImage(Image.open(shot), size=(620, 300)); self.preview.configure(image=image, text=f"Original / improved: {self.query.get()}  →  {improved}"); self.preview.image = image

    def voice_search(self) -> None:
        def worker():
            try:
                result = listen(); self.after(0, lambda: (self.query.delete(0, "end"), self.query.insert(0, result), self.run_search()))
            except Exception as exc: self.after(0, lambda: self.status.configure(text=f"Voice input unavailable: {exc}", text_color="#ed6a5a"))
        threading.Thread(target=worker, daemon=True).start()

    def bookmark_current(self) -> None:
        if self.query.get().strip(): self.repo.add_bookmark(self.query.get().strip(), self.query.get().strip(), self.engine.get()); self.status.configure(text="Bookmark saved")

    def _page_history(self) -> None:
        ctk.CTkLabel(self.content, text="Search History", font=ctk.CTkFont(size=26, weight="bold")).pack(anchor="w", padx=28, pady=24)
        search = ctk.CTkEntry(self.content, placeholder_text="Filter searches"); search.pack(fill="x", padx=28)
        table = ctk.CTkTextbox(self.content, font=("Consolas", 12)); table.pack(expand=True, fill="both", padx=28, pady=15)
        def refresh(*_):
            table.delete("1.0", "end")
            for r in self.repo.history(search.get()): table.insert("end", f"#{r['id']:04}  {r['created_at']}  {r['engine']:<14} {r['original_query']}\n")
        search.bind("<KeyRelease>", refresh); refresh()
        buttons = ctk.CTkFrame(self.content, fg_color="transparent"); buttons.pack(fill="x", padx=28, pady=(0, 20))
        for kind in ("CSV", "JSON", "XLSX", "PDF"):
            ctk.CTkButton(buttons, text=f"Export {kind}", command=lambda k=kind: self.export(k)).pack(side="left", padx=4)

    def export(self, kind: str) -> None:
        path = EXPORTS_DIR / f"history_{datetime.now():%Y%m%d_%H%M%S}.{kind.lower()}"; export_history(self.repo.history(), path, kind); self.status_message(f"Exported {path.name}")

    def _page_gallery(self) -> None:
        ctk.CTkLabel(self.content, text="Screenshot Gallery", font=ctk.CTkFont(size=26, weight="bold")).pack(anchor="w", padx=28, pady=24)
        scroll = ctk.CTkScrollableFrame(self.content); scroll.pack(expand=True, fill="both", padx=28, pady=(0, 25))
        files = sorted(SCREENSHOTS_DIR.rglob("*.png"), reverse=True)
        for path in files:
            row = ctk.CTkFrame(scroll); row.pack(fill="x", pady=4)
            ctk.CTkLabel(row, text=path.name).pack(side="left", padx=10, pady=8)
            ctk.CTkButton(row, text="Open", width=70, command=lambda p=path: os.startfile(p)).pack(side="right", padx=5)
            ctk.CTkButton(row, text="OCR", width=70, command=lambda p=path: self.show_text("OCR", extract_text(p))).pack(side="right", padx=5)
            ctk.CTkButton(row, text="AI", width=70, command=lambda p=path: self.show_text("AI Analysis", analyze_screenshot(p))).pack(side="right", padx=5)
            ctk.CTkButton(row, text="Rename", width=70, command=lambda p=path: self.rename_screenshot(p)).pack(side="right", padx=5)
            ctk.CTkButton(row, text="Delete", width=70, fg_color="#a33a3a", command=lambda p=path: self.delete_screenshot(p)).pack(side="right", padx=5)

    def show_text(self, title: str, content: str) -> None:
        window = ctk.CTkToplevel(self); window.title(title); window.geometry("650x450"); text = ctk.CTkTextbox(window); text.pack(expand=True, fill="both", padx=12, pady=12); text.insert("1.0", content)

    def delete_screenshot(self, path: Path) -> None:
        """Remove a selected screenshot, then refresh the gallery."""
        try:
            path.unlink(); self.show_page("Gallery"); notify(APP_NAME, "Screenshot deleted")
        except OSError as exc:
            self.show_text("Delete failed", str(exc))

    def rename_screenshot(self, path: Path) -> None:
        """Prompt for a safe replacement filename."""
        dialog = ctk.CTkInputDialog(text="New filename (without path):", title="Rename screenshot")
        name = dialog.get_input()
        if not name:
            return
        target = path.with_name(Path(name).stem + path.suffix)
        try:
            path.rename(target); self.show_page("Gallery")
        except OSError as exc:
            self.show_text("Rename failed", str(exc))

    def _page_analytics(self) -> None:
        data = self.repo.analytics(); frame = ctk.CTkFrame(self.content); frame.pack(expand=True, fill="both", padx=28, pady=28)
        ctk.CTkLabel(frame, text="Search Analytics", font=ctk.CTkFont(size=26, weight="bold")).pack(anchor="w", padx=22, pady=20)
        lines = [f"Total searches: {data['total']}", f"Most used browser: {data['browser'][0][0] if data['browser'] else '—'}", f"Most used engine: {data['engine'][0][0] if data['engine'] else '—'}", f"Most searched keyword: {data['keyword'][0][0] if data['keyword'] else '—'}"]
        ctk.CTkLabel(frame, text="\n".join(lines), justify="left", font=ctk.CTkFont(size=17)).pack(anchor="w", padx=22)
        if data['daily']:
            import matplotlib.pyplot as plt
            figure, axis = plt.subplots(figsize=(7, 3)); axis.bar(data['daily'].keys(), data['daily'].values(), color="#3a7ebf"); axis.tick_params(axis="x", rotation=35); figure.tight_layout(); graph = EXPORTS_DIR / "analytics.png"; figure.savefig(graph); plt.close(figure)
            image = ctk.CTkImage(Image.open(graph), size=(620, 265)); label = ctk.CTkLabel(frame, image=image, text=""); label.image = image; label.pack(padx=22, pady=20)

    def _page_bookmarks(self) -> None:
        ctk.CTkLabel(self.content, text="Favourite Searches", font=ctk.CTkFont(size=26, weight="bold")).pack(anchor="w", padx=28, pady=24)
        for b in self.repo.bookmarks(): ctk.CTkButton(self.content, text=f"{b['name']}  ·  {b['engine']}", command=lambda x=b: self._run_bookmark(x)).pack(anchor="w", padx=28, pady=5)

    def _run_bookmark(self, bookmark: dict) -> None:
        self.show_page("Search"); self.query.insert(0, bookmark['query']); self.engine.set(bookmark['engine']); self.run_search()

    def _page_settings(self) -> None:
        ctk.CTkLabel(self.content, text="Settings", font=ctk.CTkFont(size=26, weight="bold")).pack(anchor="w", padx=28, pady=24)
        ctk.CTkLabel(self.content, text=f"Database: {DATABASE_PATH}\nScreenshots: {SCREENSHOTS_DIR}\nAPI key: {'configured' if os.getenv('OPENAI_API_KEY') else 'not configured (.env)'}", justify="left").pack(anchor="w", padx=28)

    def _page_about(self) -> None:
        ctk.CTkLabel(self.content, text=APP_NAME, font=ctk.CTkFont(size=28, weight="bold")).pack(pady=(80, 10))
        ctk.CTkLabel(self.content, text="A private, local-first Selenium search workspace.\nBuilt with Python, CustomTkinter, SQLite, and optional AI.").pack()

    def status_message(self, message: str) -> None:
        self.show_page("Search"); self.status.configure(text=message)

    def _close(self) -> None:
        self.repo.set_setting("window_size", self.geometry()); self.destroy()


if __name__ == "__main__":
    SearchAssistant().mainloop()
