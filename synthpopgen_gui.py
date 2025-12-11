import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import pandas as pd
from collections import defaultdict

# import your functions from synthpopgen.py
from synthpopgen import syntheticextraction, parse_filter


class SynthPopGUI(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Synthetic Population Generator - Demo")
        self.geometry("900x600")

        # --- Input file ---
        tk.Label(self, text="Input CSV file (; separated):").grid(
            row=0, column=0, sticky="w", padx=5, pady=5
        )
        self.input_entry = tk.Entry(self, width=60)
        self.input_entry.grid(row=0, column=1, padx=5, pady=5, sticky="we")
        tk.Button(self, text="Browse...", command=self.browse_input).grid(
            row=0, column=2, padx=5, pady=5
        )

        # --- Filter string ---
        tk.Label(
            self,
            text="Filter (e.g. all or gender:male,age:30,hf:no):",
        ).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.filter_entry = tk.Entry(self, width=60)
        self.filter_entry.insert(0, "all")
        self.filter_entry.grid(
            row=1, column=1, padx=5, pady=5, sticky="we", columnspan=2
        )

        # --- Display mode ---
        tk.Label(self, text="Display mode:").grid(
            row=2, column=0, sticky="w", padx=5, pady=5
        )
        self.display_var = tk.StringVar(value="split")
        tk.Radiobutton(
            self, text="split", variable=self.display_var, value="split"
        ).grid(row=2, column=1, sticky="w")
        tk.Radiobutton(
            self, text="aggregate", variable=self.display_var, value="aggregate"
        ).grid(row=2, column=1, sticky="w", padx=80)

        # --- Output file (optional) ---
        tk.Label(self, text="Output CSV file (optional):").grid(
            row=3, column=0, sticky="w", padx=5, pady=5
        )
        self.output_entry = tk.Entry(self, width=60)
        self.output_entry.grid(row=3, column=1, padx=5, pady=5, sticky="we")
        tk.Button(self, text="Browse...", command=self.browse_output).grid(
            row=3, column=2, padx=5, pady=5
        )

        # --- Run button ---
        tk.Button(
            self,
            text="Run synthetic extraction",
            command=self.run_synthetic,
        ).grid(row=4, column=0, columnspan=3, pady=10)

        # --- Variables and conditions area ---
        tk.Label(self, text="Detected variables, conditions, and conditionals:").grid(
            row=5, column=0, sticky="w", padx=5, pady=(10, 0)
        )
        self.vars_text = scrolledtext.ScrolledText(self, wrap=tk.WORD, height=10)
        self.vars_text.grid(
            row=6, column=0, columnspan=3, padx=5, pady=5, sticky="nsew"
        )

        # --- Output preview area ---
        tk.Label(self, text="Output preview:").grid(
            row=7, column=0, sticky="w", padx=5, pady=(10, 0)
        )
        self.output_text = scrolledtext.ScrolledText(self, wrap=tk.NONE, height=10)
        self.output_text.grid(
            row=8, column=0, columnspan=3, padx=5, pady=5, sticky="nsew"
        )

        # Make main text areas expandable
        self.grid_rowconfigure(6, weight=1)
        self.grid_rowconfigure(8, weight=1)
        self.grid_columnconfigure(1, weight=1)

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

            # Inspect dataset (variables, conditions, and conditionals)
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
        """Read the CSV and show variables, their conditions,
        and the joint conditionals (like age_hpt, age_hf, etc.)."""
        input_path = self.input_entry.get().strip()
        if not input_path:
            return

        try:
            # Read everything as string for inspection
            df = pd.read_csv(input_path, delimiter=";", dtype=str)
        except Exception as e:
            self.vars_text.delete("1.0", tk.END)
            self.vars_text.insert(tk.END, f"Error reading file:\n{e}")
            return

        # Variables = all columns except 'value' (case-insensitive)
        dimension_cols = [c for c in df.columns if c.lower() != "value"]

        self.vars_text.delete("1.0", tk.END)

        if not dimension_cols:
            self.vars_text.insert(
                tk.END, "No variables found (only 'value' column present?)."
            )
            return

        # ---- Part 1: variables and their conditions ----
        self.vars_text.insert(
            tk.END, "Variables detected (excluding 'value') and their conditions:\n"
        )

        for col in dimension_cols:
            uniques = sorted(df[col].dropna().unique().tolist())

            max_show = 30
            if len(uniques) > max_show:
                display_vals = uniques[:max_show] + [
                    f"... (+{len(uniques) - max_show} more)"
                ]
            else:
                display_vals = uniques

            self.vars_text.insert(
                tk.END,
                f"- {col}:\n    {', '.join(map(str, display_vals))}\n",
            )

        # ---- Part 2: conditionals / joint distributions (joint_list analogue) ----
        # Reproduce the logic from synthpopgen: joints are rows where
        # two or more dimensions are non-empty.
        df_tmp = df.copy()
        # Count non-NA across dimension columns
        df_tmp["n_active_dims"] = df_tmp[dimension_cols].notna().sum(axis=1)
        joints = df_tmp[df_tmp["n_active_dims"] >= 2].copy()

        # Build joint_distributions keys by active dimension tuple
        joint_distributions = {}

        for _, row in joints.iterrows():
            active_dims = []
            for dim in dimension_cols:
                val = row[dim]
                if pd.notna(val) and str(val).strip() != "":
                    active_dims.append(dim)

            if len(active_dims) >= 2:
                dims_tuple = tuple(active_dims)
                # We don't need values here, just the structure,
                # so we can store a dummy True or skip values entirely.
                joint_distributions.setdefault(dims_tuple, True)

        # Group joints by base dimension (first dim in the tuple),
        # this corresponds to joint_groups_by_base and joint_list in synthpopgen.py
        joint_groups_by_base = defaultdict(list)
        for joint_dims in joint_distributions.keys():
            if len(joint_dims) >= 2:
                base = joint_dims[0]
                if joint_dims not in joint_groups_by_base[base]:
                    joint_groups_by_base[base].append(joint_dims)

        self.vars_text.insert(
            tk.END,
            "----------------------------------------\n"
            "Conditionals / joint distributions identified:\n",
        )

        if not joint_groups_by_base:
            self.vars_text.insert(
                tk.END,
                "No joint distributions detected (no rows with 2+ active dimensions).\n",
            )
        else:
            for base, joint_list in joint_groups_by_base.items():
                combos = ["_".join(j) for j in joint_list]
                self.vars_text.insert(
                    tk.END,
                    f"- Base variable: {base}\n"
                    f"  Joint combinations: {', '.join(combos)}\n",
                )

    # ------------------------
    # Run synthetic extraction
    # ------------------------
    def run_synthetic(self):
        input_path = self.input_entry.get().strip()
        filter_str = self.filter_entry.get().strip() or "all"
        display_mode = self.display_var.get()
        output_path = self.output_entry.get().strip() or None

        if not input_path:
            messagebox.showerror("Error", "Please select an input CSV file.")
            return

        try:
            # Read the tuple-based CSV file as in CLI
            df_tuples = pd.read_csv(input_path, delimiter=";", dtype=str)

            # ensure 'value' is numeric
            if "value" not in df_tuples.columns:
                raise ValueError(
                    "Input CSV must contain a 'value' column with counts."
                )
            df_tuples["value"] = pd.to_numeric(df_tuples["value"])

            # Parse filter using your existing logic
            target_components = parse_filter(filter_str, df_tuples)

            # Run synthetic extraction
            synthetic_df = syntheticextraction(
                df_tuples, target_components, display_mode=display_mode
            )

            # Save if requested
            if output_path:
                synthetic_df.to_csv(output_path, index=False, sep=";")

            # Show preview
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(
                tk.END, f"Rows: {len(synthetic_df)}\n"
            )
            # Show first 50 rows as CSV-like text
            self.output_text.insert(
                tk.END, synthetic_df.head(50).to_csv(index=False, sep=";")
            )

            msg = f"Completed. Generated {len(synthetic_df)} rows."
            if output_path:
                msg += f"\nSaved to: {output_path}"
            messagebox.showinfo("Success", msg)

        except FileNotFoundError:
            messagebox.showerror(
                "Error", f"Input file '{input_path}' not found."
            )
        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    app = SynthPopGUI()
    app.mainloop()