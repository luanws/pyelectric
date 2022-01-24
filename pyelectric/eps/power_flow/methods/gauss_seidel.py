import math
from typing import List

import numpy as np
import sympy as sp
from pyelectric.eps.power_flow.bar import Bar
from pyelectric.eps.power_flow.bar.load_bar import LoadBar
from pyelectric.eps.power_flow.bar.regulator_bar import RegulatorBar
from pyelectric.eps.power_flow.bar.slack_bar import SlackBar
from pyelectric.eps.power_flow.circuit import Circuit
from pyelectric.eps.power_flow.step import Step


class GaussSeidel:
    circuit: Circuit
    __y_bus_array: np.ndarray
    __voltage_array: np.ndarray
    __power_esp_array: np.ndarray
    __steps: List[Step] = []
    k: int = 0

    def __init__(self, circuit: Circuit):
        self.circuit = circuit

    def __str__(self) -> str:
        return str(self.circuit)

    @property
    def steps(self):
        return self.__steps

    def add_step(self, *args, **kwargs):
        self.__steps.append(Step(*args, **kwargs))

    def get_y_bus_array(self) -> np.ndarray:
        y_bus = np.zeros((len(self.circuit.bars), len(
            self.circuit.bars)), dtype=complex)
        for line in self.circuit.lines:
            bar1_index = self.circuit.get_bar_index(line.bar1)
            bar2_index = self.circuit.get_bar_index(line.bar2)
            y_bus[bar1_index, bar2_index] = -line.admittance
            y_bus[bar2_index, bar1_index] = -line.admittance

            y_bus[bar1_index, bar1_index] = sum(
                [l.admittance for l in self.circuit.lines if l.bar1 == line.bar1 or l.bar2 == line.bar1])

            y_bus[bar2_index, bar2_index] = sum(
                [l.admittance for l in self.circuit.lines if l.bar1 == line.bar2 or l.bar2 == line.bar2])

        self.add_step('Y_bus', sp.Matrix(y_bus))
        return y_bus

    def get_power_esp_array(self) -> np.ndarray:
        power_g = np.zeros((len(self.circuit.bars)), dtype=complex)
        power_d = np.zeros((len(self.circuit.bars)), dtype=complex)
        for i, bar in enumerate(self.circuit.bars):
            if isinstance(bar, LoadBar):
                power_d[i] = bar.power
            elif isinstance(bar, RegulatorBar):
                power_g[i] = bar.active_power
            if not isinstance(bar, SlackBar):
                self.add_step(f'S^esp_{bar.name}', sp.parse_expr(
                    f'(S_G{bar.name} - S_D{bar.name})/S_base'))
                self.add_step(f'S^esp_{bar.name}', power_g[i] - power_d[i])
        power_esp = power_g - power_d
        return power_esp

    def get_initial_voltage_array(self) -> np.ndarray:
        voltages = np.ones(len(self.circuit.bars), dtype=complex)
        for i, bar in enumerate(self.circuit.bars):
            if isinstance(bar, SlackBar):
                voltages[i] = bar.voltage
            elif isinstance(bar, RegulatorBar):
                voltages[i] = bar.voltage_module
            self.add_step(f'V^0_{bar.name}', voltages[i])
        return voltages

    def get_bar_power(self, bar: Bar) -> complex:
        voltages = self.__voltage_array
        y_bus = self.__y_bus_array
        i = self.circuit.get_bar_index(bar)
        summation = sum([y_bus[i, j]*voltages[j]
                        for j in range(len(voltages)) if i != j])
        S = (voltages[i].conjugate()*(y_bus[i, i]
             * voltages[i] + summation)).conjugate()
        return S

    def get_bar_voltage(self, bar: Bar) -> complex:
        voltages = self.__voltage_array
        y_bus = self.__y_bus_array
        power_esp = self.__power_esp_array
        i = self.circuit.get_bar_index(bar)
        I = power_esp[i].conjugate()/voltages[i].conjugate()
        summation = sum([y_bus[i, j]*voltages[j]
                        for j in range(len(voltages)) if i != j])
        V = (I - summation)/y_bus[i, i]
        return V

    def solve(self, repeat: int = 1, max_error: float = None):
        self.__steps = []
        self.__y_bus_array = self.get_y_bus_array()
        self.__voltage_array = self.get_initial_voltage_array()
        self.__power_esp_array = self.get_power_esp_array()
        if max_error is None:
            for _ in range(repeat):
                self.__update_bar_voltages()
        else:
            while True:
                voltages_old = self.__voltage_array.copy()
                self.__update_bar_voltages()
                voltages_new = self.__voltage_array
                error = voltages_new - voltages_old
                real_error, imag_error = np.abs(error.real), np.abs(error.imag)
                if (np.all(real_error < max_error) and np.all(imag_error < max_error)):
                    break

        self.__update_bar_powers()
        self.__update_line_amperages()
        self.__update_line_powers()

    def get_voltage_expression(self, bar: Bar):
        i = self.circuit.get_bar_index(bar)
        voltage_array = self.__voltage_array
        S_symbol = sp.Symbol(f'S^esp_{bar.name}')
        V_symbol = sp.Symbol(f'V^({self.k})_{bar.name}')
        I_symbol = S_symbol.conjugate()/V_symbol
        summation_symbol = sum([sp.Symbol(
            f'Y_{bar.name}_{j+1}')*sp.Symbol(f'V^(k)_{j+1}') for j in range(len(voltage_array)) if i != j])
        Y_symbol = sp.Symbol(f'Y_{i+1}_{i+1}')
        V_expression = (I_symbol - (summation_symbol))/Y_symbol
        return V_expression

    def __update_bar_voltages(self):
        voltage_array = self.__voltage_array
        power_esp = self.__power_esp_array

        for i, bar in enumerate(self.circuit.bars):
            if isinstance(bar, LoadBar):
                voltage_array[i] = self.get_bar_voltage(bar)

                voltage_expression = self.get_voltage_expression(bar)
                self.add_step(f'V^({self.k + 1})_{bar.name}', voltage_expression)
                self.add_step(f'V^({self.k + 1})_{bar.name}', voltage_array[i])
            elif isinstance(bar, RegulatorBar):
                Q = self.get_bar_power(bar).imag
                P = power_esp[i].real
                power_esp[i] = P + 1j*Q
                V = self.get_bar_voltage(bar)
                V_real = math.sqrt(bar.voltage_module**2 - V.imag**2)
                voltage_array[i] = V_real + V.imag*1j

                voltage_expression = self.get_voltage_expression(bar)
                imag_voltage = sp.im(voltage_expression, evaluate=False)
                voltage_symbol = sp.Symbol(f'V^({self.k + 1})_{bar.name}')
                voltage_module_symbol = sp.Symbol(f'|{"{"}V_{bar.name}{"}"}|')
                self.add_step(sp.im(voltage_symbol), imag_voltage)
                real_voltage = sp.sqrt(voltage_module_symbol**2 - sp.im(voltage_symbol)**2, evaluate=False)
                self.add_step(sp.re(voltage_symbol), real_voltage)
                self.add_step(voltage_symbol, voltage_array[i])

        self.__voltage_array = voltage_array
        self.k += 1
        self.circuit.update_bar_voltages(voltage_array)

    def __update_bar_powers(self):
        power_array = np.zeros((len(self.circuit.bars)), dtype=complex)
        for i, bar in enumerate(self.circuit.bars):
            if isinstance(bar, SlackBar):
                power_array[i] = self.get_bar_power(bar)
            elif isinstance(bar, RegulatorBar):
                power_array[i] = self.__power_esp_array[i]
        self.circuit.update_bar_powers(power_array)

    def __update_line_amperages(self):
        y_bus = self.__y_bus_array
        amperage_array = np.zeros(y_bus.shape, dtype=complex)
        y = y_bus*(np.identity(len(y_bus))*2 - 1)
        for line in self.circuit.lines:
            bar1 = line.bar1
            bar2 = line.bar2
            bar1_index = self.circuit.get_bar_index(bar1)
            bar2_index = self.circuit.get_bar_index(bar2)
            I = (bar1.voltage - bar2.voltage)*y[bar1_index, bar2_index]
            amperage_array[bar1_index, bar2_index] = I
            amperage_array[bar2_index, bar1_index] = -I
        self.circuit.update_line_amperages(amperage_array)

    def __update_line_powers(self):
        power_array = np.zeros(
            (len(self.circuit.bars), len(self.circuit.bars)), dtype=complex)
        for line in self.circuit.lines:
            bar1_index = self.circuit.get_bar_index(line.bar1)
            bar2_index = self.circuit.get_bar_index(line.bar2)

            I = line.amperage

            V1 = line.bar1.voltage
            S12 = V1*I.conjugate()
            power_array[bar1_index, bar2_index] = S12

            V2 = line.bar2.voltage
            S21 = V2*(-I).conjugate()
            power_array[bar2_index, bar1_index] = S21
        self.circuit.update_line_powers(power_array)
