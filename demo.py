import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import csv
import matplotlib.pyplot as plt

window = tk.Tk()
window.title("Synthetic Populations Generator")
window.geometry("700x700")

welcome_label = tk.Label(window, text="Benvenut* in Synthetic Populations Generator!\n Posso aiutarti integrando dati sulla popolazione che ti interessa", font=("Arial", 12), wraplength=500, justify="center")
welcome_label.pack(pady=10)

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

        uploaded_variables = tk.Label(window, text="Queste sono le informazioni correnti su cui lavorerò", font=("Arial", 12), wraplength=500, justify="center")
        uploaded_variables.pack(pady=10)


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
        compute_button = tk.Button(window, text="Calcola e salva in CSV", command=compute_and_save)
        compute_button.place(relx=0.75, rely=0.2, anchor='center')
#        compute_button.pack(pady=10)

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
        TGTHPT =  values['TGTHPT']
        TGTHF = values['TGTHF']
        TGT0_30HPT = values['TGT0_30HPT']
        TGT30_60HPT = values['TGT30_60HPT']
        TGT60_100HPT = values['TGT60_100HPT']
        TGT0_30HF = values['TGT0_30HF']
        TGT30_60HF = values['TGT30_60HF']
        TGT60_100HF = values['TGT60_100HF']

# computation

        total = TGTmale + TGTfemale
        male30 = round((TGTmale / total) * TGT0_30)
        male60 = round((TGTmale / total) * TGT30_60)
        male100 = round((TGTmale / total) * TGT60_100)
        female30 = round((TGTfemale / total) * TGT0_30)
        female60 =  round((TGTfemale / total) * TGT30_60)
        female100 = round((TGTfemale / total) * TGT60_100)
        maleHPT = round((TGTmale / total) * TGTHPT)
        femaleHPT =  round((TGTfemale / total) * TGTHPT)
        maleHF =   round((TGTmale / total) * TGTHF)
        femaleHF = round((TGTfemale / total) * TGTHF)
        maleHPT30 =  round((maleHPT / (maleHPT + femaleHPT)) *  TGT0_30HPT)
        maleHPT60 = round((maleHPT / (maleHPT + femaleHPT)) *  TGT30_60HPT)
        maleHPT100 =  round((maleHPT / (maleHPT + femaleHPT)) *  TGT60_100HPT)
        femaleHPT30 = round((femaleHPT / (maleHPT + femaleHPT)) *  TGT0_30HPT)
        femaleHPT60 =  round((femaleHPT / (maleHPT + femaleHPT)) *  TGT30_60HPT)
        femaleHPT100 =   round((femaleHPT / (maleHPT + femaleHPT)) *  TGT60_100HPT)
        maleHF30 =   round((maleHF / (maleHF + femaleHF)) * TGT0_30HF) 
        maleHF60 =  round((maleHF / (maleHF + femaleHF)) * TGT30_60HF)
        maleHF100 =    round((maleHF / (maleHF + femaleHF)) * TGT60_100HF)
        femaleHF30 =   round((femaleHF / (maleHF + femaleHF)) * TGT0_30HF)
        femaleHF60 =  round((femaleHF / (maleHF + femaleHF)) * TGT30_60HF)
        femaleHF100 =  round((femaleHF / (maleHF + femaleHF)) * TGT60_100HF)

        male_HF_HPT_30 = round( total * ((male30 / total) * ((maleHPT30 / male30) * (maleHF30 / male30))) )
        male_HF_HPT_60 = round( total * ((male60 / total) * ((maleHPT60 / male60) * (maleHF60 / male60))) )
        male_HF_HPT_100 = round( total * ((male100 / total) * ((maleHPT100 / male100) * (maleHF100 / male100))) )
        
        female_HF_HPT_30 = round( total * ((female30 / total) * ((femaleHPT30 / female30) * (femaleHF30 / female30))) )
        female_HF_HPT_60 = round( total * ((female60 / total) * ((femaleHPT60 / female60) * (femaleHF60 / female60))) )
        female_HF_HPT_100 = round( total * ((female100 / total) * ((femaleHPT100 / female100) * (femaleHF100 / female100))) )
        

        results = {
            "male_0_30": male30,
            "male_30_60": male60,
            "male_60_100": male100,
            "female_0_30": female30,
            "female_30_60": female60,
            "female_60_100": female100,
            "male_hpt": maleHPT,
            "female_hpt": femaleHPT,
            "male_hf": maleHF ,
            "female_hf": femaleHF,
            "male_hpt_30": maleHPT30,
            "male_hpt_60": maleHPT60,
            "male_hpt_100": maleHPT100,
            "female_hpt_30": femaleHPT30,
            "female_hpt_60": femaleHPT60,
            "female_hpt_100": femaleHPT100,
            "male_hf_30": maleHF30 ,
            "male_hf_60": maleHF60,
            "male_hf_100": maleHF100,
            "female_hf_30": femaleHF30,
            "female_hf_60": femaleHF60,
            "female_hf_100": femaleHF100,
            "male_30_hpt_hf": male_HF_HPT_30,
            "male_60_hpt_hf": male_HF_HPT_60,
            "male_100_hpt_hf": male_HF_HPT_100,
            "female_30_hpt_hf": female_HF_HPT_30,
            "female_60_hpt_hf": female_HF_HPT_60,
            "female_100_hpt_hf": female_HF_HPT_100,
        }

        # Save results
        with open("risultati.csv", mode="w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Group", "Estimated Count"])
            for key, value in results.items():
                writer.writerow([key, value])

        messagebox.showinfo("Success", "Results saved to 'results.csv'.")
        
        def show_plot():
           
            labels = list(results.keys())
            values = list(results.values())

            fig, ax = plt.subplots(figsize=(12, 6))
            bars = ax.barh(labels, values)
            ax.set_xlabel("Estimated Count")
            ax.set_title("Synthetic Population Estimates")
            ax.get_xaxis().set_visible(False)
            for spine in ["top", "right", "bottom", "left"]:
                ax.spines[spine].set_visible(False)

    # Add value labels to the right of each bar
            for bar in bars:
                width = bar.get_width()
                ax.text(width + max(values) * 0.01, bar.get_y() + bar.get_height() / 2,
                f'{int(width)}', va='center', fontsize=8)

            plt.tight_layout()
            plt.show()
            
        plot_button = tk.Button(window, text="Visualizza i Risultati", command=show_plot)
        plot_button.place(relx=0.75, rely=0.5, anchor='center')


    except KeyError as e:
        messagebox.showerror("Missing Variable", f"Missing variable: {e}")
    except ValueError:
        messagebox.showerror("Invalid Input", "All values must be valid integers.")
    except Exception as e:
        messagebox.showerror("Error", str(e))
        
        
# Upload button
upload_button = tk.Button(window, text="Mi serve un CSV con Variable e Value della popolazione da sintetizzare", command=upload_csv)
upload_button.pack(pady=20)

            
window.mainloop()