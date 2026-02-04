import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

import pandas as pd
from collections import defaultdict

# Logo support (JPEG)
from PIL import Image, ImageTk

# Plotting
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt

# Import functions from synthpopgen.py (CLI parity)
from synthpopgen import (
    syntheticextraction,
    parse_filter,
    compute_rmse,
    compute_ape,
)


def _is_active_cell(v) -> bool:
    """True if a cell is not NA and not empty/whitespace."""
    return pd.notna(v) and str(v).strip() != ""


class SynthPopGUI(tk.Tk):
    """
    GUI aligned to synthpopgen.py + a button to save a barplot (percentages)
    from the extracted synthetic output.

    Barplot:
      - each row = one category
      - y = percentage share of 'value' (value / sum(value) * 100)
      - labels use 'combination' if present, else build from non-'value' columns
      - saves PNG next to output CSV (if specified) or in current working dir
    """

    def __init__(self):
        super().__init__()

        self.title("Synthetic Population Generator")
        self.geometry("1020x780")

        # Stored after running extraction (used by barplot)
        self.synthetic_df = None
        self.last_output_path = None

        # --- LOGO HEADER ---
        # Put the logo image in the same folder as this script, OR change this to an absolute path.
        logo_path = "FOSSR handbook-SPG_RP.jpeg"
        try:
            img = Image.open(logo_path)
            img = img.resize((420, 140))
            self.logo_img = ImageTk.PhotoImage(img)  # keep a reference!
            tk.Label(self, image=self.logo_img).grid(row=0, column=0, columnspan=3, pady=(10, 15))
        except Exception as e:
            print("Logo could not be loaded:", e)

        # --- Input file ---
        tk.Label(self, text="Input CSV file (; separated):").grid(
            row=1, column=0, sticky="w", padx=5, pady=5
        )
        self.input_entry = tk.Entry(self, width=70)
        self.input_entry.grid(row=1, column=1, padx=5, pady=5, sticky="we")
        tk.Button(self, text="Browse...", command=self.browse_input).grid(
            row=1, column=2, padx=5, pady=5
        )

        # --- Filter string ---
        tk.Label(self, text="Filter (e.g. all or gender:male,age:30,hf:no)").grid(
            row=2, column=0, sticky="w", padx=5, pady=5
        )
        self.filter_entry = tk.Entry(self, width=70)
        self.filter_entry.insert(0, "all")
        self.filter_entry.grid(row=2, column=1, padx=5, pady=5, sticky="we", columnspan=2)
        self.filter_entry.bind("<KeyRelease>", lambda _e: self._sync_options_state())

        # --- Display mode ---
        tk.Label(self, text="Subcategories split or aggregated:").grid(
            row=3, column=0, sticky="w", padx=5, pady=5
        )
        self.display_var = tk.StringVar(value="split")
        tk.Radiobutton(self, text="split", variable=self.display_var, value="split").grid(
            row=3, column=1, sticky="w"
        )
        tk.Radiobutton(self, text="aggregate", variable=self.display_var, value="aggregate").grid(
            row=3, column=1, sticky="w", padx=90
        )

        # --- Validation options ---
        tk.Label(self, text="Validation (only with filter=all):").grid(
            row=4, column=0, sticky="w", padx=5, pady=5
        )
        self.validate_var = tk.BooleanVar(value=False)
        self.validate_check = tk.Checkbutton(
            self, text="Enable RMSE + APE", variable=self.validate_var, command=self._sync_options_state
        )
        self.validate_check.grid(row=4, column=1, sticky="w")

        tk.Label(self, text="Basename:").grid(row=4, column=1, sticky="w", padx=(220, 0))
        self.validate_base_entry = tk.Entry(self, width=18)
        self.validate_base_entry.insert(0, "validation")
        self.validate_base_entry.grid(row=4, column=1, sticky="w", padx=(290, 0))

        # --- synth-total option ---
        tk.Label(self, text="Synthetic total (only with filter=all):").grid(
            row=5, column=0, sticky="w", padx=5, pady=5
        )
        self.synth_total_entry = tk.Entry(self, width=20)
        self.synth_total_entry.grid(row=5, column=1, sticky="w")
        tk.Label(self, text="(leave blank to use inferred total)").grid(
            row=5, column=1, sticky="w", padx=(180, 0)
        )
        self.synth_total_entry.bind("<KeyRelease>", lambda _e: self._sync_options_state())

        # --- Output file (optional) ---
        tk.Label(self, text="Output CSV file (optional):").grid(
            row=6, column=0, sticky="w", padx=5, pady=5
        )
        self.output_entry = tk.Entry(self, width=70)
        self.output_entry.grid(row=6, column=1, padx=5, pady=5, sticky="we")
        tk.Button(self, text="Browse...", command=self.browse_output).grid(
            row=6, column=2, padx=5, pady=5
        )

        # --- Run button ---
        tk.Button(
            self,
            text="Run synthetic extraction",
            command=self.run_synthetic,
        ).grid(row=7, column=0, columnspan=3, pady=10)

        # --- Variables / inspection area ---
        tk.Label(self, text="Detected variables, categories, and joint structures:").grid(
            row=8, column=0, sticky="w", padx=5, pady=(10, 0)
        )
        self.vars_text = scrolledtext.ScrolledText(self, wrap=tk.WORD, height=10)
        self.vars_text.grid(row=9, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")

        # --- Output preview area ---
        tk.Label(self, text="Output preview:").grid(
            row=10, column=0, sticky="w", padx=5, pady=(10, 0)
        )
        self.output_text = scrolledtext.ScrolledText(self, wrap=tk.NONE, height=12)
        self.output_text.grid(row=11, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")

        # --- Barplot button (percent share of value) ---
        tk.Button(
            self,
            text='Generate barplot (% share)',
            command=self.generate_and_save_barplot_percent,
        ).grid(row=12, column=0, columnspan=3, pady=(10, 5))

        # Expand layout: give space to the scrolled text widgets
        self.grid_rowconfigure(9, weight=1)
        self.grid_rowconfigure(11, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self._sync_options_state()

    # ------------------------
    # UI helpers
    # ------------------------
    def _sync_options_state(self):
        """
        Keep GUI options aligned with CLI guardrails:
        - validate only when Filter == all
        - synth-total only when Filter == all
        - validate and synth-total cannot be both active
        """
        filter_str = (self.filter_entry.get() or "").strip().lower()
        is_all = (filter_str == "all")

        self.validate_check.configure(state=("normal" if is_all else "disabled"))
        self.validate_base_entry.configure(state=("normal" if (is_all and self.validate_var.get()) else "disabled"))

        self.synth_total_entry.configure(state=("normal" if is_all else "disabled"))

        if not is_all:
            self.validate_var.set(False)
            self.validate_base_entry.configure(state="disabled")
            self.synth_total_entry.delete(0, tk.END)

        if self.validate_var.get():
            self.synth_total_entry.configure(state="disabled")

        if is_all and (self.synth_total_entry.get() or "").strip() != "":
            if self.validate_var.get():
                self.validate_var.set(False)
                self.validate_base_entry.configure(state="disabled")
            self.validate_check.configure(state="disabled")
        else:
            if is_all:
                self.validate_check.configure(state="normal")

    # ------------------------
    # File selection handlers
    # ------------------------
    def browse_input(self):
        filename = filedialog.askopenfilename(
            title="Select input CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if filename:
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, filename)
            self.inspect_dataset()

    def browse_output(self):
        filename = filedialog.asksaveasfilename(
            title="Save output CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if filename:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, filename)

    # ------------------------
    # Dataset inspection
    # ------------------------
    def inspect_dataset(self):
        """Read the CSV and show variables, their conditions, and joint dimension-keys."""
        input_path = self.input_entry.get().strip()
        if not input_path:
            return

        self.vars_text.delete("1.0", tk.END)

        try:
            df = pd.read_csv(input_path, delimiter=";", dtype=str)
        except Exception as e:
            self.vars_text.insert(tk.END, f"Error reading file:\n{e}")
            return

        dimension_cols = [c for c in df.columns if c.lower() != "value"]

        if not dimension_cols:
            self.vars_text.insert(tk.END, "No variables found (only 'value' column present?).")
            return

        self.vars_text.insert(tk.END, "Variables detected (excluding 'value') and their conditions:\n\n")

        for col in dimension_cols:
            uniques = df[col].dropna().map(lambda x: str(x).strip())
            uniques = sorted([u for u in uniques.unique().tolist() if u != ""])

            max_show = 40
            if len(uniques) > max_show:
                display_vals = uniques[:max_show] + [f"... (+{len(uniques) - max_show} more)"]
            else:
                display_vals = uniques

            self.vars_text.insert(tk.END, f"- {col}:\n    {', '.join(map(str, display_vals))}\n\n")

        # Joint structures: rows with >= 2 active dims
        df_tmp = df.copy()
        df_tmp["n_active_dims"] = df_tmp[dimension_cols].apply(
            lambda r: sum(_is_active_cell(r[c]) for c in dimension_cols), axis=1
        )
        joints = df_tmp[df_tmp["n_active_dims"] >= 2].copy()

        joint_distributions = {}
        for _, row in joints.iterrows():
            active_dims = [dim for dim in dimension_cols if _is_active_cell(row[dim])]
            if len(active_dims) >= 2:
                joint_distributions.setdefault(tuple(active_dims), True)

        joint_groups_by_base = defaultdict(list)
        for joint_dims in joint_distributions.keys():
            base = joint_dims[0]
            if joint_dims not in joint_groups_by_base[base]:
                joint_groups_by_base[base].append(joint_dims)

        self.vars_text.insert(
            tk.END,
            "----------------------------------------\n"
            "Joint structures identified:\n\n",
        )

        if not joint_groups_by_base:
            self.vars_text.insert(tk.END, "No joint structures detected (no rows with 2+ active dimensions).\n")
        else:
            for base, joint_list in joint_groups_by_base.items():
                combos = ["_".join(j) for j in joint_list]
                self.vars_text.insert(
                    tk.END,
                    f"- Base variable: {base}\n"
                    f"  Joint combinations: {', '.join(combos)}\n\n",
                )

    # ------------------------
    # Run synthetic extraction
    # ------------------------
    def run_synthetic(self):
        input_path = self.input_entry.get().strip()
        filter_str = (self.filter_entry.get().strip() or "all")
        display_mode = self.display_var.get()
        output_path = self.output_entry.get().strip() or None

        validate_enabled = bool(self.validate_var.get())
        validate_base = (self.validate_base_entry.get().strip() or "validation")
        synth_total_str = (
            self.synth_total_entry.get().strip()
            if self.synth_total_entry.cget("state") != "disabled"
            else ""
        )
        synth_total = None

        if not input_path:
            messagebox.showerror("Error", "Please select an input CSV file.")
            return

        if validate_enabled and filter_str.lower() != "all":
            messagebox.showerror("Error", 'Validation can only be used together with filter="all".')
            return

        if synth_total_str and filter_str.lower() != "all":
            messagebox.showerror("Error", 'Synthetic total can only be used together with filter="all".')
            return

        if validate_enabled and synth_total_str:
            messagebox.showerror("Error", "Validation cannot be used together with a synthetic total.")
            return

        if synth_total_str:
            try:
                synth_total = int(synth_total_str)
                if synth_total < 0:
                    raise ValueError
            except Exception:
                messagebox.showerror("Error", "Synthetic total must be a non-negative integer.")
                return

        try:
            df_tuples = pd.read_csv(input_path, delimiter=";", dtype=str)

            if "value" not in df_tuples.columns:
                raise ValueError("Input CSV must contain a 'value' column with counts.")
            df_tuples["value"] = pd.to_numeric(df_tuples["value"])

            target_components = parse_filter(filter_str, df_tuples)

            synthetic_df = syntheticextraction(
                df_tuples,
                target_components,
                display_mode=display_mode,
                synth_total=synth_total,
            )

            # Store for barplot generation
            self.synthetic_df = synthetic_df.copy()
            self.last_output_path = output_path

            validation_summary_lines = []
            if validate_enabled:
                rmse = compute_rmse(df_tuples, synthetic_df)
                ape_df = compute_ape(df_tuples, synthetic_df)

                base = validate_base.strip() if validate_base.strip() else "validation"
                base = base.rsplit(".", 1)[0]

                out_dir = os.path.dirname(output_path) if output_path else os.getcwd()
                rmse_path = os.path.join(out_dir, f"{base}_RMSE.csv")
                ape_path = os.path.join(out_dir, f"{base}_APE.csv")

                rmse_df = pd.DataFrame([{
                    "metric": "RMSE",
                    "value": rmse,
                    "n_constraints": len(df_tuples)
                }])
                rmse_df.to_csv(rmse_path, index=False, sep=";")
                ape_df.to_csv(ape_path, index=False, sep=";")

                validation_summary_lines.append("Validation saved:")
                validation_summary_lines.append(f"  - RMSE: {rmse_path}")
                validation_summary_lines.append(f"  - APE : {ape_path}")
                validation_summary_lines.append(f"RMSE value: {rmse}")

            if output_path:
                synthetic_df.to_csv(output_path, index=False, sep=";")

            # Output preview
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, f"Rows generated: {len(synthetic_df)}\n")
            if output_path:
                self.output_text.insert(tk.END, f"Output saved to: {output_path}\n")
            if synth_total is not None:
                self.output_text.insert(tk.END, f"Synthetic total requested: {synth_total}\n")

            self.output_text.insert(tk.END, "\n--- Preview (first 50 rows) ---\n")
            self.output_text.insert(tk.END, synthetic_df.head(50).to_csv(index=False, sep=";"))

            if validation_summary_lines:
                self.output_text.insert(tk.END, "\n\n--- Validation ---\n")
                self.output_text.insert(tk.END, "\n".join(validation_summary_lines) + "\n")

#            messagebox.showinfo("Success", f"Completed. Generated {len(synthetic_df)} rows.")

        except FileNotFoundError:
            messagebox.showerror("Error", f"Input file '{input_path}' not found.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ------------------------
    # Percent barplot from synthetic output
    # ------------------------
    def generate_and_save_barplot_percent(self):
        """
        Barplot from the last synthetic output:

          - each row = one category
          - y-axis = percentage share of 'value'
          - x labels = 'combination' if present, otherwise built from all non-'value' columns

        Saves ONLY:
          - PNG: *_barplot_percent.png
        """
        if self.synthetic_df is None or len(self.synthetic_df) == 0:
            messagebox.showerror("Error", "No synthetic data available. Run extraction first.")
            return

        df = self.synthetic_df.copy()

        if "value" not in df.columns:
            messagebox.showerror("Error", "Synthetic output does not contain a 'value' column.")
            return

        # Labels
        if "combination" in df.columns:
            labels = df["combination"].astype(str).tolist()
            label_name = "combination"
        else:
            dim_cols = [c for c in df.columns if c != "value"]
            if not dim_cols:
                messagebox.showerror("Error", "No category columns found (only 'value' exists).")
                return

            def make_label(row):
                parts = []
                for c in dim_cols:
                    v = row[c]
                    if pd.notna(v) and str(v).strip() != "":
                        parts.append(f"{c}={str(v).strip()}")
                return "|".join(parts) if parts else "(empty)"

            labels = df.apply(make_label, axis=1).tolist()
            label_name = "dimensions"

        values = pd.to_numeric(df["value"], errors="coerce").fillna(0.0)
        total = float(values.sum())
        if total <= 0:
            messagebox.showerror("Error", "Sum of 'value' is 0; cannot compute percentages.")
            return

        percentages = (values / total) * 100.0

        # Save location
        if self.last_output_path:
            out_dir = os.path.dirname(self.last_output_path) or os.getcwd()
            base = os.path.splitext(os.path.basename(self.last_output_path))[0]
        else:
            out_dir = os.getcwd()
            base = "synthetic_output"

        png_path = os.path.join(out_dir, f"{base}_barplot_percent.png")

        # Plot (one bar per row)
        n = len(labels)
        fig_w = min(40, max(12, n * 0.35))
        fig_h = 6

        fig = plt.figure(figsize=(fig_w, fig_h))
        ax = fig.add_subplot(111)

        ax.bar(labels, percentages.tolist())
        ax.set_title("Synthetic barplot (% share)")
        ax.set_ylabel("% of total")

        ax.tick_params(axis="x", labelrotation=270)
        for t in ax.get_xticklabels():
            t.set_fontsize(8)

        fig.tight_layout()

        try:
            fig.savefig(png_path, dpi=200)
        except Exception as e:
            plt.close(fig)
            messagebox.showerror("Error", f"Failed to save PNG:\n{e}")
            return

        plt.close(fig)
#        messagebox.showinfo("Saved", f"Barplot saved successfully:\n\n{png_path}")


if __name__ == "__main__":
    app = SynthPopGUI()
    app.mainloop()
