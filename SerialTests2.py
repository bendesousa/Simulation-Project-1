import pandas as pd
from scipy.stats import chi2

df = pd.read_excel("drivers.xlsx")

arrival_time = df["arrival_time"].tolist()
offline_time = df["offline_time"].tolist()

initial_location = df["initial_location"].str.strip('()').str.split(',', expand=True)
initial_location_X = initial_location[0].astype(float).tolist()
initial_location_Y = initial_location[1].astype(float).tolist()
initial_location=[initial_location_X,initial_location_Y]

current_location = df["current_location"].str.strip('()').str.split(',', expand=True)
current_location_X = current_location[0].astype(float).tolist()
current_location_Y = current_location[1].astype(float).tolist()
current_location=[current_location_X,current_location_Y]

m=len(arrival_time)

#find inter-event times
inter=[]
for i in range(m-1):
    inter.append(arrival_time[i+1]-arrival_time[i])

#define F function
def F(x):
    sum=0
    for j in range(m-1):
        if inter[j]<=x:
            sum+=1        
    return sum/(m-1)

#find random variates of uniform(0,1)
U=[]
for i in range(m-1):
    U.append(F(inter[i]))

d=2
#create d-dimentional vectors
vect=[[],[]]
for i in range(m-1):
    if i%2==0:
        vect[0].append(U[i])
    if i%2==1:
        vect[1].append(U[i])
        
n= min(len(vect[0]),len(vect[1]))
        
#Find number of obserbations in bin x,y
k=10
O=[[0 for _ in range(k)] for _ in range(k)]
#O=[[0]*k]*k
for x in range(k):
    for y in range(k):
        for i in range(n):
            if x/k<=vect[0][i] and vect[0][i]<=(x+1)/k and y/k<=vect[1][i] and vect[1][i]<=(y+1)/k:
                O[x][y]+=1
    
#Expected number of observations:
E=n/(k**d)

#Find X^2
chi=0
for x in range(k):
    for y in range(k):
        chi+=(O[x][y]-E)**2
chi=chi/E

alpha=0.05
chi_stat = chi2.ppf(1 - alpha, (k**d)-1)

print("X^2 is: ", chi)
print("X^2_{k^d-1,1-a} is: ", chi_stat)
if chi>chi_stat:
    print("Driver inter-arrival times are not independent with ",(1-alpha)*100,"% confidence")
else:
    print("Not enough evidence to reject that driver inter-arrival times are independent")
    
#Now we repeat the same procedure for the length of a driver's shift
m=len(arrival_time)

#find inter-event times
inter=[]
for i in range(m):
    inter.append(offline_time[i]-arrival_time[i])

m=len(inter)
#define F function
def F(x):
    sum=0
    for j in range(m):
        if inter[j]<=x:
            sum+=1        
    return sum/(m)

#find random variates of uniform(0,1)
U=[]
for i in range(m):
    U.append(F(inter[i]))

d=2
#create d-dimentional vectors
vect=[[],[]]
for i in range(m):
    if i%2==0:
        vect[0].append(U[i])
    if i%2==1:
        vect[1].append(U[i])
        
n= min(len(vect[0]),len(vect[1]))
        
#Find number of obserbations in bin x,y
k=10
O=[[0 for _ in range(k)] for _ in range(k)]
#O=[[0]*k]*k
for x in range(k):
    for y in range(k):
        for i in range(n):
            if x/k<=vect[0][i] and vect[0][i]<=(x+1)/k and y/k<=vect[1][i] and vect[1][i]<=(y+1)/k:
                O[x][y]+=1
    
#Expected number of observations:
E=n/(k**d)

#Find X^2
chi=0
for x in range(k):
    for y in range(k):
        chi+=(O[x][y]-E)**2
chi=chi/E

alpha=0.05
chi_stat = chi2.ppf(1 - alpha, (k**d)-1)

print("X^2 is: ", chi)
print("X^2_{k^d-1,1-a} is: ", chi_stat)
if chi>chi_stat:
    print("Period lenghts of driver shifts are not independent with ",(1-alpha)*100,"% confidence")
else:
    print("Not enough evidence to reject that period lenghts of driver shifts are independent")
    
#Let's repeat the same procedure with the driver initial locations
for index in range(len(initial_location)):
    #find random variates of uniform(0,1)
    U=[x/20 for x in initial_location[index]]

    d=2
    #ensure the sample is even sized
    #create d-dimentional vectors
    vect=[[],[]]
    for i in range(m):
        if i%2==0:
            vect[0].append(U[i])
        if i%2==1:
            vect[1].append(U[i])
            
    n= min(len(vect[0]),len(vect[1]))
        
    #Find number of obserbations in bin x,y
    k=10
    O=[[0 for _ in range(k)] for _ in range(k)]
    for x in range(k):
        for y in range(k):
            for i in range(n):
                if x/k<=vect[0][i] and vect[0][i]<=(x+1)/k and y/k<=vect[1][i] and vect[1][i]<=(y+1)/k:
                    O[x][y]+=1
    
    #Expected number of observations:
    E=n/(k**d)

    #Find X^2
    chi=0
    for x in range(k):
        for y in range(k):
            chi+=(O[x][y]-E)**2
    chi=chi/E

    alpha=0.05
    chi_stat = chi2.ppf(1 - alpha, (k**d)-1)

    print("X^2 is: ", chi)
    print("X^2_{k^d-1,1-a} is: ", chi_stat)
    if chi>chi_stat:
        if index==0:
            print("X-coordinates of driver initial locations are not independent with ",(1-alpha)*100,"% confidence")
        else:
            print("Y-coordinates of driver initial locations are not independent with ",(1-alpha)*100,"% confidence")
    else:
        if index==0:
            print("Not enough evidence to reject that X-coordinates of driver initial locations are independent")
        else:
            print("Not enough evidence to reject that Y-coordinates of driver initial locations are independent")

#Let's repeat the same procedure with the current locations
for index in range(len(current_location)):
    #find random variates of uniform(0,1)
    U=[x/20 for x in current_location[index]]

    d=2
    #create d-dimentional vectors
    vect=[[],[]]
    for i in range(m):
        if i%2==0:
            vect[0].append(U[i])
        if i%2==1:
            vect[1].append(U[i])
            
    n= min(len(vect[0]),len(vect[1]))
        
    #Find number of obserbations in bin x,y
    k=10
    O=[[0 for _ in range(k)] for _ in range(k)]
    for x in range(k):
        for y in range(k):
            for i in range(n):
                if x/k<=vect[0][i] and vect[0][i]<=(x+1)/k and y/k<=vect[1][i] and vect[1][i]<=(y+1)/k:
                    O[x][y]+=1
    
    #Expected number of observations:
    E=n/(k**d)

    #Find X^2
    chi=0
    for x in range(k):
        for y in range(k):
            chi+=(O[x][y]-E)**2
    chi=chi/E

    alpha=0.05
    chi_stat = chi2.ppf(1 - alpha, (k**d)-1)

    print("X^2 is: ", chi)
    print("X^2_{k^d-1,1-a} is: ", chi_stat)
    if chi>chi_stat:
        if index==0:
            print("X-coordinates of current locations are not independent with ",(1-alpha)*100,"% confidence")
        else:
            print("Y-coordinates of current locations are not independent with ",(1-alpha)*100,"% confidence")
    else:
        if index==0:
            print("Not enough evidence to reject that X-coordinates of current locations are independent")
        else:
            print("Not enough evidence to reject that Y-coordinates of current locations are independent")
