import tkinter as tk
from tkinter import ttk, simpledialog, filedialog
import threading
import time
import schedule
from playsound import playsound  # Required library for playing sound
import tkinter.messagebox as messagebox
from datetime import datetime
import json

class SchoolBellRingerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("School Bell Ringer")

        self.schedules = []

        self.create_widgets()
        self.load_schedules()  # Load schedules when the application starts
        self.start_bell_thread()

    def create_widgets(self):
        # Day selector
        self.day_label = ttk.Label(self.root, text="Select Day:")
        self.day_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.day_options = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        self.day_combobox = ttk.Combobox(self.root, values=self.day_options, state="readonly")
        self.day_combobox.grid(row=0, column=1, padx=10, pady=5, sticky="we")
        self.day_combobox.current(0)  # Set default selection

        # Time entry
        self.time_label = ttk.Label(self.root, text="Select Time:")
        self.time_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.time_options = []
        for hour in range(0, 24):
            for minute in range(0, 60, 5):
                self.time_options.append(f"{hour:02d}:{minute:02d}")  # Format as HH:MM
        self.time_combobox = ttk.Combobox(self.root, values=self.time_options, state="readonly")
        self.time_combobox.grid(row=1, column=1, padx=10, pady=5, sticky="we")
        self.time_combobox.current(0)  # Set default selection

        # Sound file selection
        self.sound_button = ttk.Button(self.root, text="Select Sound", command=self.select_sound)
        self.sound_button.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="we")

        # Schedule list
        self.schedule_list = tk.Listbox(self.root, width=60, height=10)
        self.schedule_list.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

        # Save button
        self.save_button = ttk.Button(self.root, text="Save", command=self.add_schedule)
        self.save_button.grid(row=4, column=0, padx=10, pady=5, sticky="we")

        # Delete button
        self.delete_button = ttk.Button(self.root, text="Delete", command=self.delete_schedule)
        self.delete_button.grid(row=4, column=1, padx=10, pady=5, sticky="we")

        # Edit button
        self.edit_button = ttk.Button(self.root, text="Edit", command=self.edit_schedule)
        self.edit_button.grid(row=5, column=0, columnspan=2, padx=10, pady=5, sticky="we")

    def load_schedules(self):
        try:
            with open("schedules.json", "r") as file:
                data = file.read()
                if data:
                    self.schedules = json.loads(data)
                else:
                    self.schedules = []  # Initialize as an empty list if file is empty
            self.update_schedule_list()
        except FileNotFoundError:
            self.schedules = []  # Initialize as an empty list if file does not exist

    def save_schedules(self):
        with open("schedules.json", "w") as file:
            json.dump(self.schedules, file, indent=4)

    def add_schedule(self):
        day = self.day_combobox.get()
        time_entry = self.time_combobox.get()
        sound_file = getattr(self, "selected_sound", None)
        if day and time_entry and sound_file:
            current_date = datetime.now().date()  # Get current date
            schedule_time = datetime.strptime(time_entry, "%H:%M").time()  # Convert schedule time to time object
            schedule_datetime = datetime.combine(current_date, schedule_time)  # Combine with current date
            if day == current_date.strftime("%A") and schedule_datetime < datetime.now():
                messagebox.showerror("Error", "Cannot enter past time for the current day.")
            else:
                self.schedules.append({"day": day, "time": time_entry, "sound": sound_file})
                self.update_schedule_list()
                self.setup_schedule_event(day, time_entry, sound_file)
                self.save_schedules()  # Save schedules after adding a new one
                messagebox.showinfo("Schedule Saved", "The schedule has been saved successfully.")

    def select_sound(self):
        sound_file = filedialog.askopenfilename(title="Select Sound File", filetypes=[("Sound files", "*.mp3;*.wav")])
        if sound_file:
            self.selected_sound = sound_file

    def update_schedule_list(self):
        self.schedule_list.delete(0, tk.END)
        for index, schedule_item in enumerate(self.schedules):
            self.schedule_list.insert(tk.END, f"{index + 1}. {schedule_item['day']} - {schedule_item['time']} ({schedule_item['sound']})")

    def setup_schedule_event(self, day, time_entry, sound_file):
        schedule.every().day.at(time_entry).do(self.trigger_bell, sound_file)

    def trigger_bell(self, sound_file):
        # Function to show the message box
        def show_message_box():
            messagebox.showinfo("Bell Ringing", f"The bell is ringing! Sound File: {sound_file}")

        # Start a timer to show the message box after 5 seconds
        timer = threading.Timer(5, show_message_box)
        timer.start()

        print(f"Bell rings! Sound File: {sound_file}")
        # Play the selected sound
        playsound(sound_file)

    def start_bell_thread(self):
        bell_thread = threading.Thread(target=self.bell_scheduler)
        bell_thread.daemon = True
        bell_thread.start()

    def bell_scheduler(self):
        while True:
            schedule.run_pending()
            time.sleep(1)

    def delete_schedule(self):
        selected_index = self.schedule_list.curselection()
        if selected_index:
            selected_index = int(selected_index[0])
            del self.schedules[selected_index]
            self.update_schedule_list()
            self.save_schedules()  # Save schedules after deleting

    def edit_schedule(self):
        selected_index = self.schedule_list.curselection()
        if selected_index:
            selected_index = int(selected_index[0])
            selected_schedule = self.schedules[selected_index]
            # Display a dialog to edit the selected schedule
            day = simpledialog.askstring("Edit Schedule", "Enter new day:", initialvalue=selected_schedule["day"])
            time_entry = simpledialog.askstring("Edit Schedule", "Enter new time (HH:MM):",
                                                initialvalue=selected_schedule["time"])
            sound_file = filedialog.askopenfilename(title="Select Sound File",
                                                    filetypes=[("Sound files", "*.mp3;*.wav")])
            if day and time_entry and sound_file:
                self.schedules[selected_index] = {"day": day, "time": time_entry, "sound": sound_file}
                self.update_schedule_list()
                schedule.clear()
                for schedule_item in self.schedules:
                    self.setup_schedule_event(schedule_item["day"], schedule_item["time"], schedule_item["sound"])
                self.save_schedules()  # Save schedules after editing
                messagebox.showinfo("Schedule Updated", "The schedule has been updated successfully.")


if __name__ == "__main__":
    root = tk.Tk()
    app = SchoolBellRingerApp(root)
    root.mainloop()
