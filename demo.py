import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import csv

window = tk.Tk()
window.title("CSV Variable Entry + Computation")
window.geometry("400x500")

entries = {}

def upload_csv():
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if not file_path:
        return

    try:
        df = pd.read_csv(file_path, delimiter = ";")

        if 'variable' not in df.columns or 'value' not in df.columns:
            messagebox.showerror("Error", "CSV must contain 'variable' and 'value' columns.")
            return

        # Clear previous entries
        for widget in window.winfo_children():
            if isinstance(widget, tk.Entry) or isinstance(widget, tk.Label):
                widget.destroy()
        entries.clear()

        # Generate input fields
        for _, row in df.iterrows():
            var = row['variable']
            val = row['value']
            label = tk.Label(window, text=var)
            label.pack()
            entry = tk.Entry(window)
            entry.insert(0, str(val))  # Pre-fill with CSV value
            entry.pack()
            entries[var] = entry

        # Add compute button
        compute_button = tk.Button(window, text="Compute and Save to CSV", command=compute_and_save)
        compute_button.pack(pady=10)

    except Exception as e:
        messagebox.showerror("Error", f"Failed to load file:\n{e}")

def compute_and_save():
    try:
        # Retrieve values from entries
        values = {var: int(entry.get()) for var, entry in entries.items()}

        # Required variable access
        TGTmale = values['TGTmale']
        TGTfemale = values['TGTfemale']
        TGT0_30 = values['TGT0_30']
        TGT30_60 = values['TGT30_60']
        TGT60_100 = values['TGT60_100']

        total = TGTmale + TGTfemale

        results = {
            "male_0_30": round((TGTmale / total) * TGT0_30),
            "male_30_60": round((TGTmale / total) * TGT30_60),
            "male_60_100": round((TGTmale / total) * TGT60_100),
            "female_0_30": round((TGTfemale / total) * TGT0_30),
            "female_30_60": round((TGTfemale / total) * TGT30_60),
            "female_60_100": round((TGTfemale / total) * TGT60_100),
        }

        # Save results
        with open("results.csv", mode="w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Group", "Estimated Count"])
            for key, value in results.items():
                writer.writerow([key, value])

        messagebox.showinfo("Success", "Results saved to 'results.csv'.")

    except KeyError as e:
        messagebox.showerror("Missing Variable", f"Missing variable: {e}")
    except ValueError:
        messagebox.showerror("Invalid Input", "All values must be valid integers.")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Upload button
upload_button = tk.Button(window, text="Upload CSV with Variables and Values", command=upload_csv)
upload_button.pack(pady=20)

window.mainloop()