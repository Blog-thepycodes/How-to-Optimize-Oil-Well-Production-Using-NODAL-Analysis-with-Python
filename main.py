import tkinter as tk
from tkinter import ttk
import numpy as np
import pandas as pd
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg




# Function to calculate Vogel IPR curve
def vogel_ipr(q_max, p_wf, p_res):
   return q_max * (1 - 0.2 * (p_wf / p_res) - 0.8 * (p_wf / p_res) ** 2)




# Function to calculate VLP example curve
def vlp_example(depth, rate, fluid_density=50, gas_fraction=0.1):
   gas_density = 0.0764  # lb/ft³, typical value for natural gas
   liquid_density = fluid_density * (1 - gas_fraction) + gas_density * gas_fraction
   pressure_drop = 0.433 * liquid_density * depth / 1440 * rate / 1000  # Pressure drop in psi
   return pressure_drop




# Function for NODAL analysis to find the operating point
def nodal_analysis(ipr_df, vlp_df):
   vlp_interp = np.interp(ipr_df['q'], vlp_df['rate'], vlp_df['pressure_drop'])
   differences = np.abs(ipr_df['p_wf'] - vlp_interp)
   min_index = differences.idxmin()
   operating_point = (ipr_df.loc[min_index, 'q'], ipr_df.loc[min_index, 'p_wf'])
   return operating_point




# Function to plot IPR and VLP curves and the operating point
def plot_ipr_vlp(ipr_df, vlp_df, operating_point):
   fig = Figure(figsize=(8, 6))
   ax = fig.add_subplot(111)
   ax.plot(ipr_df['p_wf'], ipr_df['q'], label='IPR Curve')
   ax.plot(vlp_df['pressure_drop'], vlp_df['rate'], label='VLP Curve')
   ax.plot(operating_point[1], operating_point[0], 'ro', label='Operating Point')
   ax.set_title('NODAL Analysis')
   ax.set_xlabel('Bottom Hole Pressure (psi)')
   ax.set_ylabel('Production Rate (STB/day)')
   ax.legend()
   return fig




# Function to update the plot based on user inputs
def update_plot():
   q_max = float(q_max_entry.get())
   p_res = float(p_res_entry.get())
   depth = float(depth_entry.get())
   fluid_density = float(fluid_density_entry.get())


   p_wf = np.linspace(0, p_res, 50)
   q = vogel_ipr(q_max, p_wf, p_res)
   ipr_df = pd.DataFrame({'p_wf': p_wf, 'q': q})


   rates = np.linspace(0, q_max, 50)
   pressure_drops = vlp_example(depth, rates, fluid_density)
   vlp_df = pd.DataFrame({'rate': rates, 'pressure_drop': pressure_drops})


   operating_point = nodal_analysis(ipr_df, vlp_df)


   op_label.config(
       text=f"Operating Point: Flow Rate = {operating_point[0]:.2f} STB/day, Bottom Hole Pressure = {operating_point[1]:.2f} psi"
   )


   # Clear the previous plot
   for widget in plot_frame.winfo_children():
       widget.destroy()


   # Create a new plot
   fig = plot_ipr_vlp(ipr_df, vlp_df, operating_point)
   canvas = FigureCanvasTkAgg(fig, master=plot_frame)
   canvas.draw()
   canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)




# Main application
app = tk.Tk()
app.title("NODAL Analysis Optimizer - The Pycodes")
app.geometry("900x700")


input_frame = ttk.LabelFrame(app, text="Input Parameters")
input_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)


# Input fields
ttk.Label(input_frame, text="Maximum Production Rate (STB/day):").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
q_max_entry = ttk.Entry(input_frame)
q_max_entry.grid(row=0, column=1, padx=5, pady=5)
q_max_entry.insert(0, "2000")


ttk.Label(input_frame, text="Reservoir Pressure (psi):").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
p_res_entry = ttk.Entry(input_frame)
p_res_entry.grid(row=1, column=1, padx=5, pady=5)
p_res_entry.insert(0, "3000")


ttk.Label(input_frame, text="Well Depth (feet):").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
depth_entry = ttk.Entry(input_frame)
depth_entry.grid(row=2, column=1, padx=5, pady=5)
depth_entry.insert(0, "10000")


ttk.Label(input_frame, text="Fluid Density (lb/ft³):").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
fluid_density_entry = ttk.Entry(input_frame)
fluid_density_entry.grid(row=3, column=1, padx=5, pady=5)
fluid_density_entry.insert(0, "50")


# Update button
update_button = ttk.Button(input_frame, text="Update Plot", command=update_plot)
update_button.grid(row=4, column=0, columnspan=2, pady=10)


# Operating point label
op_label = ttk.Label(app, text="Operating Point: Flow Rate = N/A, Bottom Hole Pressure = N/A")
op_label.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)


# Plot frame
plot_frame = ttk.Frame(app)
plot_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=1)


# Run the application
app.mainloop()
