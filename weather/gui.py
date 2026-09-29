"""Tkinter (ttk) の画面。4ペイン: グループ / 地点 / 期間と操作 / 結果。"""
from __future__ import annotations

import queue
import sys
import threading
import tkinter as tk
from datetime import date, timedelta
from tkinter import messagebox, ttk

from PIL import Image, ImageTk

from . import export, paths, tenki
from .settings import (
    HEADER,
    PLACE,
    Group,
    Item,
    Settings,
    Term,
    load_places,
    search_places,
)

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WEEKDAYS = "月火水木金土日"
ICON_HEIGHT = 24
WIN_W, WIN_H = 1180, 780


class WeatherApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.settings = Settings.load()
        self.cache = tenki.Cache()
        self.icon_store = tenki.IconStore()

        self.forecasts: dict[str, tenki.PlaceForecast] = {}
        self._images: dict[str, ImageTk.PhotoImage] = {}  # 保持しないとGCで消える
        self._events: queue.Queue = queue.Queue()
        self._fetching = False

        self._build()
        self._sync_from_settings()
        self._refresh_range_label()
        self._pull_from_cache()
        self.root.after(50, self._fit_window)

    # --- 画面 ---------------------------------------------------------------

    def _build(self) -> None:
        root = self.root
        root.title("天気予報 ビューア")
        root.geometry(f"{WIN_W}x{WIN_H}")
        root.minsize(900, 560)

        self._start = self.settings.term.start_date()
        self.var_year = tk.IntVar(value=self._start.year)
        self.var_month = tk.IntVar(value=self._start.month)
        self.var_day = tk.IntVar(value=self._start.day)
        self.var_days = tk.IntVar(value=self.settings.term.days)
        self.var_range = tk.StringVar()
        self.var_icons = tk.BooleanVar(value=self.settings.display.show_icons)
        self.var_dedupe = tk.BooleanVar(value=self.settings.display.dedupe)
        self.var_force = tk.BooleanVar(value=False)
        self.var_search = tk.StringVar()
        self.var_search.trace_add("write", lambda *_: self._refresh_search())
        self.var_status = tk.StringVar(value="")

        self.body = body = ttk.Panedwindow(root, orient=tk.HORIZONTAL)
        body.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        body.add(self._build_groups(), weight=0)
        body.add(self._build_places(), weight=0)
        body.add(self._build_side(), weight=1)

        self._build_log(root)
        self.root.after(100, self._poll_events)

    def _build_groups(self) -> ttk.Frame:
        frame = ttk.Frame(self.root, padding=(0, 0, 6, 0))
        frame.configure(width=210)
        frame.pack_propagate(False)
        head = ttk.Frame(frame)
        head.pack(fill=tk.X)
        ttk.Label(head, text="グループ").pack(side=tk.LEFT)
        ttk.Label(head, text="(左列クリックで有効/無効)", foreground="#888").pack(side=tk.LEFT, padx=6)

        self.group_tree = ttk.Treeview(
            frame, columns=("on", "name", "count"), show="headings", selectmode="browse"
        )
        self.group_tree.heading("on", text="")
        self.group_tree.heading("name", text="グループ")
        self.group_tree.heading("count", text="地点")
        self.group_tree.column("on", width=28, minwidth=28, anchor=tk.CENTER, stretch=False)
        self.group_tree.column("name", width=130, minwidth=90, anchor=tk.W, stretch=True)
        self.group_tree.column("count", width=44, minwidth=40, anchor=tk.E, stretch=False)
        self.group_tree.pack(fill=tk.BOTH, expand=True, pady=4)
        self.group_tree.bind("<<TreeviewSelect>>", lambda e: self._on_group_select())
        self.group_tree.bind("<Button-1>", self._on_group_click)

        row = ttk.Frame(frame)
        row.pack(fill=tk.X)
        for text, cmd in (
            ("追加", self._add_group),
            ("複製", self._copy_group),
            ("削除", self._del_group),
        ):
            ttk.Button(row, text=text, command=cmd, width=5).pack(side=tk.LEFT, padx=1)
        row2 = ttk.Frame(frame)
        row2.pack(fill=tk.X, pady=(3, 0))
        for text, cmd in (("↑", lambda: self._move_group(-1)), ("↓", lambda: self._move_group(1))):
            ttk.Button(row2, text=text, command=cmd, width=5).pack(side=tk.LEFT, padx=1)
        return frame

    def _build_places(self) -> ttk.Frame:
        frame = ttk.Frame(self.root, padding=(0, 0, 6, 0))
        frame.configure(width=250)
        frame.pack_propagate(False)
        ttk.Label(frame, text="地点（このグループの順）").pack(anchor=tk.W)
        self.item_list = tk.Listbox(frame, selectmode=tk.EXTENDED, exportselection=False)
        self.item_list.pack(fill=tk.BOTH, expand=True, pady=4)
        self.item_list.bind("<Double-Button-1>", lambda e: self._move_item(-1))

        row = ttk.Frame(frame)
        row.pack(fill=tk.X)
        for text, cmd in (
            ("追加", self._add_places),
            ("見出し", self._add_header),
            ("削除", self._del_items),
        ):
            ttk.Button(row, text=text, command=cmd, width=6).pack(side=tk.LEFT, padx=1)
        row2 = ttk.Frame(frame)
        row2.pack(fill=tk.X, pady=(3, 0))
        for text, cmd in (("↑", lambda: self._move_item(-1)), ("↓", lambda: self._move_item(1))):
            ttk.Button(row2, text=text, command=cmd, width=6).pack(side=tk.LEFT, padx=1)
        row2.pack(side=tk.TOP, fill=tk.X, pady=(3, 6))

        ttk.Separator(frame).pack(fill=tk.X, pady=2)
        ttk.Label(frame, text="地点を検索して追加").pack(anchor=tk.W)
        ttk.Entry(frame, textvariable=self.var_search).pack(fill=tk.X, pady=(2, 2))
        self.search_list = tk.Listbox(frame, selectmode=tk.EXTENDED, height=8, exportselection=False)
        self.search_list.pack(fill=tk.BOTH, expand=True)
        self.search_list.bind("<Double-Button-1>", lambda e: self._add_places())
        ttk.Button(frame, text="検索結果を追加 (Enter)", command=self._add_places).pack(fill=tk.X, pady=(3, 0))
        return frame

    def _build_side(self) -> ttk.Frame:
        frame = ttk.Frame(self.root)
        top = ttk.Frame(frame)
        top.pack(fill=tk.X)

        ttk.Label(top, text="開始").pack(side=tk.LEFT, padx=(0, 4))
        for label, var, lo, hi in (
            ("年", self.var_year, 2000, 2100),
            ("月", self.var_month, 1, 12),
            ("日", self.var_day, 1, 31),
        ):
            ttk.Spinbox(top, from_=lo, to=hi, width=4, textvariable=var,
                        command=self._apply_term).pack(side=tk.LEFT, padx=1)
            ttk.Label(top, text=label).pack(side=tk.LEFT, padx=(1, 4))
        ttk.Button(top, text="今日", width=4, command=self._on_today).pack(side=tk.LEFT, padx=(2, 0))

        bottom = ttk.Frame(frame)
        bottom.pack(fill=tk.X, pady=(3, 0))
        ttk.Label(bottom, text="日数").pack(side=tk.LEFT, padx=(0, 4))
        ttk.Spinbox(bottom, from_=1, to=paths.MAX_DAYS, width=4, textvariable=self.var_days,
                    command=self._apply_term).pack(side=tk.LEFT, padx=1)
        ttk.Label(bottom, text="日").pack(side=tk.LEFT, padx=(1, 6))
        ttk.Label(bottom, textvariable=self.var_range, foreground="#666").pack(side=tk.LEFT)
        ttk.Button(bottom, text="再描画", command=self._apply_term).pack(side=tk.RIGHT)

        opts = ttk.Frame(frame)
        opts.pack(fill=tk.X, pady=4)
        ttk.Checkbutton(opts, text="アイコン", variable=self.var_icons,
                        command=self._apply_display).pack(side=tk.LEFT)
        ttk.Checkbutton(opts, text="地点を重複させない", variable=self.var_dedupe,
                        command=self._apply_display).pack(side=tk.LEFT, padx=8)
        ttk.Checkbutton(opts, text="強制再取得", variable=self.var_force).pack(side=tk.LEFT)

        btns = ttk.Frame(frame)
        btns.pack(fill=tk.X, pady=4)
        self.btn_fetch = ttk.Button(btns, text="取得", command=self._on_fetch)
        self.btn_fetch.pack(side=tk.LEFT)
        self.btn_html = ttk.Button(btns, text="HTML出力", command=self._on_export)
        self.btn_html.pack(side=tk.LEFT, padx=4)
        self.btn_open = ttk.Button(btns, text="開く", command=self._on_open)
        self.btn_open.pack(side=tk.LEFT)

        self.progress = ttk.Progressbar(frame, mode="determinate")
        self.progress.pack(fill=tk.X, pady=(4, 6))

        grid = ttk.Frame(frame)
        grid.pack(fill=tk.BOTH, expand=True)
        self.head_canvas = tk.Canvas(grid, height=self.HEADER_H, bg="#eef2f7",
                                     highlightthickness=1, highlightbackground="#ccd3dc")
        self.grid_canvas = tk.Canvas(grid, bg="white", highlightthickness=1,
                                     highlightbackground="#ccc")
        grid_vsb = ttk.Scrollbar(grid, orient=tk.VERTICAL, command=self.grid_canvas.yview)
        grid_hsb = ttk.Scrollbar(grid, orient=tk.HORIZONTAL, command=self._on_hscroll)
        self.grid_canvas.configure(yscrollcommand=grid_vsb.set, xscrollcommand=grid_hsb.set)
        grid_vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.grid_hsb = grid_hsb
        grid_hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self.head_canvas.pack(side=tk.TOP, fill=tk.X)
        self.grid_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.grid_canvas.bind("<MouseWheel>", self._on_wheel)
        self.head_canvas.bind("<MouseWheel>", lambda e: self._on_wheel(e) or "break")
        return frame

    def _build_log(self, root: tk.Tk) -> None:
        frame = ttk.LabelFrame(root, text="ログ", padding=4)
        frame.pack(fill=tk.X, padx=6, pady=(0, 6))
        self.log_text = tk.Text(frame, height=5, wrap=tk.NONE, state=tk.DISABLED)
        sb = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=sb.set)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        ttk.Label(root, textvariable=self.var_status).pack(anchor=tk.W, padx=8, pady=(0, 4))

    def log(self, message: str) -> None:
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)

    # --- 設定と表示の同期 ---------------------------------------------------

    def current_group(self) -> Group | None:
        sel = self.group_tree.selection()
        if not sel:
            return None
        index = int(sel[0])
        return self.settings.groups[index] if 0 <= index < len(self.settings.groups) else None

    def _on_group_click(self, event) -> None:
        """左列（有効/無効の列）をクリックされたら所属行のチェックを反転する。"""
        if self.group_tree.identify_region(event.x, event.y) != "cell":
            return
        if self.group_tree.identify_column(event.x) != "#1":
            return
        iid = self.group_tree.identify_row(event.y)
        if not iid:
            return
        index = int(iid)
        name = self.settings.groups[index].name
        if name in self.settings.active_groups:
            self.settings.active_groups.remove(name)
        else:
            self.settings.active_groups.append(name)
        self._save()
        self._sync_from_settings()
        self.group_tree.selection_set(iid)

    def _sync_from_settings(self) -> None:
        selected = self.group_tree.selection() if hasattr(self, "group_tree") else ()
        self.group_tree.delete(*self.group_tree.get_children())
        for i, g in enumerate(self.settings.groups):
            self.group_tree.insert(
                "", tk.END, iid=str(i),
                values=(
                    "☑" if g.name in self.settings.active_groups else "☐",
                    g.name,
                    len(g.places()),
                ),
            )
        if selected and self.group_tree.exists(selected[0]):
            self.group_tree.selection_set(selected[0])
        self._on_group_select()

    def _on_group_select(self) -> None:
        self._refresh_items()
        self._refresh_table()

    def _refresh_items(self) -> None:
        self.item_list.delete(0, tk.END)
        group = self.current_group()
        if not group:
            return
        for item in group.items:
            self.item_list.insert(tk.END, ("▸ " if item.is_header else "") + item.text)

    def _refresh_search(self) -> None:
        self.search_list.delete(0, tk.END)
        query = self.var_search.get()
        if not query.strip():
            return
        known = load_places()
        for name in search_places(query):
            self.search_list.insert(tk.END, name if name in known else f"{name} ※未登録")

    # --- 編集操作 -----------------------------------------------------------

    def _save(self) -> None:
        start = self._read_date_vars()
        self._set_date_vars(start)
        self.settings.term = Term(start.isoformat(), self.var_days.get())
        self.settings.display.show_icons = self.var_icons.get()
        self.settings.display.dedupe = self.var_dedupe.get()
        self.settings.save()
        self._refresh_range_label()

    def _set_date_vars(self, d: date) -> None:
        self.var_year.set(d.year)
        self.var_month.set(d.month)
        self.var_day.set(d.day)

    def _read_date_vars(self) -> date:
        """年/月/日から日付を読む。2月31日など不正なら直前の正しい値に戻す。"""
        try:
            return date(self.var_year.get(), self.var_month.get(), self.var_day.get())
        except (ValueError, tk.TclError):
            return self.settings.term.start_date()

    def _refresh_range_label(self) -> None:
        term = self.settings.term
        start, end = term.start_date(), term.end_date()
        text = f"{start:%Y/%m/%d} 〜 {end:%m/%d}"
        today = date.today()
        if end < today:
            text += "  ※すべて過去"
        elif start > today + timedelta(days=paths.MAX_DAYS - 1):
            text += "  ※予報期間外"
        self.var_range.set(text)

    def _on_today(self) -> None:
        self._set_date_vars(date.today())
        self._apply_term()

    def _add_group(self) -> None:
        name = self._ask("グループ名", "新しいグループ")
        if not name:
            return
        if self.settings.group(name):
            messagebox.showwarning("重複", f"『{name}』は既にあります")
            return
        self.settings.groups.append(Group(name=name))
        self._save()
        self._sync_from_settings()
        self._select_group(len(self.settings.groups) - 1)

    def _copy_group(self) -> None:
        src = self.current_group()
        if not src:
            return
        name = self._ask("複製後のグループ名", "グループの複製", default=src.name + " のコピー")
        if not name:
            return
        self.settings.groups.append(
            Group(name=name, items=[Item(i.type, i.text) for i in src.items])
        )
        self._save()
        self._sync_from_settings()
        self._select_group(len(self.settings.groups) - 1)

    def _del_group(self) -> None:
        group = self.current_group()
        if not group:
            return
        if not messagebox.askyesno("確認", f"『{group.name}』を削除しますか？"):
            return
        index = self.settings.groups.index(group)
        self.settings.groups.remove(group)
        if group.name in self.settings.active_groups:
            self.settings.active_groups.remove(group.name)
        self._save()
        self._sync_from_settings()
        self._select_group(min(index, len(self.settings.groups) - 1))

    def _select_group(self, index: int) -> None:
        iid = str(index)
        if self.group_tree.exists(iid):
            self.group_tree.selection_set(iid)
            self.group_tree.see(iid)
        self._on_group_select()

    def _move_group(self, delta: int) -> None:
        index = self._selected_index()
        if index is None:
            return
        j = index + delta
        if not 0 <= j < len(self.settings.groups):
            return
        groups = self.settings.groups
        groups[index], groups[j] = groups[j], groups[i]
        self._save()
        self._sync_from_settings()
        self._select_group(j)

    def _selected_index(self) -> int | None:
        sel = self.group_tree.selection()
        return int(sel[0]) if sel else None

    def _add_places(self) -> None:
        group = self.current_group()
        names = [self.search_list.get(i) for i in self.search_list.curselection()]
        if not group or not names:
            return
        known = load_places()
        existing = {i.text for i in group.items if not i.is_header}
        added = 0
        for raw in names:
            name = raw.split(" ")[0]
            if name in existing:
                continue
            if name not in known:
                messagebox.showerror("未登録", f"『{name}』は tenki.jp 対応表にありません")
                continue
            group.items.append(Item(PLACE, name))
            existing.add(name)
            added += 1
        if added:
            self._save()
            self._refresh_items()
            self.log(f"『{group.name}』に {added} 地点を追加しました")

    def _add_header(self) -> None:
        group = self.current_group()
        if not group:
            return
        text = self._ask("見出し", "リストの中に入れる区切り見出し", default="例: 東京/神奈川")
        if not text:
            return
        group.items.append(Item(HEADER, text))
        self._save()
        self._refresh_items()

    def _del_items(self) -> None:
        group = self.current_group()
        if not group:
            return
        sel = sorted(self.item_list.curselection(), reverse=True)
        if not sel:
            return
        for i in sel:
            del group.items[i]
        self._save()
        self._refresh_items()

    def _move_item(self, delta: int) -> None:
        group = self.current_group()
        if not group:
            return
        sel = sorted(self.item_list.curselection())
        if not sel:
            return
        indices = list(range(len(group.items)))
        if delta < 0:
            for k in sel:
                if k == 0 or indices[k - 1] in sel:
                    return
        else:
            for k in sel:
                if k == len(indices) - 1 or indices[k + 1] in sel:
                    return
        items = group.items
        for k in sel:
            items[k], items[k + delta] = items[k + delta], items[k]
        self._save()
        self._refresh_items()
        self.item_list.selection_set(sel[0] + delta)

    def _ask(self, prompt: str, title: str, default: str = "") -> str | None:
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.transient(self.root)
        dialog.resizable(False, False)
        ttk.Label(dialog, text=prompt).grid(row=0, column=0, padx=10, pady=(10, 4))
        var = tk.StringVar(value=default)
        entry = ttk.Entry(dialog, textvariable=var, width=32)
        entry.grid(row=1, column=0, padx=10, pady=(0, 10))
        entry.focus_set()
        entry.select_range(0, tk.END)
        result: list[str | None] = [None]

        def ok() -> None:
            result[0] = var.get().strip()
            dialog.destroy()

        def cancel() -> None:
            dialog.destroy()

        ttk.Button(dialog, text="OK", command=ok).grid(row=2, column=0, sticky=tk.E, padx=10, pady=(0, 8))
        dialog.bind("<Return>", lambda e: ok())
        dialog.bind("<Escape>", lambda e: cancel())
        dialog.grab_set()
        self.root.wait_window(dialog)
        return result[0] or None

    def _apply_term(self) -> None:
        self._save()
        self._refresh_table()
        self._fit_window()

    def _apply_display(self) -> None:
        self._save()
        self._refresh_table()

    def _fit_window(self) -> None:
        """開始日と日数の分の列を1画面で収めるよう、サイズとペイン配分を調整する。"""
        self.root.update_idletasks()
        groups_w = 210
        places_w = 250
        canvas_needed = self.COL_PLACE + self.COL_DATE * len(self.settings.term.dates()) + 30
        body_pad = 12  # Panedwindow の padx(6) の左右分
        needed = body_pad + groups_w + places_w + canvas_needed
        screen = self.root.winfo_screenwidth()
        new_w = min(max(self.root.winfo_width(), needed), screen - 24)
        self.root.geometry(f"{new_w}x{self.root.winfo_height()}")
        self.root.update_idletasks()
        # 右ペイン（結果テーブル）へ可能な限り幅を配分する
        self.body.sashpos(0, groups_w)
        self.body.sashpos(1, groups_w + places_w)
        self.root.update_idletasks()

    # --- 取得 ---------------------------------------------------------------

    def _on_fetch(self) -> None:
        if self._fetching:
            return
        self._save()
        items = self.settings.resolved_items()
        places = self.settings.resolved_places()
        if not places:
            messagebox.showinfo("対象なし", "グループを選んで場所を追加してください")
            return

        self.forecasts.clear()
        self._refresh_table()
        self._fetching = True
        self.btn_fetch.configure(state=tk.DISABLED)
        self.progress.configure(maximum=len(places), value=0)
        self._put(f"取得開始: {len(places)} 地点 / {len(items)} 行")

        def worker() -> None:
            def progress(done, total, place, result):
                self._put(("progress", done, total, place, result.error))
            try:
                results = tenki.fetch_all(
                    places,
                    on_progress=progress,
                    force=self.var_force.get(),
                    cache=self.cache,
                )
                self._put(("done", {f.place: f for f in results}))
            except Exception as e:  # noqa: BLE001 - UI側で通知する
                self._put(("fatal", f"{type(e).__name__}: {e}"))

        threading.Thread(target=worker, daemon=True).start()

    def _put(self, event) -> None:
        self._events.put(event)

    def _poll_events(self) -> None:
        try:
            while True:
                event = self._events.get_nowait()
                if isinstance(event, tuple) and event[0] == "progress":
                    self._on_progress(*event[1:])
                elif isinstance(event, tuple) and event[0] == "done":
                    self._on_done(*event[1:])
                elif isinstance(event, tuple) and event[0] == "fatal":
                    self._on_fatal(event[1])
        except queue.Empty:
            pass
        self.root.after(100, self._poll_events)

    def _on_progress(self, done: int, total: int, place: str, error: str | None) -> None:
        self.progress.configure(value=done)
        if error:
            self.log(f"  [{done}/{total}] {place}: 失敗 - {error}")
        else:
            self.log(f"  [{done}/{total}] {place}")

    def _on_done(self, forecasts: dict[str, tenki.PlaceForecast]) -> None:
        self.forecasts = forecasts
        self._fetching = False
        self.btn_fetch.configure(state=tk.NORMAL)
        failed = [f.place for f in forecasts.values() if f.error]
        announced = next((f.announced for f in forecasts.values() if f.announced), None)
        summary = f"取得完了: 成功 {len(forecasts) - len(failed)} / 失敗 {len(failed)}"
        if announced:
            summary += f" / {announced}"
        self._put_status(summary)
        self.log(summary)
        for place in failed:
            self.log(f"  失敗: {place} - {forecasts[place].error}")
        self._refresh_table()

    def _on_fatal(self, message: str) -> None:
        self._fetching = False
        self.btn_fetch.configure(state=tk.NORMAL)
        self._put_status("取得に失敗しました")
        self.log(f"ERROR {message}")
        messagebox.showerror("取得エラー", message)

    def _put_status(self, text: str) -> None:
        self.var_status.set(text)

    def _pull_from_cache(self) -> None:
        places = self.settings.resolved_places()
        if not self.cache.is_fresh(places):
            if self.cache.data["places"]:
                self._put_status("キャッシュは古いので取得してください")
            return
        for name in places:
            hit = self.cache.get(name)
            if hit is not None:
                self.forecasts[name] = hit
        if self.forecasts:
            self._put_status(f"キャッシュから表示中 ({len(self.forecasts)} 地点)")
            self._refresh_table()

    # --- 結果テーブル（Canvas グリッド） -------------------------------------

    COL_PLACE = 140
    COL_DATE = 78
    ROW_H = 50
    HEADER_H = 44

    def _on_wheel(self, event) -> None:
        if event.delta:
            self.grid_canvas.yview_scroll(int(-event.delta / 120), "units")

    def _on_hscroll(self, *args) -> None:
        """横スクロールはヘッダーとデータの両方に同期させる。"""
        self.head_canvas.xview(*args)
        self.grid_canvas.xview(*args)

    def _refresh_table(self) -> None:
        self._images.clear()
        self.grid_canvas.delete("all")
        self.head_canvas.delete("all")
        items = self.settings.resolved_items()
        if not items:
            self.grid_canvas.configure(scrollregion=(0, 0, 1, 1))
            return

        term = self.settings.term
        dates = term.dates()
        col_w = self.COL_DATE if dates else 0
        total_w = self.COL_PLACE + col_w * len(dates)

        # 固定ヘッダー行（月日が常に見える）
        head = self.head_canvas
        head.create_rectangle(0, 0, total_w, self.HEADER_H, fill="#eef2f7",
                              outline="#d7dde5")
        head.create_text(8, self.HEADER_H // 2, text="地点", anchor=tk.W,
                         font=("Yu Gothic UI", 9, "bold"))
        for i, d in enumerate(dates):
            x = self.COL_PLACE + i * col_w + col_w // 2
            head.create_text(x, self.HEADER_H // 2 - 7,
                             text=f"{d.month}/{d.day}", font=("Yu Gothic UI", 9))
            head.create_text(x, self.HEADER_H // 2 + 9,
                             text=f"({WEEKDAYS[d.weekday()]})",
                             font=("Yu Gothic UI", 8), fill="#777")
        head.create_line(0, self.HEADER_H - 1, total_w, self.HEADER_H - 1, fill="#ccd3dc")
        for i in range(1, len(dates) + 1):
            x = self.COL_PLACE + i * col_w
            head.create_line(x, 0, x, self.HEADER_H, fill="#e5e9ee")
        head.configure(scrollregion=(0, 0, total_w, self.HEADER_H))

        # データ本体（縦スクロールするのはこちらだけ）
        canvas = self.grid_canvas
        y = 0
        for item in items:
            if item.is_header:
                canvas.create_rectangle(0, y, total_w, y + self.ROW_H,
                                        fill="#fff4d6", outline="#eadcb8")
                canvas.create_text(8, y + self.ROW_H // 2,
                                   text=f"▸ {item.text}", anchor=tk.W,
                                   font=("Yu Gothic UI", 9, "bold"))
                y += self.ROW_H
                continue

            forecast = self.forecasts.get(item.text)
            self._draw_row(y, item.text, forecast, dates)
            y += self.ROW_H

        total_h = y
        for i in range(1, len(dates) + 1):
            x = self.COL_PLACE + i * col_w
            canvas.create_line(x, 0, x, total_h, fill="#e5e9ee")
        canvas.configure(scrollregion=(0, 0, total_w, total_h))

    def _draw_row(self, y: int, place: str, forecast, dates: list[date]) -> None:
        if forecast is None:
            self.grid_canvas.create_text(8, y + self.ROW_H // 2, text=f"? {place}",
                                         anchor=tk.W, fill="#999")
            return
        if forecast.error:
            self.grid_canvas.create_rectangle(0, y, self.COL_PLACE + self.COL_DATE * len(dates),
                                              y + self.ROW_H, fill="#fdecea", outline="#f2c8c2")
            self.grid_canvas.create_text(8, y + self.ROW_H // 2, text=place, anchor=tk.W,
                                         font=("Yu Gothic UI", 9, "bold"))
            self.grid_canvas.create_text(self.COL_PLACE + 8, y + self.ROW_H // 2,
                                         text=f"取得失敗: {forecast.error}", anchor=tk.W,
                                         fill="#a12")
            return
        self.grid_canvas.create_text(8, y + self.ROW_H // 2, text=place, anchor=tk.W,
                                     font=("Yu Gothic UI", 9, "bold"))
        for i, d in enumerate(dates):
            self._draw_cell(y, self.COL_PLACE + i * self.COL_DATE, forecast, d)

    def _draw_cell(self, y: int, x: int, forecast: tenki.PlaceForecast, d: date) -> None:
        daily = forecast.on(d)
        if daily is None:
            return
        cx = x + self.COL_DATE // 2
        if self.settings.display.show_icons:
            photo = self._photo(daily.icon_url)
            if photo is not None:
                self.grid_canvas.create_image(cx, y + 17, image=photo)
                text = " ".join(v for v in (daily.prob, daily.precip) if v)
                if text:
                    self.grid_canvas.create_text(cx, y + 39, text=text,
                                                 font=("Yu Gothic UI", 8))
                return
        text = daily.telop or ""
        nums = " ".join(v for v in (daily.prob, daily.precip) if v)
        self.grid_canvas.create_text(cx, y + 17, text=text, font=("Yu Gothic UI", 9))
        if nums:
            self.grid_canvas.create_text(cx, y + 37, text=nums, font=("Yu Gothic UI", 8),
                                         fill="#555")

    def _photo(self, url: str | None) -> ImageTk.PhotoImage | None:
        if not url:
            return None
        if url in self._images:
            return self._images[url]
        image: Image.Image | None = self.icon_store.get(url)
        if image is None:
            return None
        ratio = ICON_HEIGHT / image.height
        small = image.resize((max(1, int(image.width * ratio)), ICON_HEIGHT), Image.LANCZOS)
        photo = ImageTk.PhotoImage(small)
        self._images[url] = photo  # 参照を保持しないとセルから消える
        return photo

    # --- 出力 ---------------------------------------------------------------

    def _on_export(self) -> None:
        if not self.forecasts:
            messagebox.showinfo("データなし", "先に取得してください")
            return
        self._warm_icons()
        path = export.save(
            self.settings.resolved_items(),
            self.forecasts,
            self.settings.term,
            icons=self.icon_store,
            show_icons=self.settings.display.show_icons,
            title="天気予報",
        )
        self._put_status(f"HTML出力: {path.name}")
        self.log(f"HTML出力: {path}")

    def _on_open(self) -> None:
        path = paths.EXPORT_HTML
        if not path.exists():
            messagebox.showinfo("未出力", "先に HTML出力 を実行してください")
            return
        export.open_in_browser(path)

    def _warm_icons(self) -> None:
        """出力前に、まだ取っていないアイコンをまとめて取得する。"""
        for url in sorted(export.used_icon_urls(self.forecasts)):
            self.icon_store.get(url)


def main() -> None:
    root = tk.Tk()
    WeatherApp(root)
    root.mainloop()
