# gui.py

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import os

from parser.fin_reader import parse_fin_file
from parser.fin_to_df import transactions_to_dataframe, clean_dataframe

class FinParserApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FIN File Parser")
        self.geometry("500x200")
        self.filepaths = []

        # File selection
        self.select_button = tk.Button(self, text="Select FIN Files", command=self.select_files)
        self.select_button.pack(pady=10)

        self.files_label = tk.Label(self, text="No files selected")
        self.files_label.pack()

        # Output format
        self.format_var = tk.StringVar(value='csv')
        self.format_frame = tk.Frame(self)
        tk.Radiobutton(self.format_frame, text="CSV", variable=self.format_var, value='csv').pack(side=tk.LEFT)
        tk.Radiobutton(self.format_frame, text="JSON", variable=self.format_var, value='json').pack(side=tk.LEFT)
        tk.Radiobutton(self.format_frame, text="SQLite", variable=self.format_var, value='sqlite').pack(side=tk.LEFT)
        self.format_frame.pack(pady=10)

        # Parse button
        self.parse_button = tk.Button(self, text="Parse and Export", command=self.start_parsing)
        self.parse_button.pack(pady=10)

        # Progress bar
        self.progress = ttk.Progressbar(self, mode='indeterminate')
        self.progress.pack(fill=tk.X, padx=20, pady=10)

    def select_files(self):
        paths = filedialog.askopenfilenames(
            title="Select .fin Files", filetypes=[("FIN files", "*.fin"), ("All files", "*.*")]
        )
        if paths:
            self.filepaths = list(paths)
            display_text = "\n".join(os.path.basename(p) for p in self.filepaths)
            self.files_label.config(text=display_text)

    def start_parsing(self):
        if not self.filepaths:
            messagebox.showwarning("No Files", "Please select at least one .fin file.")
            return
        # Disable UI elements
        self.parse_button.config(state=tk.DISABLED)
        self.progress.start(10)
        threading.Thread(target=self.parse_and_export).start()

    def parse_and_export(self):
        try:
            all_dfs = []
            for filepath in self.filepaths:
                stmts = parse_fin_file(filepath)
                df = transactions_to_dataframe(stmts)
                df = clean_dataframe(df)
                all_dfs.append(df)
            combined = all_dfs[0].append(all_dfs[1:], ignore_index=True)

            fmt = self.format_var.get()
            out_dir = os.path.dirname(self.filepaths[0])  # same dir as first file
            if fmt == 'csv':
                out_file = os.path.join(out_dir, 'parsed_transactions.csv')
                combined.to_csv(out_file, index=False)
            elif fmt == 'json':
                out_file = os.path.join(out_dir, 'parsed_transactions.json')
                combined.to_json(out_file, orient='records', date_format='iso')
            else:  # SQLite
                out_file = os.path.join(out_dir, 'parsed_transactions.db')
                combined.to_sql('transactions', f"sqlite:///{out_file}", if_exists='append', index=False)

            message = f"Successfully wrote {fmt.upper()} to:\n{out_file}"
            messagebox.showinfo("Done", message)
        except Exception as e:
            messagebox.showerror("Error", f"Parsing failed: {e}")
        finally:
            self.progress.stop()
            self.parse_button.config(state=tk.NORMAL)

if __name__ == '__main__':
    app = FinParserApp()
    app.mainloop()
