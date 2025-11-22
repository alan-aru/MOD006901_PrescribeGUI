# gui.py
import pandas as pd
import matplotlib.pyplot as plt
import threading
import os
from tkinter import *
from tkinter import ttk, filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Import logic functions
from logic import (
    load_csv_file,
    detect_numeric_columns,
    detect_categorical_columns,
    apply_filters,
    aggregate_for_plot,
    numeric_summary,
    categorical_summary,
)


class PrescribingDataGUI:
    def __init__(self, main):
        self.main = main
        main.title("NHS Prescribing Data Explorer")
        main.geometry("1400x800")

        # --- File Upload Section ---
        self.file_label = Label(main, text="No file loaded", fg="gray")
        self.file_label.pack(pady=5)

        self.load_button = Button(main, text="Load CSV", command=self.load_csv)
        self.load_button.pack(pady=5)

        # --- Filter Frame ---
        self.filter_frame = LabelFrame(main, text="Optional Filters", padx=5, pady=5)
        self.filter_frame.pack(fill=X, padx=10, pady=5)

        self.filters = {
            "REGIONAL_OFFICE_NAME": None,
            "PCO_NAME": None,
            "ICB_NAME": None,
            "PRACTICE_NAME": None,
            "BNF_CHEMICAL_SUBSTANCE": None,
            "BNF_PRESENTATION_NAME": None,
            "BNF_CHAPTER_PLUS_CODE": None
        }

        self.filter_widgets = {}

        # 2-row layout
        for idx, col in enumerate(self.filters.keys()):
            row = 0 if idx < 4 else 1
            col_pos = idx if idx < 4 else idx - 4

            Label(self.filter_frame, text=f"{col}:").grid(
                row=row*2, column=col_pos*2, padx=5, pady=5, sticky=W
            )

            cb = ttk.Combobox(self.filter_frame, state="readonly", width=50)
            cb.grid(row=row*2+1, column=col_pos*2, columnspan=2, padx=5, pady=5, sticky=W)
            self.filter_widgets[col] = cb

        # --- Plot Controls ---
        self.control_frame = Frame(main)
        self.control_frame.pack(fill=X, padx=10, pady=5)

        Label(self.control_frame, text="X-axis (categorical):").grid(row=0, column=0, padx=5)
        self.x_dropdown = ttk.Combobox(self.control_frame, state="readonly", width=50)
        self.x_dropdown.grid(row=0, column=1, padx=5)

        Label(self.control_frame, text="Y-axis (numeric):").grid(row=0, column=2, padx=5)
        self.y_dropdown = ttk.Combobox(self.control_frame, state="readonly", width=25)
        self.y_dropdown.grid(row=0, column=3, padx=5)

        Label(self.control_frame, text="Aggregation:").grid(row=0, column=4, padx=5)
        self.agg_dropdown = ttk.Combobox(self.control_frame, state="readonly", width=12)
        self.agg_dropdown['values'] = ["Sum", "Average", "Count"]
        self.agg_dropdown.set("Sum")
        self.agg_dropdown.grid(row=0, column=5, padx=5)

        Button(self.control_frame, text="Plot Data", command=self.plot_data).grid(row=0, column=6, padx=10)
        Button(self.control_frame, text="Show Summary", command=self.show_summary).grid(row=0, column=7, padx=10)

        # Output frame
        self.output_frame = Frame(main)
        self.output_frame.pack(fill=BOTH, expand=True)

        # Internal state
        self.df = None
        self.numeric_cols = []
        self.categorical_cols = []

        # Exclusions for categorical summary
        self.categorical_summary_exclude = [
            "ADDRESS_1", "ADDRESS_2", "ADDRESS_3", "ADDRESS_4",
            "POSTCODE", "YEAR_MONTH"
        ]

    # --- Load CSV ---
    def load_csv(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv")],
            title="Select NHS Prescribing CSV Dataset"
        )
        if not file_path:
            return

        # Loading popup
        loading = Toplevel(self.main)
        loading.title("Loading")
        loading.geometry("320x90")
        loading.resizable(False, False)
        loading.transient(self.main)
        try:
            loading.grab_set()
        except:
            pass

        Label(loading, text="Loading file, please wait...").pack(pady=(12, 6))
        pb = ttk.Progressbar(loading, mode='indeterminate')
        pb.pack(fill=X, padx=12, pady=(0, 10))
        pb.start(10)

        def finish_load(result_df, error):
            pb.stop()
            try:
                loading.grab_release()
            except:
                pass
            loading.destroy()

            if error:
                messagebox.showerror("Error", f"Failed to load CSV:\n{error}")
                return

            self.df = result_df
            self.file_label.config(text=f"Loaded: {os.path.basename(file_path)}", fg="green")

            # Use logic.py
            self.numeric_cols = detect_numeric_columns(self.df)
            self.categorical_cols = detect_categorical_columns(self.df, self.numeric_cols)

            # Populate dropdowns
            self.x_dropdown['values'] = self.categorical_cols
            self.y_dropdown['values'] = self.numeric_cols

            # Populate filters
            for col in self.filters.keys():
                if col in self.df.columns:
                    values = sorted(self.df[col].dropna().unique().tolist())
                    self.filter_widgets[col]['values'] = ["All"] + values
                    self.filter_widgets[col].set("All")

            messagebox.showinfo("Success", "CSV loaded successfully.")

        def do_load():
            try:
                df_local = load_csv_file(file_path)
                self.main.after(0, lambda: finish_load(df_local, None))
            except Exception as e:
                self.main.after(0, lambda: finish_load(None, e))

        threading.Thread(target=do_load, daemon=True).start()

    # --- Plotting ---
    def plot_data(self):
        if self.df is None:
            messagebox.showwarning("No data", "Please load a CSV file first.")
            return

        x_col = self.x_dropdown.get()
        y_col = self.y_dropdown.get()
        agg_method = self.agg_dropdown.get()

        df_filtered = apply_filters(
            self.df,
            {col: self.filter_widgets[col].get() for col in self.filters.keys()}
        )

        if df_filtered.empty:
            messagebox.showinfo("No data", "No rows match the selected filters.")
            return

        plot_df = aggregate_for_plot(df_filtered, x_col, y_col, agg_method)

        # Draw plot
        fig, ax = plt.subplots(figsize=(8, 5))
        plot_df.plot(kind="bar", ax=ax)

        ax.set_title(f"{agg_method} of {y_col} by {x_col}")
        ax.set_ylabel(f"{agg_method} of {y_col}")
        ax.set_xlabel(x_col)
        plt.xticks(rotation=45, ha="right")
        fig.tight_layout()

        for widget in self.output_frame.winfo_children():
            widget.destroy()

        canvas = FigureCanvasTkAgg(fig, master=self.output_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=True)

        def on_resize(event):
            fig.tight_layout()
            canvas.draw()

        self.output_frame.bind("<Configure>", on_resize)

    # --- Summary ---
    def show_summary(self):
        if self.df is None:
            messagebox.showwarning("No data", "Please load a CSV file first.")
            return

        df_filtered = apply_filters(
            self.df,
            {col: self.filter_widgets[col].get() for col in self.filters.keys()}
        )
        if df_filtered.empty:
            messagebox.showinfo("No data", "No rows match the selected filters.")
            return

        # Clear previous output
        for widget in self.output_frame.winfo_children():
            widget.destroy()

        # Create scrollable Text widget
        text_widget = Text(self.output_frame, wrap=NONE)
        scrollbar_y = Scrollbar(self.output_frame, orient=VERTICAL, command=text_widget.yview)
        scrollbar_x = Scrollbar(self.output_frame, orient=HORIZONTAL, command=text_widget.xview)
        text_widget.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        text_widget.pack(fill=BOTH, expand=True, side=LEFT)
        scrollbar_y.pack(fill=Y, side=RIGHT)
        scrollbar_x.pack(fill=X, side=BOTTOM)

        # --- Numeric summary reflecting aggregation ---
        if self.numeric_cols:
            text_widget.insert(END, "=== Numeric Summary ===\n")

            # Use aggregation dropdown for numeric summary
            agg_method = self.agg_dropdown.get()
            group_col = self.x_dropdown.get() if self.x_dropdown.get() else None

            summary = numeric_summary(
                df_filtered,
                self.numeric_cols,
                agg_method=agg_method,
                group_col=group_col
            )

            # Display the summary table
            text_widget.insert(END, summary.to_string() + "\n\n")

        # --- Categorical summary (excluding selected fields) ---
        categorical_cols = [
            c for c in df_filtered.columns
            if c not in self.numeric_cols and c not in self.categorical_summary_exclude
        ]
        if categorical_cols:
            text_widget.insert(END, "=== Categorical Summary ===\n")
            for col in categorical_cols:
                text_widget.insert(END, f"{col} value counts:\n")
                counts = df_filtered[col].value_counts().head(20)  # top 20 only
                text_widget.insert(END, counts.to_string() + "\n\n")

        text_widget.config(state=DISABLED)


# Run the app
if __name__ == "__main__":
    root = Tk()
    app = PrescribingDataGUI(root)
    root.mainloop()