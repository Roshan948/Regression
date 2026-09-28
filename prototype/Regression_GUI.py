"""
Regression_GUI.py — Tkinter form for the bike demand predictor, matching the
reference project's own GUI toolkit (plain Tkinter/ttk), with two fixes:

1. No "minute" field — the underlying model was trained without it, since
   every timestamp in the dataset is on the hour (see the notebook's EDA).
2. holiday/workingday are sent as single 0/1 flags, not one-hot pairs — the
   model was trained on single binary columns for these (see Fix #3 in the
   notebook), so the GUI's output dict matches that exactly.
"""
from predict import predict
import tkinter as tk
from tkinter import ttk, messagebox

root = tk.Tk()
root.title("Bike Rental Prediction Model")
root.geometry("370x480")

temp_var = tk.StringVar()
humidity_var = tk.StringVar()
windspeed_var = tk.StringVar()

weather_var = tk.StringVar(value="clear")
season_var = tk.StringVar(value="spring")

holiday_var = tk.BooleanVar(value=False)
workday_var = tk.BooleanVar(value=False)

year_var = tk.StringVar(value="2011")
month_var = tk.StringVar(value="1")
day_var = tk.StringVar(value="1")
hour_var = tk.StringVar(value="0")


def validate_float(value):
    if value == "":
        return True
    try:
        return float(value) >= 0
    except ValueError:
        return False


validate_command = (root.register(validate_float), "%P")

float_fields = [
    ("Temperature", temp_var),
    ("Humidity Percentage", humidity_var),
    ("Wind Speed", windspeed_var),
]

for row, (label, variable) in enumerate(float_fields):
    ttk.Label(root, text=label).grid(row=row, column=0, padx=10, pady=8, sticky="w")
    ttk.Entry(
        root, textvariable=variable, width=20,
        validate="key", validatecommand=validate_command,
    ).grid(row=row, column=1, padx=10, pady=8, sticky="w")

ttk.Label(root, text="Weather").grid(row=3, column=0, padx=10, pady=8, sticky="w")
ttk.Combobox(
    root, textvariable=weather_var,
    values=["clear", "cloudy", "light", "heavy"], state="readonly", width=17,
).grid(row=3, column=1, padx=10, pady=8, sticky="w")

ttk.Label(root, text="Season").grid(row=4, column=0, padx=10, pady=8, sticky="w")
ttk.Combobox(
    root, textvariable=season_var,
    values=["spring", "summer", "fall", "winter"], state="readonly", width=17,
).grid(row=4, column=1, padx=10, pady=8, sticky="w")

ttk.Checkbutton(root, text="Holiday", variable=holiday_var).grid(row=5, column=0, padx=10, pady=8, sticky="w")
ttk.Checkbutton(root, text="Workday", variable=workday_var).grid(row=5, column=1, padx=10, pady=8, sticky="w")

ttk.Label(root, text="Year").grid(row=6, column=0, padx=10, pady=8, sticky="w")
ttk.Combobox(
    root, textvariable=year_var, values=["2011", "2012"], state="readonly", width=17,
).grid(row=6, column=1, padx=10, pady=8, sticky="w")

ttk.Label(root, text="Month").grid(row=7, column=0, padx=10, pady=8, sticky="w")
ttk.Combobox(
    root, textvariable=month_var, values=[str(i) for i in range(1, 13)], state="readonly", width=17,
).grid(row=7, column=1, padx=10, pady=8, sticky="w")

ttk.Label(root, text="Day").grid(row=8, column=0, padx=10, pady=8, sticky="w")
ttk.Combobox(
    root, textvariable=day_var, values=[str(i) for i in range(1, 32)], state="readonly", width=17,
).grid(row=8, column=1, padx=10, pady=8, sticky="w")

ttk.Label(root, text="Hour").grid(row=9, column=0, padx=10, pady=8, sticky="w")
tk.Spinbox(
    root, from_=0, to=23, textvariable=hour_var, width=17, wrap=True,
).grid(row=9, column=1, padx=10, pady=8, sticky="w")


def submit():
    if not all([temp_var.get(), humidity_var.get(), windspeed_var.get()]):
        messagebox.showerror("Invalid Input", "Please fill in all three weather measurements.")
        return

    temp = float(temp_var.get())
    humidity = float(humidity_var.get())
    windspeed = float(windspeed_var.get())

    if any(v < 0 for v in [temp, humidity, windspeed]):
        messagebox.showerror("Invalid Input", "Measurements cannot be negative.")
        return

    weather = weather_var.get()
    weather_map = {"clear": 1, "cloudy": 2, "light": 3, "heavy": 4}
    weather_num = weather_map[weather]

    season = season_var.get()
    season_map = {"spring": 1, "summer": 2, "fall": 3, "winter": 4}
    season_num = season_map[season]

    data = {
        "temp": temp,
        "humidity": humidity,
        "windspeed": windspeed,
        "holiday": int(holiday_var.get()),
        "workingday": int(workday_var.get()),
        "year": int(year_var.get()),
        "month": int(month_var.get()),
        "day": int(day_var.get()),
        "hour": int(hour_var.get()),
    }
    for w in (1, 2, 3, 4):
        data[f"weather_{w}"] = (weather_num == w)
    for s in (1, 2, 3, 4):
        data[f"season_{s}"] = (season_num == s)

    result = predict(data)

    messagebox.showinfo("Prediction", f"Prediction: {result} bikes rented")


ttk.Button(root, text="Submit", command=submit).grid(row=10, column=0, columnspan=2, pady=20)

if __name__ == "__main__":
    root.mainloop()
