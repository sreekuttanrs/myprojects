import os
import tkinter as tk
from tkinter import scrolledtext

class NmapScannerApp:
    def __init__(self, root):
        self.root = root
        root.title("Nmap Scanner")

        self.ip_label = tk.Label(root, text="Enter IP Address:")
        self.ip_label.pack(pady=10)

        self.ip_entry = tk.Entry(root)
        self.ip_entry.pack(pady=10)

        self.scan_button = tk.Button(root, text="Scan", command=self.scan_ip)
        self.scan_button.pack(pady=10)

        self.result_text = scrolledtext.ScrolledText(root, height=15, width=50)
        self.result_text.pack(pady=10)

    def scan_ip(self):
        ip_address = self.ip_entry.get()
        if ip_address:
            result = self.run_nmap(ip_address)
            self.display_result(result)
        else:
            self.display_result("Please enter an IP address.")

    def run_nmap(self, ip_address):
        command = f"nmap {ip_address}"
        result = os.popen(command).read()
        return result

    def display_result(self, result):
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, result)

if __name__ == "__main__":
    root = tk.Tk()
    app = NmapScannerApp(root)
    root.mainloop()
