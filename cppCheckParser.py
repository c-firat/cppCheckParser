import tkinter as tk
from tkinter import ttk, filedialog
import xml.etree.ElementTree as ET
import subprocess
import os

class XmlViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("XML Viewer")

        # Create Treeview widget
        self.tree = ttk.Treeview(root, columns=('ID', 'Severity', 'Message', 'Symbol', 'Location'))
        self.tree.heading('#0', text='Index')
        self.tree.heading('ID', text='ID')
        self.tree.heading('Severity', text='Severity')
        self.tree.heading('Message', text='Message')
        self.tree.heading('Symbol', text='Symbol')
        self.tree.heading('Location', text='Location')

        # Bind the double click event to open file and line
        self.tree.bind('<Double-1>', self.open_location)

        self.tree.pack(expand=tk.YES, fill=tk.BOTH)

        # Ask user to choose XML file
        self.load_xml()

    def load_xml(self):
        file_path = filedialog.askopenfilename(filetypes=[('XML files', '*.xml')])

        if file_path:
            # Parse the XML file
            tree = ET.parse(file_path)
            root = tree.getroot()

            # Extract information and populate the Treeview
            for index, error in enumerate(root.findall('.//error')):
                error_id = error.get('id')
                severity = error.get('severity')
                msg = error.get('msg')

                # Check if location_element is not None
                location_element = error.find('location')
                if location_element is not None:
                    location = {
                        'file': location_element.get('file', ''),
                        'line': location_element.get('line', ''),
                        'column': location_element.get('column', '')
                    }
                else:
                    location = {'file': '', 'line': '', 'column': ''}

                # Check if location_element is not None
                symbol_element = error.find('symbol')
                symbol = symbol_element.text if symbol_element is not None else ''

                item_id = 'item{}'.format(index)  # Use a string identifier for the item
                self.tree.insert('', 'end', item_id, text=str(index), values=(error_id, severity, msg, symbol))
                self.tree.set(item_id, 'Location', str(location))

    def open_location(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            location_str = self.tree.item(selected_item, 'values')[4]
            try:
                location_dict = eval(location_str)  # Convert the string representation to a dictionary
            except Exception as e:
                print(f"Error converting 'Location' string to dictionary: {e}")
                return

            if 'file' in location_dict and 'line' in location_dict:
                file_path = location_dict['file']
                line_number = location_dict['line']
                print(file_path)
                try:
                    # Try opening with Visual Studio Code
                    subprocess.run(['code', '--goto', '{}:{}:{}'.format(os.path.relpath(file_path, start='~/..'), line_number, 1)], check=True)
                except subprocess.CalledProcessError:
                    print('Failed to open with Visual Studio Code.')

if __name__ == "__main__":
    root = tk.Tk()
    app = XmlViewer(root)
    root.mainloop()
