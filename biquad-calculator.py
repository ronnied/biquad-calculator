import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class BiquadCalculator(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Biquad Filter Calculator")
        self.geometry("1000x800")

        # Configure style for macOS native look
        style = ttk.Style()
        style.theme_use('default')

        # Create main container
        main_frame = ttk.Frame(self, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Input fields frame
        input_frame = ttk.LabelFrame(main_frame, text="Filter Parameters", padding="10")
        input_frame.grid(row=0, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))

        # Create and place input fields
        self.filter_type_var = tk.StringVar(value="parametric")
        self.freq_var = tk.StringVar(value="1000")
        self.gain_var = tk.StringVar(value="6")
        self.q_var = tk.StringVar(value="0.707")
        self.gainLinear_var = tk.StringVar(value="0")

        # Filter type selector
        ttk.Label(input_frame, text="Filter Type:").grid(row=0, column=0, padx=5, pady=2)
        filter_types = ['parametric', 'low_shelf', 'high_shelf']
        filter_combo = ttk.Combobox(input_frame, textvariable=self.filter_type_var, values=filter_types,
                                    state='readonly')
        filter_combo.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(input_frame, text="Frequency (Hz):").grid(row=1, column=0, padx=5, pady=2)
        ttk.Entry(input_frame, textvariable=self.freq_var).grid(row=1, column=1, padx=5, pady=2)

        ttk.Label(input_frame, text="Boost/Cut (dB):").grid(row=2, column=0, padx=5, pady=2)
        ttk.Entry(input_frame, textvariable=self.gain_var).grid(row=2, column=1, padx=5, pady=2)

        ttk.Label(input_frame, text="Q Factor:").grid(row=3, column=0, padx=5, pady=2)
        ttk.Entry(input_frame, textvariable=self.q_var).grid(row=3, column=1, padx=5, pady=2)

        ttk.Label(input_frame, text="GainLinear (dB):").grid(row=4, column=0, padx=5, pady=2)
        ttk.Entry(input_frame, textvariable=self.gainLinear_var).grid(row=4, column=1, padx=5, pady=2)

        calculate_button = ttk.Button(input_frame, text="Calculate", command=self.calculate)
        calculate_button.grid(row=5, column=0, columnspan=2, pady=10)

        # Bind Return/Enter key to calculate
        self.bind('<Return>', lambda event: self.calculate())

        # Create matplotlib figure
        self.fig = Figure(figsize=(10, 4))
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=main_frame)
        self.canvas.get_tk_widget().grid(row=1, column=0, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Coefficients display
        self.coeff_frame = ttk.LabelFrame(main_frame, text="Filter Coefficients", padding="10")
        self.coeff_frame.grid(row=2, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))

        self.coeff_labels = {}
        coeff_names = ['b0', 'b1', 'b2', 'a1', 'a2']
        for i, name in enumerate(coeff_names):
            ttk.Label(self.coeff_frame, text=f"{name}:").grid(row=i, column=0, padx=5, pady=2)
            self.coeff_labels[name] = ttk.Label(self.coeff_frame, text="0.000000")
            self.coeff_labels[name].grid(row=i, column=1, padx=5, pady=2)

        # Calculate initial response
        self.calculate()

    def calculate_parametric_coefficients(self, w0, dbBoost, Q, gainLinear):
        A = np.power(10, dbBoost / 40)
        alpha = np.sin(w0) / (2 * Q)

        a0 = 1 + alpha / A
        a1 = -2 * np.cos(w0)
        a2 = 1 - alpha / A

        b0 = (1 + alpha * A) * gainLinear
        b1 = (-2 * np.cos(w0)) * gainLinear
        b2 = (1 - alpha * A) * gainLinear

        return b0, b1, b2, a0, a1, a2

    def calculate_shelf_coefficients(self, w0, dbBoost, Q, gainLinear, shelf_type='low'):
        A = np.power(10, dbBoost / 40)
        alpha = np.sin(w0) / 2 * np.sqrt((A + 1 / A) * (1 / Q - 1) + 2)

        if shelf_type == 'low':
            a0 = (A + 1) + (A - 1) * np.cos(w0) + 2 * np.sqrt(A) * alpha
            a1 = -2 * ((A - 1) + (A + 1) * np.cos(w0))
            a2 = (A + 1) + (A - 1) * np.cos(w0) - 2 * np.sqrt(A) * alpha

            b0 = A * ((A + 1) - (A - 1) * np.cos(w0) + 2 * np.sqrt(A) * alpha) * gainLinear
            b1 = 2 * A * ((A - 1) - (A + 1) * np.cos(w0)) * gainLinear
            b2 = A * ((A + 1) - (A - 1) * np.cos(w0) - 2 * np.sqrt(A) * alpha) * gainLinear
        else:  # high shelf
            a0 = (A + 1) + (A - 1) * np.cos(w0) + 2 * np.sqrt(A) * alpha
            a1 = 2 * ((A - 1) - (A + 1) * np.cos(w0))
            a2 = (A + 1) + (A - 1) * np.cos(w0) - 2 * np.sqrt(A) * alpha

            b0 = A * ((A + 1) + (A - 1) * np.cos(w0) + 2 * np.sqrt(A) * alpha) * gainLinear
            b1 = -2 * A * ((A - 1) + (A + 1) * np.cos(w0)) * gainLinear
            b2 = A * ((A + 1) + (A - 1) * np.cos(w0) - 2 * np.sqrt(A) * alpha) * gainLinear

        return b0, b1, b2, a0, a1, a2

    def calculate_coefficients(self):
        try:
            freq = float(self.freq_var.get())
            dbBoost = float(self.gain_var.get())
            Q = float(self.q_var.get())
            gainLinear_db = float(self.gainLinear_var.get())
            filter_type = self.filter_type_var.get()
            fs = 48000

            w0 = 2 * np.pi * (freq / fs)
            gainLinear = 1.0 if gainLinear_db == 0 else np.power(10, gainLinear_db / 20)

            if filter_type == 'parametric':
                b0, b1, b2, a0, a1, a2 = self.calculate_parametric_coefficients(w0, dbBoost, Q, gainLinear)
            elif filter_type == 'low_shelf':
                b0, b1, b2, a0, a1, a2 = self.calculate_shelf_coefficients(w0, dbBoost, Q, gainLinear, 'low')
            else:  # high_shelf
                b0, b1, b2, a0, a1, a2 = self.calculate_shelf_coefficients(w0, dbBoost, Q, gainLinear, 'high')

            # Normalize coefficients
            b0 /= a0
            b1 /= a0
            b2 /= a0
            a1 /= a0
            a2 /= a0

            return b0, b1, b2, a1, a2
        except ValueError:
            return None

    def calculate_frequency_response(self, b0, b1, b2, a1, a2):
        fs = 48000
        freqs = np.logspace(np.log10(20), np.log10(fs / 2), 1000)
        w = 2 * np.pi * freqs / fs
        z = np.exp(1j * w)

        H = (b0 + b1 * np.power(z, -1) + b2 * np.power(z, -2)) / \
            (1 + a1 * np.power(z, -1) + a2 * np.power(z, -2))
        return freqs, 20 * np.log10(np.abs(H))

    def calculate(self, event=None):
        try:
            coeffs = self.calculate_coefficients()
            if coeffs is None:
                return

            # Force update the GUI
            self.update_idletasks()

            b0, b1, b2, a1, a2 = coeffs

            # Update coefficient labels
            self.coeff_labels['b0'].config(text=f"{b0:.6f}")
            self.coeff_labels['b1'].config(text=f"{b1:.6f}")
            self.coeff_labels['b2'].config(text=f"{b2:.6f}")
            self.coeff_labels['a1'].config(text=f"{a1:.6f}")
            self.coeff_labels['a2'].config(text=f"{a2:.6f}")

            # Calculate and plot frequency response
            freqs, mag = self.calculate_frequency_response(b0, b1, b2, a1, a2)

            self.ax.clear()
            self.ax.semilogx(freqs, mag)
            self.ax.grid(True)
            self.ax.set_xlabel('Frequency [Hz]')
            self.ax.set_ylabel('Magnitude [dB]')
            filter_type = self.filter_type_var.get().replace('_', ' ').title()
            self.ax.set_title(f'Biquad Filter Frequency Response - {filter_type}')
            self.ax.set_ylim([-40, 40])
            self.fig.tight_layout()
            self.canvas.draw()

        except Exception as e:
            print(f"Error in calculate: {e}")


if __name__ == "__main__":
    app = BiquadCalculator()
    app.mainloop()