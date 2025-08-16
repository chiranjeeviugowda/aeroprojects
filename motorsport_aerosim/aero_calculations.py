import math

def calculate_downforce(rho, velocity, area, cl):
    return 0.5 * rho * velocity ** 2 * area * cl

def calculate_drag(rho, velocity, area, cd):
    return 0.5 * rho * velocity ** 2 * area * cd

def aoa_to_coefficients(aoa_deg):
    
    aoa_rad = math.radians(aoa_deg)
    cl = 2 * math.pi * aoa_rad  # Lift coefficient estimate
    cd = 0.02 + (cl ** 2) / (math.pi * 0.9 * 2.0)#Parabolic drag polar
    return cl, cd
