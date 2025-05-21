import tkinter as tk
import tkinter.ttk as ttk
# window = tk.Tk()
#label = tk.Label(window,
#    text="Hello, Tkinter",
#    fg="white",
#    bg="black",
#    width=10,
#    height=10
#)
#label.pack()

#button = tk.Button(window,
#    text="Click me!",
#    width=25,
#    height=5,
#    bg="blue",
#    fg="yellow",
#)
#button.pack()

#entry = tk.Entry(window,
#                 fg="yellow", bg="blue", width=50)
#entry.pack()

#label = tk.Label(window,text="Name")
#entry = tk.Entry(window)


#name = entry.get()
#name
#entry.delete(0)
#label.pack()
#entry.pack()

def get_name(event=None):  # Accept `event` for binding
    name = entry.get()
    print("Entered name:", name)
    label_result.config(text=f"Hello, {name}!")

window = tk.Tk()


label = tk.Label(window, text="Name")
entry = tk.Entry(window)
label_result = tk.Label(window)

label.pack()
entry.pack()
label_result.pack()

# Bind Enter key to the Entry field
entry.bind("<Return>", get_name)
window.destroy()
window.mainloop()

