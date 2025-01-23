import pandas
from os.path import exists
import sys

path = sys.argv[1]

fx = []
f = open('{}/pareto_front.out'.format(path), 'w')
f2 = open('{}/pareto_front_uuid.out'.format(path), 'w')
f3 = open('{}/plot.out'.format(path), 'w')

for i in range(0,100):
    cost_output_file = '{}/{}_output_t.csv'.format(path, i)
    load_output_file = '{}/{}_reportloads.csv'.format(path, i)

    file_exists = exists(cost_output_file)
    
    if file_exists:
        csvFile = pandas.read_csv(cost_output_file)
        cost = csvFile['Cost'].sum()
        loadFile = pandas.read_csv(load_output_file)
        load = loadFile['NLoadEos'].sum()
        fx.append([cost,load])

        
for i in range(len(fx)):
   f.write('{} {}\n'.format(fx[i][0], fx[i][1])) 
   f2.write('{} {}\n'.format(fx[i][0], fx[i][1])) 
   f3.write('{} {}\n'.format(fx[i][0], fx[i][1])) 

f.close()
f2.close()
f3.close()

# displaying the contents of the CSV file

