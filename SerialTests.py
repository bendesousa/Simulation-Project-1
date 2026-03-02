import pandas as pd
from scipy.stats import chi2

df = pd.read_excel("riders.xlsx")

request_time = df["request_time"].tolist()
pickup_time = df["pickup_time"].tolist()

pickup_location = df["pickup_location"].str.strip('()').str.split(',', expand=True)
pickup_location_X = pickup_location[0].astype(float).tolist()
pickup_location_Y = pickup_location[1].astype(float).tolist()
pickup_location=[pickup_location_X,pickup_location_Y]

dropoff_location = df["dropoff_location"].str.strip('()').str.split(',', expand=True)
dropoff_location_X = dropoff_location[0].astype(float).tolist()
dropoff_location_Y = dropoff_location[1].astype(float).tolist()
dropoff_location=[dropoff_location_X,dropoff_location_Y]

m=len(request_time)

#find inter-event times
inter=[]
for i in range(m-1):
    inter.append(request_time[i+1]-request_time[i])

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
    print("Rider inter-arrival times are not independent with ",(1-alpha)*100,"% confidence")
else:
    print("Not enough evidence to reject that rider inter-arrival times are independent")
    
#Now we repeat the same procedure for pickup times
m=len(request_time)

#find inter-event times
inter=[]
for i in range(m):
    if pickup_time[i]>=0:
        inter.append(pickup_time[i]-request_time[i])

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
    print("Rider waiting times are not independent with ",(1-alpha)*100,"% confidence")
else:
    print("Not enough evidence to reject that rider waiting times are independent")
    
#Let's repeat the same procedure with the pick_up locations
for index in range(len(pickup_location)):
    #find random variates of uniform(0,1)
    U=[x/20 for x in pickup_location[index]]

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
            print("X-coordinates of pick up locations are not independent with ",(1-alpha)*100,"% confidence")
        else:
            print("Y-coordinates of pick up locations are not independent with ",(1-alpha)*100,"% confidence")
    else:
        if index==0:
            print("Not enough evidence to reject that X-coordinates of pick up locations are independent")
        else:
            print("Not enough evidence to reject that Y-coordinates of pick up locations are independent")

#Let's repeat the same procedure with the dropoff locations
for index in range(len(dropoff_location)):
    #find random variates of uniform(0,1)
    U=[x/20 for x in dropoff_location[index]]

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
            print("X-coordinates of dropoff locations are not independent with ",(1-alpha)*100,"% confidence")
        else:
            print("Y-coordinates of dropoff locations are not independent with ",(1-alpha)*100,"% confidence")
    else:
        if index==0:
            print("Not enough evidence to reject that X-coordinates of dropoff locations are independent")
        else:
            print("Not enough evidence to reject that Y-coordinates of dropoff locations are independent")