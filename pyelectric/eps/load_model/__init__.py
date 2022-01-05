def check_max_error(V_load: complex, V_load_old: complex, max_error: float) -> bool:
    real_error = abs(abs(V_load) - abs(V_load_old))
    imag_error = abs(V_load.imag - V_load_old.imag)
    if real_error <= max_error or imag_error <= max_error:
        return True
    return False


def constant_current(S_load: complex, Z_line: complex, V: complex) -> complex:
    V_load = V
    I = (S_load/V_load).conjugate()
    V_line = Z_line*I
    V_load = V - V_line
    return V_load


def constant_power(S_load: complex, Z_line: complex, V: complex, max_error: float) -> complex:
    V_load = V
    V_load_old: complex = max_error + 1

    while True:
        I = (S_load.conjugate()/V_load)
        V_line = Z_line*I
        V_load = V - V_line

        if check_max_error(V_load, V_load_old, max_error):
            break
        V_load_old = V_load
    return V_load


def constant_impedance(S_load: complex, Z_line: complex, V: complex, max_error: float) -> complex:
    V_load = V
    V_load_old: complex = max_error + 1

    while True:
        Z_load = (V**2/S_load).conjugate()
        I = V_load/Z_load
        V_line = Z_line*I
        V_load = V - V_line

        if check_max_error(V_load, V_load_old, max_error):
            break
        V_load_old = V_load
    return V_load
