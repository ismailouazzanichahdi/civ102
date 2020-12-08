import numpy as np
import matplotlib.pyplot as plt
import copy

######################################################################################################### I ######################################################################################################### 

def center_finder(h, thickeness):
    '''
find the centroid of the cross section. Executed before the supports impacts the cross section.
    '''
    Area_side = h * thickeness
    Area_top = 100 * thickeness
    Area = Area_top + 2 * Area_side
    
    side_center = h/2
    top_center = h + (thickeness/2)
    return (1/Area) * (2 * Area_side * side_center + Area_top * top_center)


def New_center_finder(h, thickeness, depth):
    '''
find the centroid of the cross section taking into account the support. Executed after the supports impacts the cross section.
    '''
    Area_side = h * thickeness
    Area_top = 100 * thickeness
    Area_support = depth * thickeness
    Area = Area_top + 2 * Area_side + Area_support
    
    side_center = h/2 + depth
    top_center = h + (thickeness/2) + depth
    support_center = depth / 2
    return (1/Area) * (2 * Area_side * side_center + Area_top * top_center + Area_support * support_center)




def height_finder(h_initial, x, d, L):
    '''
find the height of the flange at point x starting from the left of the bridge.
    '''
    slope = (h_initial - 45) / (L - d)
    b = - slope * d
    return h_initial - (slope * x + b )


def depth_finder(depth_initial, x, L):
    '''
find the height of the support at x in the cross section.
    '''
    slope = depth_initial / 100
    b = L * slope - depth_initial
    return slope * x + b


# def center_finder(area, width, thickeness, h):
#     A_total = 2 * ( width * thickeness + h * thickeness)
#     y_bar = 

def Io_finder_side(h, thickeness):
    return (thickeness * pow(h, 3))/12

def Io_finder_horizontal(width, thickeness):
    return (width * pow(thickeness, 3))/12

def Io_finder_support(depth, thickeness):
    return(thickeness *  pow(depth, 3)) / 12

def di2_finder(h, y):
    return pow(h - y, 2)


def I_finder(iterations, L, d, h_initial, depth_initial):
    I_values = [0] * iterations
    x_values = [0] * iterations
    for x in range(iterations):
        x_values[x] =  0 + x * (L / iterations)
    
    
    for i in range(iterations):
        if x_values[i] >= d and x_values[i] < L - 100 :

            h = height_finder(h_initial, x_values[i], d, L)
            last_h = h
            y = center_finder(h, thickeness)
            I_values[i] = 2 * (Io_finder_side(h, thickeness) + thickeness * h * di2_finder(h/2, y) ) +  Io_finder_horizontal(width, thickeness) + width * thickeness * di2_finder(h+(thickeness/2),y)
       
        elif  x_values[i] >= L - 100:
            h = height_finder(h_initial, x_values[i], d, L)
            depth = depth_finder(depth_initial, x_values[i], L)
            last_h = h
            y = New_center_finder(h, thickeness, depth)
            I_values[i] = 2 * (Io_finder_side(h, thickeness) + thickeness * h * di2_finder(h/2, y) ) +  Io_finder_horizontal(width, thickeness) + width * thickeness * di2_finder(h+(thickeness/2),y) + Io_finder_support(depth, thickeness) + depth * thickeness * di2_finder(depth, y) 
       
            
            
            
        else:
            y = h_initial/2
            I_values[i] = 2 * (Io_finder_side(h_initial, thickeness) + thickeness * h_initial * di2_finder(h_initial/2, y) ) + 2 *  Io_finder_horizontal(width, thickeness) + 2 * width * thickeness * di2_finder(h_initial+(thickeness/2),y)
    
    return x_values, I_values

######################################################################################################### M ######################################################################################################### 

def M_finder(Shear_Force, Force_Application, L, iterations):
    M_values = [0] * iterations
    x_values = [0] * iterations
    
    M_values[0] = 0
    
    
    for x in range(iterations):
        x_values[x] =  0 + x * (L / iterations)
        
    for i in range(1, iterations):
        if x_values[i] < Force_Application:
            M_values[i] = M_values[i-1] + (L/ iterations) * Shear_Force
        else:
            M_values[i] = M_values[i-1]
            
    return x_values, M_values
        
def Curvature_finder(L, iterations, M_values, I_values, E):
    Phi_values = [0] * iterations
    x_values = [0] * iterations   
    
    for x in range(iterations):
        x_values[x] =  0 + x * (L / iterations)
        
    for i in range(iterations):
        Phi_values[i] = M_values[i]/(E * I_values[i])

    return x_values, Phi_values


def Graph_finder(x_values, M_values, I_values, Phi_values, L, h_initial, d):
    Total_L = 2* L
    M_values_right = M_values[::-1]
    I_values_right = I_values[::-1]
    x_values_right = [0] * len(x_values)
    
    
    for i in range(len(x_values)):
        x_values_right[i] = L + x_values[i]
        
    M = M_values + M_values_right
    I = I_values + I_values_right
    x = x_values + x_values_right
    
    
    iterations = len(x)
    Phi = [0] * iterations
    for i in range(iterations):
        Phi[i] = M[i]/(E * I[i])
        
    h_values = [0] * len(x_values)
    for i in range(len(x_values)):
        h_values[i] = 100 - height_finder(h_initial, x_values[i], d, L)
    
    h = h_values + h_values[::-1]
    

    return x, Phi, I, M, h


def Deflection_finder(Phi, L):
    Area_under_curvature = 0
    
    
    for i in range(L):
        Area_under_curvature += Phi[i] * 1
        
    return Area_under_curvature

def Centroid_finder(Area_under_curvature, x, Phi, L):
    Area_to_left = 0
    Area_to_right = Area_under_curvature    
    i = 0
    # last_x = 0
    # mindiff = max(Phi)

    for i in range(len(x)) :
        Area_to_left +=  Phi[i] 
        Area_to_right -= Phi[i] 
        if Area_to_left >= Area_to_right:
            return x[i]
        i += 1
        
    return 0




def new_M_finder(maxM, M, Shear_Force, L, iterations):
    M_test = [0] * iterations
    x_values = [0] * iterations
    
    M_values[0] = 0
    
    
    for x in range(iterations):
        x_values[x] =  0 + x * (L / iterations)
        
    for i in range(1, iterations):
        M_test[i] = M_test[i-1] + (L/ iterations) * Shear_Force

            
    return x_values, M_test







if __name__ == "__main__":
    d = 30
    width = 100 
    h_initial = 100
    L = 490
    E = 4000
    thickeness = 1.27
    
    depth_initial = 600
    
    iterations = int(L)
    
    x_values, I_values = I_finder(iterations, L, d, h_initial, depth_initial)
    plt.figure(1)
    plt.xlabel('x [mm] along the beam')
    plt.ylabel('I [mm^4]')
    plt.plot(x_values, I_values)
    
    Shear_Force = 1/2 #Enter P/2 here
    Force_Application = 295
    plt.figure(2)
    x_values, M_values = M_finder(Shear_Force, Force_Application, L, iterations)
    # plt.xlabel('x [mm] along the beam')
    # plt.ylabel('Moment [XX mm]')
    # plt.plot(x_values, M_values)
    
    
    plt.figure(3)
    x_values, Phi_values = Curvature_finder(L, iterations, M_values, I_values, E)
    # plt.xlabel('x [mm] along the beam')
    # plt.ylabel('Moment [rad/mm]')
    # plt.plot(x_values, Phi_values)
    
    ftsize = 20
    
    x, Phi, I, M, h= Graph_finder(x_values, M_values, I_values, Phi_values, L, h_initial, d)
    fig4, axs = plt.subplots(3, figsize=(30,16))
    axs[0].plot(x, Phi)
    axs[0].set_title("Curvature Diagram",  fontsize= ftsize)
    axs[1].plot(x, I)
    axs[1].set_title("I values", fontsize= ftsize)
    axs[2].plot(x, M)
    axs[2].set_title("Bending Moment Diagram", fontsize= ftsize)

    fig4.suptitle("Diagrams without center support", fontsize= 30)
    print("Without center support: ")
    print("Max moment:", max(M))
    print("Max Phi:", max(Phi))
    Area_under_curvature = Deflection_finder(Phi, L)
    print("Area under Phi until x = L/2:", Area_under_curvature)
    print("Centroid of Area under phi until x = L/2:", Centroid_finder(Area_under_curvature, x, Phi, L))
    
    maxM = 245
    print("")
    
    x_values, M_test = new_M_finder(maxM, M, Shear_Force, L, iterations)
    x_values, Phi_test = Curvature_finder(L, iterations, M_test, I_values, E)
    
    x, New_Phi, I, New_M, h= Graph_finder(x_values, M_test, I_values, Phi_test, L, h_initial, d)
    fig5, axi = plt.subplots(3, figsize=(30,16))
    axi[0].plot(x, New_Phi)
    axi[0].set_title("Curvature Diagram", fontsize= ftsize)
    axi[1].plot(x, I)
    axi[1].set_title("I values", fontsize= ftsize)
    axi[2].plot(x, New_M)
    axi[2].set_title("Bending Moment Diagram", fontsize= ftsize)


    fig5.suptitle("Diagrams with center support", fontsize= 30)

    New_Area_under_curvature = Deflection_finder(New_Phi, L)
    print("With center support: ")
    print("Max moment:", max(New_M))
    print("Max Phi:", max(New_Phi))
    print("Area under Phi until x = L/2:", New_Area_under_curvature)
    print("Centroid of Area under phi until x = L/2:", Centroid_finder(New_Area_under_curvature, x, New_Phi, L))
    
    # print('')
    # tPhi = [20] * 100
    # tx = [0] * 100
    # for i in range(100):
    #     tx[i] = i
    # print(tPhi)
    # tArea = Deflection_finder(tPhi, 100)
    # print(tArea)
    # tc = Centroid_finder(tArea, tx, tPhi, 100)
    # print(tc)