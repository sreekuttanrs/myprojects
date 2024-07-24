import os
import socket
import tkinter as tk

def get_connected_networks():
    result = os.popen("iwlist scan | grep ESSID").read()
    return result

def get_own_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))  # Connect to a public IP address
    own_ip = s.getsockname()[0]
    s.close()
    return own_ip

def get_connected_wifi():
    result = os.popen("iwgetid -r").read()
    return result.strip()

def scan_network():
    result = os.popen("sudo arp-scan -l").read()
    return result

class NetworkScannerApp:
    def __init__(self, root):
        self.root = root
        root.title("Network Information Scanner")

        self.result_text = tk.Text(root, height=20, width=80)
        self.result_text.pack(pady=10)

        self.scan_button = tk.Button(root, text="Scan Network Information", command=self.scan_network_info)
        self.scan_button.pack(pady=10)

    def scan_network_info(self):
        own_ip = get_own_ip()
        connected_wifi = get_connected_wifi()
        networks_info = get_connected_networks()
        devices_info = scan_network()

        result = f"Your IP Address: {own_ip}\n"
        result += f"Connected Wi-Fi: {connected_wifi}\n\n"
        result += "Connected Networks:\n"
        result += networks_info + "\n\n"
        result += "Devices on the Same Network:\n"
        result += devices_info

        self.display_result(result)

    def display_result(self, result):
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, result)

if __name__ == "__main__":
    root = tk.Tk()
    app = NetworkScannerApp(root)
    root.mainloop()
