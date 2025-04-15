import tkinter as tk
from tkinter import messagebox, ttk
import json
import os

BUGGY_FILE = "buggy_profiles.json"

# Load buggy profiles from JSON
def load_buggies():
    if not os.path.exists(BUGGY_FILE):
        return {}
    with open(BUGGY_FILE, "r") as f:
        return json.load(f)

def save_buggies(data):
    with open(BUGGY_FILE, "w") as f:
        json.dump(data, f, indent=2)

class BuggyEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Buggy Profile Editor")
        self.buggies = load_buggies()
        self.current_buggy_key = None

        self.buggy_listbox = tk.Listbox(root, width=30)
        self.buggy_listbox.pack(side=tk.LEFT, fill=tk.Y)
        self.buggy_listbox.bind("<<ListboxSelect>>", self.load_buggy_fields)

        self.form_frame = tk.Frame(root)
        self.form_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.form_widgets = {}
        self.build_form()

        self.btn_frame = tk.Frame(root)
        self.btn_frame.pack(fill=tk.X)

        tk.Button(self.btn_frame, text="Save", command=self.save_buggy).pack(side=tk.LEFT)
        tk.Button(self.btn_frame, text="Delete", command=self.delete_buggy).pack(side=tk.LEFT)
        tk.Button(self.btn_frame, text="New Buggy", command=self.new_buggy).pack(side=tk.LEFT)

        self.refresh_buggy_list()

    def build_form(self):
        sections = [
            "motor", "gearbox", "wheel", "buggy", "battery", "sensor_array"
        ]
        self.name_entry = self.create_labeled_entry(self.form_frame, "Name")

        self.section_vars = {}
        for section in sections:
            label = tk.Label(self.form_frame, text=f"{section.upper()}", font=("Arial", 10, "bold"))
            label.pack(pady=5)

            section_dict = {}
            if section == "sensor_array":
                sensor_count = self.create_labeled_entry(self.form_frame, f"{section}_sensor_count")
                section_dict["sensor_count"] = sensor_count

                coords_label = tk.Label(self.form_frame, text="Sensor Coordinates (comma-separated x,y per line):")
                coords_label.pack()
                coords_text = tk.Text(self.form_frame, height=5, width=40)
                coords_text.pack()
                section_dict["sensor_coordinates"] = coords_text
            else:
                if section == "motor":
                    for field in ["armature_resistance", "brush_voltage", "torque_constant", "emf_constant", "motor_max_current", "motor_inertia"]:
                        section_dict[field] = self.create_labeled_entry(self.form_frame, f"{section}_{field}")
                # Add custom fields
                if section == "gearbox":
                    for field in ["gear_ratio", "gearbox_efficiency", "gearbox_inertia"]:
                        section_dict[field] = self.create_labeled_entry(self.form_frame, f"{section}_{field}")
                elif section == "wheel":
                    for field in ["wheel_radius", "wheel_inertia"]:
                        section_dict[field] = self.create_labeled_entry(self.form_frame, f"{section}_{field}")
                elif section == "buggy":
                    for field in ["weight", "track_width", "friction_coefficient", "buggy_innertia"]:
                        section_dict[field] = self.create_labeled_entry(self.form_frame, f"{section}_{field}")
                elif section == "battery":
                    for field in ["nominal_voltage", "internal_resistance"]:
                        section_dict[field] = self.create_labeled_entry(self.form_frame, f"{section}_{field}")
            self.section_vars[section] = section_dict

    def create_labeled_entry(self, parent, label_text):
        frame = tk.Frame(parent)
        frame.pack(fill=tk.X, padx=5, pady=2)
        label = tk.Label(frame, text=label_text, width=25, anchor='w')
        label.pack(side=tk.LEFT)
        entry = tk.Entry(frame)
        entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        return entry

    def refresh_buggy_list(self):
        self.buggy_listbox.delete(0, tk.END)
        for key in self.buggies.keys():
            self.buggy_listbox.insert(tk.END, key)

    def load_buggy_fields(self, event=None):
        if not self.buggy_listbox.curselection():
            return
        index = self.buggy_listbox.curselection()[0]
        key = list(self.buggies.keys())[index]
        self.current_buggy_key = key
        data = self.buggies[key]

        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, data.get("name", ""))

        for section, fields in self.section_vars.items():
            section_data = data.get(section, {})
            for field, widget in fields.items():
                if field == "sensor_coordinates":
                    widget.delete("1.0", tk.END)
                    coords = section_data.get("sensor_coordinates", [])
                    for x, y in coords:
                        widget.insert(tk.END, f"{x},{y}\n")
                else:
                    value = section_data.get(field, "")
                    widget.delete(0, tk.END)
                    widget.insert(0, str(value))

    def save_buggy(self):
        key = self.current_buggy_key or f"buggy_{len(self.buggies)+1}"
        name = self.name_entry.get()

        new_data = {"name": name}
        for section, fields in self.section_vars.items():
            section_data = {}
            for field, widget in fields.items():
                if field == "sensor_coordinates":
                    text = widget.get("1.0", tk.END).strip()
                    coords = []
                    for line in text.splitlines():
                        try:
                            x, y = map(float, line.split(","))
                            coords.append([x, y])
                        except:
                            pass
                    section_data["sensor_coordinates"] = coords
                else:
                    try:
                        section_data[field] = float(widget.get())
                    except ValueError:
                        section_data[field] = widget.get()
            new_data[section] = section_data

        self.buggies[key] = new_data
        save_buggies(self.buggies)
        self.refresh_buggy_list()
        messagebox.showinfo("Saved", f"Buggy '{key}' saved.")

    def delete_buggy(self):
        if self.current_buggy_key and self.current_buggy_key in self.buggies:
            if messagebox.askyesno("Confirm Delete", f"Delete {self.current_buggy_key}?"):
                del self.buggies[self.current_buggy_key]
                save_buggies(self.buggies)
                self.refresh_buggy_list()
                self.current_buggy_key = None
                self.clear_form()

    def clear_form(self):
        self.name_entry.delete(0, tk.END)
        for section in self.section_vars.values():
            for field, widget in section.items():
                if field == "sensor_coordinates":
                    widget.delete("1.0", tk.END)
                else:
                    widget.delete(0, tk.END)

    def new_buggy(self):
        self.clear_form()
        self.current_buggy_key = None

# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = BuggyEditor(root)
    root.mainloop()
