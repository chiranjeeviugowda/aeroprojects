import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from aero_calculations import calculate_downforce, calculate_drag, aoa_to_coefficients
import numpy as np
from mpl_toolkits.mplot3d import Axes3D

car_profiles = {
    "Custom": {},
    "Formula Student": {"area": 1.0, "aoa": 35, "velocity": 25},  
    "GT Car": {"area": 1.8, "aoa": 20, "velocity": 50},          
    "F1 Car": {"area": 1.5, "aoa": 12, "velocity": 80}          
}

def apply_profile(*args):
    selected = profile_var.get()
    profile = car_profiles.get(selected, {})
    
    if "area" in profile:
        entry_area.delete(0, tk.END)
        entry_area.insert(0, profile["area"])
    
    if "aoa" in profile:
        aoa_var.set(profile["aoa"])  
    
    if "velocity" in profile:
        speed_var.set(profile["velocity"])  
    
    update_slider_result()  

def plot_aoa_vs_coeffs():
    try:
        aoa_range = list(range(-5, 21))  
        cl_vals = []
        cd_vals = []

        for aoa in aoa_range:
            cl, cd = aoa_to_coefficients(aoa)
            cl_vals.append(cl)
            cd_vals.append(cd)

        fig.clear()
        ax = fig.add_subplot(111)
        ax.plot(aoa_range, cl_vals, label='CL (Lift Coefficient)')
        ax.plot(aoa_range, cd_vals, label='CD (Drag Coefficient)')
        ax.set_xlabel('Angle of Attack (°)')
        ax.set_ylabel('Coefficient Value')
        ax.set_title('AoA vs CL/CD')
        ax.legend()
        canvas.draw()

        label_result.config(text="Plotted AoA vs CL/CD.")
    except Exception as e:
        label_result.config(text=f"Error: {str(e)}")

def calculate_and_plot():
    try:
        rho = float(entry_rho.get())
        velocity = speed_var.get()
        area = float(entry_area.get())
        aoa = aoa_var.get()

        cl, cd = aoa_to_coefficients(aoa)
        downforce = calculate_downforce(rho, velocity, area, cl)
        drag = calculate_drag(rho, velocity, area, cd)

        label_result.config(text=f"CL: {cl:.2f}, CD: {cd:.2f}\nDownforce: {downforce:.2f} N\nDrag: {drag:.2f} N")

        #graphs
        speeds = list(range(0, 301, 10)) 
        speeds_mps = [s / 3.6 for s in speeds]
        downforce_vals = [calculate_downforce(rho, v, area, cl) for v in speeds_mps]
        drag_vals = [calculate_drag(rho, v, area, cd) for v in speeds_mps]

        fig.clear()
        ax = fig.add_subplot(111)
        ax.plot(speeds, downforce_vals, label='Downforce (N)')
        ax.plot(speeds, drag_vals, label='Drag (N)')
        ax.set_xlabel('Speed (km/h)')
        ax.set_ylabel('Force (N)')
        ax.set_title('Aero Forces vs Speed')
        ax.legend()
        canvas.draw()
    except ValueError:
        label_result.config(text="Invalid input. Please enter numeric values.")
def update_slider_result():
    speed_label.config(text=f"{speed_var.get():.1f} m/s")
    aoa_label.config(text=f"{aoa_var.get():.1f}°")
    calculate_and_plot()

def plot_efficiency_heatmap():
    aoa_range = np.linspace(-10, 45, 100)
    speed_range = np.linspace(1, 100, 100)  

    AOA, SPEED = np.meshgrid(aoa_range, speed_range)
    EFFICIENCY = np.zeros_like(AOA)

    for i in range(AOA.shape[0]):
        for j in range(AOA.shape[1]):
            cl, cd = aoa_to_coefficients(AOA[i, j])
            if cd != 0:
                EFFICIENCY[i, j] = cl / cd
            else:
                EFFICIENCY[i, j] = 0

    fig = plt.figure(figsize=(10, 6))
    ax = fig.add_subplot(111, projection='3d')
    ax.plot_surface(AOA, SPEED, EFFICIENCY, cmap='plasma')

    ax.set_title("Aero Efficiency (Cl/Cd) vs AoA and Speed")
    ax.set_xlabel("Angle of Attack (°)")
    ax.set_ylabel("Speed (m/s)")
    ax.set_zlabel("Cl / Cd")

    plt.tight_layout()
    plt.show()
#GUI Setup
root = tk.Tk()
root.title("Motorsport AeroSim")

frame = ttk.Frame(root, padding=20)
frame.grid(row=0, column=0)

#Inputs
ttk.Label(frame, text="Air Density (kg/m³):").grid(row=0, column=0, sticky="e")
entry_rho = ttk.Entry(frame)
entry_rho.insert(0, "1.225")
entry_rho.grid(row=0, column=1)

#Speed Slider
ttk.Label(frame, text="Speed (m/s):").grid(row=1, column=0, sticky="e")
speed_var = tk.DoubleVar(value=60)
speed_slider = ttk.Scale(frame, from_=0, to=100, variable=speed_var, orient="horizontal", command=lambda e: update_slider_result())
speed_slider.grid(row=1, column=1)
speed_label = ttk.Label(frame, text=f"{speed_var.get():.1f} m/s")
speed_label.grid(row=1, column=2)

#AoA Slider
ttk.Label(frame, text="Angle of Attack (°):").grid(row=3, column=0, sticky="e")
aoa_var = tk.DoubleVar(value=10)
aoa_slider = ttk.Scale(frame, from_=-10, to=45, variable=aoa_var, orient="horizontal", command=lambda e: update_slider_result())
aoa_slider.grid(row=3, column=1)
aoa_label = ttk.Label(frame, text=f"{aoa_var.get():.1f}°")
aoa_label.grid(row=3, column=2)



ttk.Label(frame, text="Wing Area (m²):").grid(row=2, column=0, sticky="e")
entry_area = ttk.Entry(frame)
entry_area.insert(0, "1.2")
entry_area.grid(row=2, column=1)
#Dropdown for Car Profile
ttk.Label(frame, text="Select Car Profile:").grid(row=4, column=0, sticky="e")
profile_var = tk.StringVar()
profile_combo = ttk.Combobox(frame, textvariable=profile_var, state="readonly")
profile_combo['values'] = list(car_profiles.keys())
profile_combo.current(0)
profile_combo.grid(row=4, column=1)

#Update inputs when profile is changed
def apply_profile(*args):
    selected = profile_var.get()
    profile = car_profiles.get(selected, {})

    if "area" in profile:
        area_var.set(profile["area"])

    if "aoa" in profile:
        aoa_var.set(profile["aoa"])

    if "velocity" in profile:
        speed_var.set(profile["velocity"])

    update_slider_result()


#Button & Results

ttk.Button(frame, text="Calculate", command=calculate_and_plot).grid(row=5, column=0, columnspan=2, pady=10)
ttk.Button(frame, text="Plot AoA vs CL/CD", command=plot_aoa_vs_coeffs).grid(row=6, column=0, columnspan=2, pady=5,padx=300)
ttk.Button(frame, text="Show Efficiency Heatmap", command=plot_efficiency_heatmap).grid(row=6, column=1, pady=10)

label_result = ttk.Label(frame, text="")
label_result.grid(row=7, column=0, columnspan=2)

#Plot Area
fig = plt.Figure(figsize=(6, 4), dpi=100)
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().grid(row=0, column=1, rowspan=7, padx=20, pady=20)

root.mainloop()
