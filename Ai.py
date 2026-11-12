"""Planera uppgifter i egna kategorier.""" #Ai slop, behöver inte statera längs up

#Doesn't use a deafult colloring so its easy changable

import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from typing import TypedDict
from uuid import uuid4


DEFAULT_CATEGORIES = ["Hemma", "Skola", "Personligt", "Övrigt"]


class Task(TypedDict):
    id: str
    title: str
    category: str
    done: bool


class PlannerApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        root.title("Min planering")
        root.geometry("900x600")
        root.minsize(700, 450)
        root.configure(bg="#f4f6fb")
        self.categories = DEFAULT_CATEGORIES.copy()
        self.tasks: list[Task] = []
        self.selected_category: str | None = None
        self._style()
        self._layout()
        self._refresh_categories()
        self._refresh_tasks()

    def _style(self) -> None:
        style = ttk.Style(self.root)
        style.theme_use("clam")
        for name, options in {
            "TFrame": {"background": "#f4f6fb"},
            "Sidebar.TFrame": {"background": "#202a44"},
            "TLabel": {"background": "#f4f6fb", "foreground": "#202a44"},
            "Title.TLabel": {
                "background": "#f4f6fb",
                "foreground": "#202a44",
                "font": ("Segoe UI", 22, "bold"),
            },
            "SidebarTitle.TLabel": {
                "background": "#202a44",
                "foreground": "white",
                "font": ("Segoe UI", 17, "bold"),
            },
            "Treeview": {
                "background": "white",
                "fieldbackground": "white",
                "rowheight": 36,
                "font": ("Segoe UI", 10),
            },
            "Treeview.Heading": {
                "background": "#e8ecf5",
                "foreground": "#202a44",
                "font": ("Segoe UI", 10, "bold"),
            },
        }.items():
            style.configure(name, **options)
        style.map("Treeview", background=[("selected", "#dce6ff")])

    def _layout(self) -> None:
        root = self.root
        root.columnconfigure(1, weight=1)
        root.rowconfigure(0, weight=1)

        sidebar = ttk.Frame(root, style="Sidebar.TFrame", padding=20, width=220)
        sidebar.grid(row=0, column=0, sticky="ns")
        sidebar.grid_propagate(False)
        ttk.Label(sidebar, text="Min planering", style="SidebarTitle.TLabel").pack(
            anchor="w", pady=(4, 24)
        )
        ttk.Label(
            sidebar,
            text="KATEGORIER",
            background="#202a44",
            foreground="#aeb9d1",
            font=("Segoe UI", 9, "bold"),
        ).pack(anchor="w", pady=(0, 8))
        self.category_buttons = ttk.Frame(sidebar, style="Sidebar.TFrame")
        self.category_buttons.pack(fill="x")
        ttk.Button(sidebar, text="+ Lägg till kategori", command=self._add_category).pack(
            fill="x", side="bottom", pady=(12, 0)
        )

        content = ttk.Frame(root, padding=(30, 26, 30, 22))
        content.grid(row=0, column=1, sticky="nsew")
        content.columnconfigure(0, weight=1)
        content.rowconfigure(1, weight=1)
        header = ttk.Frame(content)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        header.columnconfigure(0, weight=1)
        self.heading = ttk.Label(header, text="Alla uppgifter", style="Title.TLabel")
        self.heading.grid(row=0, column=0, sticky="w")
        ttk.Button(header, text="+ Ny uppgift", command=self._add_task).grid(
            row=0, column=1, sticky="e"
        )

        listing = ttk.Frame(content)
        listing.grid(row=1, column=0, sticky="nsew")
        listing.columnconfigure(0, weight=1)
        listing.rowconfigure(0, weight=1)
        columns = ("status", "title", "category")
        self.task_list = ttk.Treeview(
            listing, columns=columns, show="headings", selectmode="browse"
        )
        for column, title, width in (
            ("status", "Status", 90),
            ("title", "Uppgift", 300),
            ("category", "Kategori", 150),
        ):
            self.task_list.heading(column, text=title)
            self.task_list.column(column, width=width)
        self.task_list.column("status", stretch=False, anchor="center")
        self.task_list.column("category", stretch=False)
        self.task_list.tag_configure("done", foreground="#7b8498")
        self.task_list.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(listing, orient="vertical", command=self.task_list.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.task_list.configure(yscrollcommand=scrollbar.set)

        actions = ttk.Frame(content)
        actions.grid(row=2, column=0, sticky="w", pady=(16, 0))
        ttk.Button(actions, text="Markera klar / ångra", command=self._toggle_done).pack(
            side="left"
        )
        ttk.Button(actions, text="Ta bort", command=self._delete_task).pack(
            side="left", padx=(8, 0)
        )

    def _refresh_categories(self) -> None:
        for child in self.category_buttons.winfo_children():
            child.destroy()
        for category in [None, *self.categories]:
            ttk.Button(
                self.category_buttons,
                text=category or "Alla uppgifter",
                command=lambda selected=category: self._select_category(selected),
            ).pack(fill="x", pady=2)

    def _select_category(self, category: str | None) -> None:
        self.selected_category = category
        self.heading.configure(text=category or "Alla uppgifter")
        self._refresh_tasks()

    def _refresh_tasks(self) -> None:
        for item in self.task_list.get_children():
            self.task_list.delete(item)
        tasks = (
            task for task in self.tasks
            if self.selected_category is None or task["category"] == self.selected_category
        )
        for task in sorted(tasks, key=lambda item: (item["done"], item["title"].casefold())):
            done = task["done"]
            self.task_list.insert(
                "", "end", iid=task["id"],
                values=("Klar" if done else "Öppen", task["title"], task["category"]),
                tags=("done",) if done else (),
            )

    def _add_category(self) -> None:
        category = simpledialog.askstring("Ny kategori", "Vad ska kategorin heta?", parent=self.root)
        if category is None:
            return
        category = category.strip()
        if not category:
            messagebox.showwarning("Tom kategori", "Skriv ett namn på kategorin.", parent=self.root)
            return
        if any(c.casefold() == category.casefold() for c in self.categories):
            messagebox.showwarning("Kategorin finns redan", "Välj ett annat namn.", parent=self.root)
            return
        self.categories.append(category)
        self._refresh_categories()
        self._select_category(category)

    def _add_task(self) -> None:
        dialog = tk.Toplevel(self.root)
        dialog.title("Ny uppgift")
        dialog.transient(self.root)
        dialog.resizable(False, False)
        dialog.grab_set()
        frame = ttk.Frame(dialog, padding=20)
        frame.grid()
        ttk.Label(frame, text="Vad behöver du göra?").grid(row=0, column=0, sticky="w")
        title = ttk.Entry(frame, width=38)
        title.grid(row=1, column=0, sticky="ew", pady=(6, 14))
        ttk.Label(frame, text="Kategori").grid(row=2, column=0, sticky="w")
        category = ttk.Combobox(frame, values=self.categories, state="readonly", width=35)
        category.grid(row=3, column=0, sticky="ew", pady=(6, 18))
        category.set(
            self.selected_category
            if self.selected_category in self.categories
            else self.categories[0]
        )

        def save() -> None:
            text = title.get().strip()
            if not text:
                messagebox.showwarning("Tom uppgift", "Skriv vad du behöver göra.", parent=dialog)
                title.focus_set()
                return
            self.tasks.append(
                {"id": uuid4().hex, "title": text, "category": category.get(), "done": False}
            )
            self._refresh_tasks()
            dialog.destroy()

        buttons = ttk.Frame(frame)
        buttons.grid(row=4, column=0, sticky="e")
        ttk.Button(buttons, text="Avbryt", command=dialog.destroy).pack(side="left", padx=(0, 8))
        ttk.Button(buttons, text="Spara", command=save).pack(side="left")
        title.focus_set()
        def save_on_enter(event: tk.Event) -> str:
            if event.widget == title:
                save()
            return "break"

        dialog.bind("<Return>", save_on_enter)

    def _selected_task(self) -> Task | None:
        selected = self.task_list.selection()
        if not selected:
            messagebox.showinfo("Välj en uppgift", "Markera en uppgift i listan först.", parent=self.root)
            return None
        return next((task for task in self.tasks if task["id"] == selected[0]), None)

    def _toggle_done(self) -> None:
        if task := self._selected_task():
            task["done"] = not task["done"]
            self._refresh_tasks()

    def _delete_task(self) -> None:
        if task := self._selected_task():
            if messagebox.askyesno(
                "Ta bort uppgift",
                f"Vill du ta bort uppgiften ”{task['title']}”?",
                parent=self.root,
            ):
                self.tasks.remove(task)
                self._refresh_tasks()


if __name__ == "__main__":
    root = tk.Tk()
    PlannerApp(root)
    root.mainloop()
