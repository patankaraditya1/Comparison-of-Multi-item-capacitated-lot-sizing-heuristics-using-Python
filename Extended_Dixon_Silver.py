import sys
import csv
import pandas as pd

if (len(sys.argv) == 2):
	locationsFolder		= str(sys.argv[1])		# Ex: Data_1 or Data_2

else:
	print 'ERROR: You passed', len(sys.argv)-1, 'input parameters.'
	quit()

Data = 'Sample_Data/%s/Data.csv' % locationsFolder
Machine_hours = 'Sample_Data/%s/Machine_hours.csv' % locationsFolder
Forecasted_demand = 'Sample_Data/%s/Forecasted_demand.csv' % locationsFolder


l = 0
N = []
h = {}
S = {}
Xmax = {}
kinv = {}
SS = {}
Iin = {}
Iend = {}
with open(Data, 'rb') as csvfile:
    spamreader = csv.reader(csvfile , delimiter =',', quotechar ='|')
    for row in spamreader :
    # Only read rows that do NOT start with the "%" character .
        if ( row [0][0] != '%') :
            N.append(int( row [0]))
            h[int(row[0])] = float(row[1])
            S[int(row[0])] = float(row[2])
            Xmax[int(row[0])] = int(row[3])
            kinv[int(row[0])] = float(row[4])
            SS[int(row[0])] = float(row[5])
            Iin[int(row[0])] = float(row[6])
            Iend[int(row[0])] = float(row[7])


#print kinv
#print Iin


H = []
C = {}

with open (Machine_hours, 'rb') as csvfile :
    spamreader = csv.reader(csvfile , delimiter =',', quotechar ='|')
    for row in spamreader :
    # Only read rows that do NOT start with the "%" character .
        if ( row [0][0] != '%') :
            H.append(int(row[0]))
            C[int(row[0])] = int(row[1])

csvFile = Forecasted_demand
df = pd.read_csv(csvFile)

#print df

D = {}
for i in range(0, len(N)):
    for j in range(0 , len(H)):
        D[i+1,j+1] = df.iat[i,j]

#print D[12,12]

Irem = {}
d = {}
l = 0
for i in N:
    Irem[i] = Iin[i] - SS[i]
for i in N:
    for j in H:
        d[i,j,l] = D[i,j]
j = 1

for i in N:
    for j in H:
        if (Irem[i] > D[i, j]):
            d[i, j, l] = 0
        elif (Irem[i] <= D[i, j]):
            d[i, j, l] = D[i, j] - Irem[i]
        Irem[i] = Irem[i] - D[i,j]
        if(Irem[i] < 0):
            break
for i in N:
    d[i,len(H), l] = D[i,len(H)] + Iend[i] - SS[i]

#print d[1,2,0]

sum_C = 0
CR = {}
sum_CR = 0
for j in H:
    sum_CR_I = 0
    #print j
    for i in N:
        sum_CR_I += int(d[i,j,l]/float(kinv[i]))
    CR[j] = sum_CR_I
    #print CR[j]
    sum_C += C[j]
    sum_CR += CR[j]
#print sum_CR
#print sum_C

# Feasibility Check
if (sum_CR <= sum_C):
    print "FEASIBLE!!!"
else:
    print "INFEASIBLE"
    exit()

# Converting multisetup problem into single setup
dmax = {}
n = {}
sum_n = 0
for i in N:
    dmax[i] = max(d[i,j,l] for j in H)
    #print dmax[i],",",Xmax[i]
    n[i] = int((dmax[i]/Xmax[i]) - 1)
    sum_n += n[i]

len_Ndash = len(N) + sum_n
#print len_Ndash

Ndash = []
for i in N:
    for l in range(0, n[i]+1):
        Ndash.append((i,l))
#print Ndash
drem ={}
for i in N:
    for j in H:
        drem[i,j] = d[i,j,l]
for i in N:
    for j in H:
        for l in range(0, n[i]+1):
            if(drem[i,j] <= Xmax[i]):
                d[i,j,l] = drem[i,j]
                drem[i,j] = 0
            elif(drem[i,j] > Xmax[i]):
                d[i,j,l] = Xmax[i]
                drem[i,j] = drem[i,j] - Xmax[i]

#print len(d)

for i in N:
    for l in range(0, n[i]+1):
        h[i,l] = h[i]
        S[i,l] = S[i]
        kinv[i,l] = kinv[i]

#print h
X = {}
Xrem = {}
RC = {}
R = 1
for i in N:
    for j in H:
        for l in range(0, n[i]+1):
            X[i,j,l] = d[i,j,l]
            Xrem[i,j,l] = Xmax[i] - X[i,j,l]  #######



# Define step 4.12
def Step1(R):
    x = {}
    for i in N:
        for j in H:
            sum = 0
            for l in range(0, n[i]+1):
                sum += X[i,j,l]
            x[i,j] = sum
    #print "x:", x[1,1]

    I={}
    t = 1
    for i in N:
        I[i,t]=Iin[i]+x[i,t]-D[i,t]
        for j in range(2,len(H)):
            I[i,j] = I[i,j-1]+x[i,j]- D[i,j]
        I[i,len(H)] = Iend[i]
    #print"I:",I[11,12]
    sum1 = 0
    sum2 = 0
    for i in N:
        for t in H:
            sum1 += (h[i]*(I[i,t] - SS[i]))
    print "Inventory cost:",sum1

    for i in N:
        for j in H:
            if(x[i,j] != 0):
                sum2 += S[i]

    print"Setup Cost:",sum2
    print "Total cost:", sum1+sum2
    x_list = []
    I_list = []
    for i in N:
        list = []
        list1 = []
        for j in H:
            list.append(x[i, j])
            list1.append(I[i, j])
        x_list.append(list)
        I_list.append(list1)
        # print x_list

    df = pd.DataFrame(x_list)
    df1 = pd.DataFrame(I_list)
    # df = df.transpose()
    # print df
    # print df1
    if(locationsFolder == 'Data_1'):
        df.to_csv('Solution_Dixon_1.csv')
        print"Solution saved to Solution_Dixon_1.csv"
        df1.to_csv('Inventory_Dixon_1.csv')
        print"Inventory solution saved to Inventory_Dixon_1.csv"
    else:
        df.to_csv('Solution_Dixon_2.csv')
        print"Solution saved to Solution_Dixon_2.csv"
        df1.to_csv('Inventory_Dixon_2.csv')
        print"Inventory solution saved to Inventory_Dixon_2.csv"

# Start at Step 4.3
def Step3(R,d):
    T = {}
    for i in N:
        for l in range(0, n[i]+1):
            T[i,l] = 1

    #print len(T)
    sum = 0
    for i in N:
        for l in range(0, n[i]+1):
            #print"d dor RC:", d[i,R,l]
            sum += int(d[i, R, l]/float(kinv[i,l]))

    RC[R] = C[R] - sum
    #print"RC:",RC
    global Idash
    Idash = {}
    for i in N:
        for j in range(0, len(H)+1):
            for l in range(0, n[i]+1):
                Idash[i, j, l] = 0

    # Step 4.5
    def Step(R):
        AP = {}
        sum_C = 0
        CR = {}
        sum_CR = 0
        for j in H:
            sum_CR_I = 0
            sum_AP_I = 0
            #print j
            for i in N:
                for l in range(0, n[i]+1):
                    sum_CR_I += int(d[i, j, l]/float(kinv[i, l]))
                    sum_AP_I += int((Idash[i, j-1, l] - Idash[i, j, l])/kinv[i,l])
            CR[j] = sum_CR_I
            AP[j] = sum_AP_I
            #print CR[j]
        #print CR
        #print C
        T_t = []

        for t in range(R, len(H)-R): #######
            sum_AP_t = 0
            sum_CR_t = 0

            for j in range(R+1, R+t):
                sum_AP_t += AP[j]
                sum_CR_t += (CR[j] - C[j])
            if(sum_AP_t < sum_CR_t):
                T_t.append(t)

        if(T_t != []):
            tc = min(T_t)
        else:
            tc = len(H)+1

        #print tc

        idash = []
        Xcan = {}
        ldash = []
        rem_cap = {}
        rem_cap[R]= RC[R]
        for i in N:
            for l in range(0, n[i]+1):
                #print"i:",i,"l:",l
                #print "R:",R,"T:",T[i,l]
                if(T[i,l] <= len(H)-R):
                    T[i,l] = T[i,l]
                else:
                    T[i,l] = len(H)-R

                Xcan[i,l] = min(d[i, R+T[i,l], l], Xrem[i, R, l])
                #print "Xcan for idash:",Xcan[i,l]/kinv[i,l]
                #print "RC for idash:",RC[R]
                #print "Rem cap:", rem_cap[R]
                #print "T and tc for idash:",T[i,l]," and ", tc, "R:", R
                if ((T[i, l] < tc) and (Xcan[i,l] > 0) and (rem_cap[R]- (Xcan[i,l]/kinv[i,l]))>=0):
                    rem_cap[R] -= int(Xcan[i,l]/kinv[i,l])
                    idash.append(i)
                    ldash.append(l)
                    #print "idash:", idash
                    #print "ldash:", ldash

        # print "idash:",idash
        # print "ldash:", ldash

        # Check again if wrong
        U = {}
        for i in range(0, len(idash)):
                #print"idash:",idash[i]
                #print"ldash:", ldash[i]
                #print "T:",T[idash[i],ldash[i]]
                sum = 0
                for j in (R, R + T[idash[i], ldash[i]]):
                    sum += ((j - R) * d[idash[i], j, ldash[i]])
                #print T[idash[i],ldash[i]]
                # print "i,l",idash[i],ldash[i]
                # print d[i,T[idash[i],ldash[i]]+1,l]
                if(T[idash[i], ldash[i]] != 0):
                    AC_T = ((S[idash[i], ldash[i]] + (h[idash[i], ldash[i]] * sum)) / T[idash[i], ldash[i]])
                    AC_T1 = ((S[idash[i], ldash[i]] + (h[idash[i], ldash[i]] * sum)) / (T[idash[i], ldash[i]] + 1))
                else:
                    AC_T = 0
                    AC_T1 = ((S[idash[i], ldash[i]] + (h[idash[i], ldash[i]] * sum)) / (T[idash[i], ldash[i]] + 1))
                #print "d:",d[idash[i], T[idash[i], ldash[i]] + 1, ldash[i]]
                if (d[idash[i], T[idash[i], ldash[i]] + 1, ldash[i]] != 0):
                    U[idash[i], ldash[i]] = ((kinv[idash[i], ldash[i]] * (AC_T - AC_T1)) / float(d[idash[i], T[idash[i], ldash[i]] + 1, ldash[i]]))
                else: ###### See for it
                   U[idash[i], ldash[i]] = 'INF'
        #print "U:", U
        if(bool(U) == True):
            Umax_key = max(U, key=U.get)
        else:
            Umax_key = 0
            U[Umax_key] = 0

        #print Umax_key
        if (U[Umax_key] > 0 and ((RC[R] - (Xcan[Umax_key[0], Umax_key[1]] / kinv[Umax_key[0], Umax_key[1]])) >= 0)):
            X[Umax_key[0], R, Umax_key[1]] += Xcan[Umax_key[0], Umax_key[1]]
            for j in range(R + 1, R + T[Umax_key[0], Umax_key[1]] + 1):
                Idash[Umax_key[0], j, Umax_key[1]] += Xcan[Umax_key[0], Umax_key[1]]
            Xrem[Umax_key[0], R + T[Umax_key[0], Umax_key[1]], Umax_key[1]] += Xcan[Umax_key[0], Umax_key[1]]
            X[Umax_key[0], R + T[Umax_key[0], Umax_key[1]], Umax_key[1]] -= Xcan[Umax_key[0], Umax_key[1]]
            d[Umax_key[0], R + T[Umax_key[0], Umax_key[1]], Umax_key[1]] -= Xcan[Umax_key[0], Umax_key[1]]
            #print "RC before decrement:", RC[R]
            RC[R] -= int(Xcan[Umax_key[0], Umax_key[1]] / kinv[Umax_key[0], Umax_key[1]])
            #print "RC inside if:", RC[R]
            Xrem[Umax_key[0], R, Umax_key[1]] -= Xcan[Umax_key[0], Umax_key[1]]
            T[Umax_key[0], Umax_key[1]] += 1
            #print "Goto step 4.5"
            Step(R)
            # continue from step 4.5
        else:
            # got Step 4.12
            if (tc > len(H)):
                R = R + 1
                if (R <= len(H)):
                    Step3(R,d)
                elif (R > len(H)):
                    Step1(R)

                    # Step1()
                    # print "Goto step 4.12"
            elif (tc < len(H)):
                Q_list = []
                for t in range(R + tc - 1, len(H) + 1):
                    sum = 0
                    for j in range(R + 1, t + 1):
                        sum += (CR[j] - C[j] - AP[j])
                    Q_list.append(sum)
                Q = max(Q_list)
                #print Q

                def Step2(R, Q):
                    idash = []
                    Xcan = {}
                    ldash = []
                    rem_cap1 = {}
                    rem_cap1[R] = RC[R]

                    for i in N:
                        for l in range(0, n[i] + 1):
                            Xcan[i, l] = min(d[i, R + T[i, l], l], Xrem[i, R, l])
                            #print "Xcan for idash:", Xcan[i, l]
                            #print "RC for idash:", RC[R]
                            #print "T and tc for idash:", T[i, l], " and ", tc
                            if ((T[i, l] < tc) and (Xcan[i, l] > 0) and (
                            (rem_cap1[R] - (Xcan[i, l] / kinv[i, l]) >= 0))):
                                rem_cap1[R] -= int(Xcan[i, l] / kinv[i, l])
                                idash.append(i)
                                ldash.append(l)

                    #print "idash:", idash
                    #print "ldash:", ldash

                    delta = {}
                    for i in range(0, len(idash)):
                        sum = 0
                        for j in (R, R + T[idash[i], ldash[i]]):
                            sum += ((j - R) * d[idash[i], j, ldash[i]])
                        # print T[idash[i],ldash[i]]
                        # print "i,l",idash[i],ldash[i]
                        # print d[i,T[idash[i],ldash[i]]+1,l]
                        AC_T = ((S[idash[i], ldash[i]] + h[idash[i], ldash[i]] * sum) / T[idash[i], ldash[i]])
                        AC_T1 = ((S[idash[i], ldash[i]] + h[idash[i], ldash[i]] * sum) / (T[idash[i], ldash[i]] + 1))
                        if (d[idash[i], T[idash[i], ldash[i]] + 1, ldash[i]] != 0):  #######
                            delta[idash[i], ldash[i]] = ((kinv[idash[i], ldash[i]] * (AC_T1 - AC_T)) / float(d[idash[i], T[idash[i], ldash[i]] + 1, ldash[i]]))
                    #print "delta:", delta
                    if (bool(delta) == True):
                        delta_min_key = min(delta, key=delta.get)

                        W = Xcan[delta_min_key[0], delta_min_key[1]] / kinv[delta_min_key[0], delta_min_key[1]]
                        if (Q > W):
                            X[delta_min_key[0], R, delta_min_key[1]] += Xcan[delta_min_key[0], delta_min_key[1]]
                            for j in range(R + 1, R + T[delta_min_key[0], delta_min_key[1]] + 1):
                                Idash[delta_min_key[0], j, delta_min_key[1]] += Xcan[delta_min_key[0], delta_min_key[1]]
                            Xrem[delta_min_key[0], R + T[delta_min_key[0], delta_min_key[1]], delta_min_key[1]] += Xcan[
                                delta_min_key[0], delta_min_key[1]]
                            X[delta_min_key[0], R + T[delta_min_key[0], delta_min_key[1]], delta_min_key[1]] -= Xcan[
                                delta_min_key[0], delta_min_key[1]]
                            d[delta_min_key[0], R + T[delta_min_key[0], delta_min_key[1]], delta_min_key[1]] -= Xcan[delta_min_key[0], delta_min_key[1]]
                            #print "RC before decrement:", RC[R]
                            RC[R] -= int(
                                Xcan[delta_min_key[0], delta_min_key[1]] / kinv[delta_min_key[0], delta_min_key[1]])
                            #print "RC inside if:", RC[R]
                            Xrem[delta_min_key[0], R, delta_min_key[1]] -= Xcan[delta_min_key[0], delta_min_key[1]]
                            Q = Q - W
                            T[delta_min_key[0], delta_min_key[1]] += 1
                            Step2(R, Q)

                        else:
                            IQ = int(Q * kinv[delta_min_key[0], delta_min_key[1]])
                            X[delta_min_key[0], R, delta_min_key[1]] += IQ
                            for j in range(R + 1, R + T[delta_min_key[0], delta_min_key[1]] + 1):
                                Idash[delta_min_key[0], j, delta_min_key[1]] += IQ
                            Xrem[delta_min_key[0], R + T[delta_min_key[0], delta_min_key[1]], delta_min_key[1]] += IQ
                            X[delta_min_key[0], R + T[delta_min_key[0], delta_min_key[1]], delta_min_key[1]] -= IQ
                            d[delta_min_key[0], R + T[delta_min_key[0], delta_min_key[1]], delta_min_key[1]] -= IQ
                            Xrem[delta_min_key[0], R, delta_min_key[1]] -= IQ

                    R = R + 1
                    if (R <= len(H)):
                        Step3(R,d)
                    elif (R > len(H)):
                        Step1(R)

                Step2(R, Q)
    Step(R)


Step3(R,d)
sum = 0
for i in N:
    sum += (C[i]-RC[i])

#print "sum:",sum


