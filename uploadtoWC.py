import pysftp
import tkinter as tk
from tkinter import filedialog


cnopts = pysftp.CnOpts()


root = tk.Tk()
root.withdraw()
file_path = filedialog.askopenfilename(title='File to upload')

cnopts = pysftp.CnOpts()
cnopts.hostkeys = None

conn = pysftp.Connection('data.wellcentive.com', username='CHA_CHF', password='V37aPO2bJ6e5wFcLoL+V', cnopts=cnopts)

conn.put(file_path)
