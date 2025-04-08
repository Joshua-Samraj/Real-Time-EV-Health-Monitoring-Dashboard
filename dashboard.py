import pymongo
import customtkinter as ctk
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta
from PIL import Image, ImageTk
import cv2

# Set Dark Mode for the Dashboard
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

def exit_app():
    root.quit()
    root.destroy()

def update_time_filter(choice):
    time_var.set(int(choice))
    refresh_charts()

def fetch_data():
    try:
        client = pymongo.MongoClient("your_mongodb_url", serverSelectionTimeoutMS=5000)
        
        db = client["your_database_name"]
        collection = db["your_collection_name"]

        current_time = datetime.utcnow()
        time_threshold = current_time - timedelta(minutes=time_var.get())
        data = collection.find({"timestamp": {"$gte": time_threshold}})

        timestamps = []
        values = {key: [] for key in [
            "temperature_motor", "current_motor", "voltage_motor",
            "pressure_tyre", "temperature_tyre",
            "temperature_engine", "current_engine", "battery_voltage"
        ]}

        for item in data:
            try:
                timestamp = item.get("timestamp")
                if isinstance(timestamp, str):
                    timestamp = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
                timestamps.append(timestamp)

                for key in values.keys():
                    values[key].append(item.get(key, 0))
            except Exception as e:
                print("Skipping invalid data:", e)

        client.close()
        return timestamps, values
    except Exception as e:
        print("Error fetching data:", str(e))
        return [], {}

def update_plot(ax, timestamps, values, title, ylabel):
    ax.clear()
    if not timestamps or not values:
        return
    
    ax.fill_between(timestamps, values, color="#c44e52", alpha=0.5)
    ax.plot(timestamps, values, marker='o', linestyle='-', color="white", label=title)
    
    # Display live value on the chart
    if timestamps and values:
        ax.text(timestamps[-1], values[-1], f"{values[-1]:.2f}", color='white', fontsize=10, ha='left', va='bottom', bbox=dict(facecolor='black', alpha=0.5))
    
    ax.set_title(title, color="white")
    ax.set_xlabel("Time", color="white")
    ax.set_ylabel(ylabel, color="white")
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    ax.figure.autofmt_xdate()
    ax.grid(True, linestyle="--", alpha=0.5)

    ax.set_facecolor("#2b2b2b")
    ax.figure.set_facecolor("#2b2b2b")
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')

    ax.figure.canvas.draw()

def refresh_charts():
    timestamps, values = fetch_data()
    if timestamps:
        update_plot(ax_motor_temp, timestamps, values["temperature_motor"], "Motor Temperature", "°C")
        update_plot(ax_motor_current, timestamps, values["current_motor"], "Motor Current", "A")
        update_plot(ax_motor_voltage, timestamps, values["voltage_motor"], "Motor Voltage", "V")
        update_plot(ax_tyre_pressure, timestamps, values["pressure_tyre"], "Tyre Pressure", "bar")
        update_plot(ax_tyre_temp, timestamps, values["temperature_tyre"], "Tyre Temperature", "°C")
        update_plot(ax_engine_temp, timestamps, values["temperature_engine"], "Battery Temperature", "°C")
        update_plot(ax_engine_current, timestamps, values["current_engine"], "Battery Current", "A")
        update_plot(ax_battery_voltage, timestamps, values["battery_voltage"], "Battery Voltage", "V")
    
    # Schedule the next refresh after 5000ms (5 seconds)
    # root.after(5000, refresh_charts)

def main():
    global root
    global ax_motor_temp, ax_motor_current, ax_motor_voltage
    global ax_tyre_pressure, ax_tyre_temp
    global ax_engine_temp, ax_engine_current, ax_battery_voltage
    global time_var

    root = ctk.CTk()
    root.title("EV Health Monitoring Dashboard")
    root.geometry("1100x700")

    sidebar = ctk.CTkFrame(root, width=200)
    sidebar.pack(side="left", fill="y", padx=10, pady=10)

    chat_label = ctk.CTkLabel(sidebar, text="Sections", font=("Arial", 16, "bold"))
    chat_label.pack(pady=10)

    exit_button = ctk.CTkButton(sidebar, text="Exit", command=exit_app, fg_color="red")
    exit_button.pack(pady=20)
    refresh_charts_button = ctk.CTkButton(sidebar, text="Refresh", command=refresh_charts, fg_color="green")
    refresh_charts_button.pack(pady=20)

    content_frame = ctk.CTkFrame(root)
    content_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

    tabview = ctk.CTkTabview(content_frame)
    tabview.pack(fill="both", expand=True)

    tab_motor = tabview.add("Motor")
    tab_tyre = tabview.add("Tyre")
    tab_engine = tabview.add("BATTERY")

    fig_motor, (ax_motor_temp, ax_motor_current, ax_motor_voltage) = plt.subplots(3, 1, figsize=(6, 6))
    canvas_motor = FigureCanvasTkAgg(fig_motor, master=tab_motor)
    canvas_motor.get_tk_widget().pack(fill="both", expand=True)

    fig_tyre, (ax_tyre_pressure, ax_tyre_temp) = plt.subplots(2, 1, figsize=(6, 4))
    canvas_tyre = FigureCanvasTkAgg(fig_tyre, master=tab_tyre)
    canvas_tyre.get_tk_widget().pack(fill="both", expand=True)

    fig_engine, (ax_engine_temp, ax_engine_current, ax_battery_voltage) = plt.subplots(3, 1, figsize=(6, 6))
    canvas_engine = FigureCanvasTkAgg(fig_engine, master=tab_engine)
    canvas_engine.get_tk_widget().pack(fill="both", expand=True)

    time_label = ctk.CTkLabel(root, text="Time Filter (mins):")
    time_label.pack(pady=5)

    time_var = ctk.IntVar(value=5)
    time_dropdown = ctk.CTkComboBox(root, values=["1", "5","15","30","60"], variable=time_var, command=update_time_filter)
    time_dropdown.pack(pady=5)

    # Start the auto-refresh cycle
    refresh_charts()
    root.mainloop()

if __name__ == "__main__":
    main()
