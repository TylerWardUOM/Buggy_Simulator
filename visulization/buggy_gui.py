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
        self.buggy_keys = []

        self.buggy_listbox = tk.Listbox(root, width=30)
        self.buggy_listbox.pack(side=tk.LEFT, fill=tk.Y)
        self.buggy_listbox.bind("<<ListboxSelect>>", self.load_buggy_fields)

        form_container = tk.Frame(root)
        form_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.form_canvas = tk.Canvas(form_container, highlightthickness=0)
        form_scrollbar = tk.Scrollbar(
            form_container,
            orient=tk.VERTICAL,
            command=self.form_canvas.yview,
        )
        self.form_canvas.configure(yscrollcommand=form_scrollbar.set)
        form_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.form_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.form_frame = tk.Frame(self.form_canvas)
        form_window = self.form_canvas.create_window(
            (0, 0),
            window=self.form_frame,
            anchor="nw",
        )
        self.form_frame.bind(
            "<Configure>",
            lambda event: self.form_canvas.configure(
                scrollregion=self.form_canvas.bbox("all")
            ),
        )
        self.form_canvas.bind(
            "<Configure>",
            lambda event: self.form_canvas.itemconfigure(
                form_window,
                width=event.width,
            ),
        )

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
            "gearbox", "wheel", "buggy", "battery", "sensor_array"
        ]
        self.name_entry = self.create_labeled_entry(self.form_frame, "Name")

        self.section_vars = {}
        self.motor_sections = {}
        self.motor_section_frames = {}
        motor_label = tk.Label(
            self.form_frame,
            text="MOTOR CONFIGURATION",
            font=("Arial", 10, "bold"),
        )
        motor_label.pack(pady=5)
        self.motor_mode = tk.StringVar(value="shared")
        motor_modes = [
            ("Shared motor (both wheels)", "shared"),
            ("Left motor only (copied to right)", "left_only"),
            ("Right motor only (copied to left)", "right_only"),
            ("Independent left and right motors", "independent"),
        ]
        for label, value in motor_modes:
            tk.Radiobutton(
                self.form_frame,
                text=label,
                variable=self.motor_mode,
                value=value,
                command=self.update_motor_field_visibility,
            ).pack(anchor="w", padx=5)
        for section, title in (
            ("motor", "Shared motor"),
            ("left_motor", "Left motor"),
            ("right_motor", "Right motor"),
        ):
            section_frame = tk.Frame(self.form_frame)
            section_frame.pack(fill=tk.X)
            tk.Label(section_frame, text=title).pack(anchor="w", pady=(5, 0))
            self.motor_section_frames[section] = section_frame
            self.motor_sections[section] = self.create_motor_fields(section_frame)

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
        self.update_motor_field_visibility()

    def create_motor_fields(self, parent):
        fields = {}
        for field in [
            "armature_resistance",
            "brush_voltage",
            "torque_constant",
            "emf_constant",
            "motor_max_current",
            "motor_inertia",
        ]:
            fields[field] = self.create_labeled_entry(
                parent,
                f"{field}",
            )
        return fields

    def update_motor_field_visibility(self):
        mode = self.motor_mode.get()
        visible_sections = {
            "shared": {"motor"},
            "left_only": {"left_motor"},
            "right_only": {"right_motor"},
            "independent": {"left_motor", "right_motor"},
        }[mode]
        for section, frame in self.motor_section_frames.items():
            frame.pack_forget()
            if section in visible_sections:
                frame.pack(fill=tk.X)

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
        self.buggy_keys = list(self.buggies.keys())
        for key in self.buggy_keys:
            display_name = self.buggies[key].get("name", "").strip() or key
            self.buggy_listbox.insert(tk.END, display_name)

    def load_buggy_fields(self, event=None):
        if not self.buggy_listbox.curselection():
            return
        index = self.buggy_listbox.curselection()[0]
        key = self.buggy_keys[index]
        self.current_buggy_key = key
        data = self.buggies[key]

        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, data.get("name", ""))

        if "left_motor" in data and "right_motor" in data:
            motor_mode = "independent"
        elif "left_motor" in data:
            motor_mode = "left_only"
        elif "right_motor" in data:
            motor_mode = "right_only"
        else:
            motor_mode = "shared"
        self.motor_mode.set(motor_mode)
        for section, fields in self.motor_sections.items():
            section_data = data.get(section, {})
            for field, widget in fields.items():
                widget.delete(0, tk.END)
                widget.insert(0, str(section_data.get(field, "")))
        self.update_motor_field_visibility()

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
        motor_mode = self.motor_mode.get()
        motor_sections = {
            "shared": ("motor",),
            "left_only": ("left_motor",),
            "right_only": ("right_motor",),
            "independent": ("left_motor", "right_motor"),
        }[motor_mode]
        for section in motor_sections:
            section_data = {}
            for field, widget in self.motor_sections[section].items():
                try:
                    section_data[field] = float(widget.get())
                except ValueError:
                    section_data[field] = widget.get()
            new_data[section] = section_data

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
        self.motor_mode.set("shared")
        for section in self.motor_sections.values():
            for widget in section.values():
                widget.delete(0, tk.END)
        self.update_motor_field_visibility()
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
