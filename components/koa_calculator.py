import math

def koa(qb:float,qd:float,qf:float,kd:float):    

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
