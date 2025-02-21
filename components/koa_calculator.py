import math

def koa(qb:float,qd:float,qf:float,kd:float):    

     # Input validation
    if not (100 <= qb <= 300):
        return "Error: Qb must be between 20 and 50."   
    if not (100 <= qd <= 1000):
        return "Error: Qd must be between 100 and 1000."
    if not (0 <= qf <= 30):
        return "Error: Qf must be between 0 and 30."
    if not (100 <= kd <= 350):
        return "Error: Kd must be between 100 and 350."

    try:       
        kconv = (qb - kd) / kd * qf
        kdif = kd - kconv
        f1 = qb / (1 - qb / qd)
        f2 = (1 - kdif / qd) / (1 - kdif / qb)
        koa_value = f1 * math.log(f2)  # Use math.log for natural logarithm
        
        return kdif, koa_value
    
    except ZeroDivisionError:
        print("Error: Division by zero encountered.")
        return None, None
