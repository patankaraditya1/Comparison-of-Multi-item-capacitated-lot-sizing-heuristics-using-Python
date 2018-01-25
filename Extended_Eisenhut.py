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

N =[]
h = {}
S = {}
kinv = {}
SS ={}
Iin ={}
Iend = {}

with open(Data, 'rb') as csvfile:
    spamreader = csv.reader(csvfile , delimiter =',', quotechar ='|')
    for row in spamreader :
    # Only read rows that do NOT start with the "%" character .
        if ( row [0][0] != '%') :
            N.append(int( row [0]))
            h[int(row[0])] = float(row[1])
            S[int(row[0])] = float(row[2])
            # Xmax[int(row[0])] = int(row[3])
            kinv[int(row[0])] = float(row[4])
            SS[int(row[0])] = float(row[5])
            Iin[int(row[0])] = float(row[6])
            Iend[int(row[0])] = float(row[7])

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
#print len(H)

#print df

D = {}
for i in range(0, len(N)):
    for j in range(0 , len(H)):
        D[i+1,j+1] = int(df.iat[i,j]/kinv[i+1])

#print D[12,12]

Irem = {}
d = {}
for i in N:
    Irem[i] = int((Iin[i] - SS[i])/kinv[i])
for i in N:
    for j in H:
        d[i,j] = D[i,j]
j = 1

for i in N:
    for j in H:
        if (Irem[i] > D[i, j]):
            d[i, j] = 0
        elif (Irem[i] <= D[i, j]):
            d[i, j] = D[i, j] - Irem[i]
        Irem[i] = Irem[i] - D[i,j]
        if(Irem[i] < 0):
            break
for i in N:
    d[i,len(H)] = D[i,len(H)] + int(Iend[i]/kinv[i]) - int(SS[i]/kinv[i])
#print len(d)
# d = {}
# for i in range(0, len(N)):
#     for j in range(0 , len(H)):
#         d[i+1,j+1] = df.iat[i,j]
# print d
sum_c = 0
sum_d = 0
for k in H:
    sum_c += C[k]
    for i in N:
        sum_d += d[i,k]
    #print "sum_d:",sum_d

if(sum_c>=sum_d):
    print "FEASIBLE!!!"
else:
    print "INFEASIBLE"


RC ={}
R = 1
x ={}
a = 1
def Step1(R,d,x):

    B = {}
    sum = 0
    for i in N:
        sum += d[i,R]
    RC[R] = C[R] - sum


    def Step6(R, a, d, x, RC):
        #print "Entered feedback with R:",R," With a =", a
        #print "x:", x
        sum = 0
        for i in N:
            sum += d[i, R]
        INF = {}
        if (sum > C[R]):
            INF[R] = sum - C[R]
        else:
            INF[R] = 0
        #print "INF:",INF
        L = {}
        for i in N:
            if(d[i,R]>0):#######
                L[i] = min(INF[R], d[i, R])
            #######
            else:
                L[i] = INF[R]


        #print "L:",L
        Mstar = []
        for i in N:
            if (d[i, R - a] != 0):
                Mstar.append(i)
        #print"Mstar:",Mstar
        M = {}
        for i in Mstar:
            M[i] = a * L[i] * h[i]
        #print "M:",M

        q = min(M, key=M.get)
        #print"q:",q

        E = min(RC[R - a], L[q])
        #print "E:",E
        d[q, R] -= E
        #print"d:",d[q,R]
        x[q, R - a] += E
        #print "x:",x[q,R-a]
        RC[R - a] -= E
        #print"RC:",RC[R-a]
        INF[R] -= E
        #print"INF:",INF[R]
        if (INF[R] > 0):
            if (E == RC[R - a]):
                a = a + 1
                Step6(R, a, d, x, RC)
            else:
                if (Mstar != []):
                    Step6(R, a, d, x, RC)
                else:
                    def Step4(R, a, x, d, RC, INF):
                        AC = {}
                        E = {}
                        B = {}
                        Transfer = {}
                        for i in N:
                            if (d[i, R] <= INF[R]):
                                E[i] = min(d[i, R], RC[R - a])
                                if (E[i] == d[i, R]):
                                    AC[i] = a * h[i] * d[i, R]
                                    Transfer[i] = d[i, R]
                                elif (E[i] == RC[R - a]):
                                    AC[i] == (a * h[i] * RC[R - a]) + S[i]
                                    Transfer[i] = RC[R - a]
                            else:
                                B[i] = min(INF[R], RC[R - a])
                                if (B[i] == RC[R - 1]):
                                    AC[i] = (a * h[i] * RC[R - a]) + S[i]
                                    Transfer[i] = RC[R - a]
                                elif (B[i] == INF[R]):
                                    AC[i] = (a * h[i] * INF[R]) + S[i]
                                    Transfer[i] = INF[R]
                                if (d[i, R] < RC[R - a]):
                                    AC[i] = a * h[i] * d[i, R]
                                    Transfer[i] = d[i, R]
                        min_cost_key = min(AC, key=AC.get)
                        amt_tranfer = Transfer[min_cost_key]

                        d[q, R] -= amt_tranfer
                        x[q, R - a] += amt_tranfer
                        RC[R - a] -= amt_tranfer
                        INF[R] -= amt_tranfer
                        if (INF[R] > 0):
                            if (RC[R - a] == 0):
                                a = a + 1
                                Step6(R, a, d, x, RC)
                            elif (RC[R - 1] > 0):
                                Step4(R, a, x, d, RC, INF)

                    Step4(R, a, x, d, RC, INF)
        else:
            Step1(R,d,x)

    if (RC[R]>=0):
        #print "RC:",RC
        for t in range(2, len(H)+1):
            sum = 0
            for k in range(2, t+1):
                sum1 = 0
                for i in N:
                    sum1 += d[i,k]
               # print"SUM1:",sum1,"C:",C[k]
                sum1 = sum1 - C[k]
                sum += sum1
            B[t] = sum
        #print B

        for k in range(2, len(H)):
            if (B[k]>=0):
                Tstar = k
            else:
                Tstar = len(H)
        U = {}
        I = {}

        for t in H:
            for i in N:
                sum = 0
                for k in range(1, t+1):
                    sum += (k - 1) * d[i, k]
                I[i, t] = h[i] * sum
        #print"I:", I

        for i in N:
            for t in range(R+1,R+1):
                if(d[i,t-1]!=0 ):
                    U[i,t] = (S[i] - I[i,t])/(t*t*d[i,t])
        #print"U:", U

        for i in N:
            x[i,R] = d[i,R]

        def Step(R,U, RC, d, x):
            if (bool(U) == True):
                U_max = max(U, key=U.get)
                #print U_max[0],U_max[1]
                #print RC[R],d[U_max[0],U_max[1]]
                if(d[U_max[0],U_max[1]] <= RC[R] and U[U_max[0],U_max[1]]>0):
                    #print"in if"
                    x[U_max[0],U_max[1]-1] += d[U_max[0],U_max[1]]
                    del U[U_max[0],U_max[1]]
                    RC[R] -= d[U_max[0],U_max[1]]
                    d[U_max[0], U_max[1]] -= d[U_max[0],U_max[1]]
                    Step(R,U,RC,d, x)
                else:
                    del U[U_max[0], U_max[1]]
                    Step(R,U, RC, d, x)

            else:
                #print "R:",R,"X:",x
                R = R+1
                if(R<=len(H)):
                    Step1(R,d,x)
                else:
                    #print"STOP"
                    #print"x:",x
                    I = {}
                    t = 1
                    for i in N:
                        I[i, t] = Iin[i] + ((x[i, t] - D[i, t])*kinv[i])
                        for j in range(2, len(H)):
                            I[i, j] = I[i, j - 1] + ((x[i, j] - D[i, j])*kinv[i])
                        I[i, len(H)] = Iend[i]
                    x_list = []
                    I_list = []
                    for i in N:
                        list = []
                        list1 = []
                        for j in H:
                            if(x[i,j] >= 0):
                                list.append(x[i, j]*kinv[i])
                                list1.append(I[i, j])
                            else:
                                list.append((-1)*x[i, j]*kinv[i])
                                list1.append(I[i, j])

                        x_list.append(list)
                        I_list.append(list1)
                        # print x_list

                    df = pd.DataFrame(x_list)
                    df1 = pd.DataFrame(I_list)
                    #print df
                    #print df1

                    if (locationsFolder == 'Data_1'):
                        df.to_csv('Solution_Eisenhut_1.csv')
                        print"Solution saved to Solution_Eisenhut_1.csv"
                        df1.to_csv('Inventory_Eisenhut_1.csv')
                        print"Inventory solution saved to Inventory_Eisenhut_1.csv"
                    else:
                        df.to_csv('Solution_Eisenhut_2.csv')
                        print"Solution saved to Solution_Eisenhut_2.csv"
                        df1.to_csv('Inventory_Eisenhut_2.csv')
                        print"Inventory solution saved to Inventory_Eisenhut_2.csv"

                    sum1 = 0
                    sum2 = 0
                    for i in N:
                        for t in H:
                            sum1 += (h[i] * (I[i, t] - SS[i]))
                    print "Inventory cost:", sum1

                    for i in N:
                        for j in H:
                            if (x[i, j] != 0):
                                sum2 += S[i]

                    print"Setup Cost:", sum2
                    print"Total cost:", sum1 + sum2

        Step(R,U,RC,d,x)
    else:
        #print"Entering feedback mechanism from main"
        Step6(R,a,d,x,RC)


Step1(R,d,x)


