import serial
import sys
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

assert len(sys.argv)==3

log_file = open(sys.argv[2],"a+")

ser = serial.Serial(sys.argv[1], 115200)
ser.flushInput()

n_plot = 0

print "Serial opened : " + str(sys.argv[1])

def read(display=True):
	line = ser.readline().rstrip()
	log_file.write(line)
	if(display):
		print('\t' + line)
	return line

def read_int(i):
	return int(read().split('\t')[i])

def decode_histo():
	units = read().split('\t')[1]
	bounds = list(map(int, read().split('\t')[1:]))
	nb_values = read_int(1)
	histo = list(map(int, read(False).split('\t')[1:]))
	avg = read_int(1)
	recv = read_int(1)
	sent = read_int(1)

	overtimed = histo[-1]
	histo = histo[:-1]
	nb_values = nb_values-1

	bounds = list(map(lambda x : x/1000., bounds))
	x_axis = [(x+0.5)*(bounds[1]-bounds[0])/nb_values+bounds[0] for x in range(nb_values)]
	

	histo_cumulate = [0 for i in range(len(histo))]
	histo_cumulate[0] = histo[0]
	for i in range(1, len(histo)):
		histo_cumulate[i] = histo_cumulate[i-1] + histo[i]

	histo = list(map(lambda x:x*100./sent, histo))
	histo_cumulate = list(map(lambda x: x*100./sent, histo_cumulate))

	plt.ion()

	fig = plt.figure(n_plot)
	ax1 = fig.add_subplot(111)
	ax2 = ax1.twinx()

	plt.title('(' + str(n_plot) + ')' + 'Overall receive ' + str(recv*100./sent) + '% ; Sent : ' + str(sent) + ' ; Longer than ' + str(bounds[1]) + units + ' : ' + str(overtimed))

	ax1.plot(x_axis, histo, color='tab:blue')
	ax1.set_ylabel('% packets', color='tab:blue')
	ax1.tick_params(axis='y', labelcolor='tab:blue')
	ax1.set_yticks([i*0.5  for i in range(int(max(histo)+1)*2)])

	ax1.set_xticks([i*(bounds[1]-bounds[0])/10.+bounds[0]  for i in range(11)])


	ax2.plot(x_axis, histo_cumulate, color='tab:red')
	ax2.set_ylabel('% packets', color='tab:red')
	ax2.tick_params(axis='y', labelcolor='tab:red')
	ax2.set_yticks([i*10  for i in range(11)])

	ax2.plot([x_axis[0], x_axis[-1]], [95, 95], color='tab:orange')

	ax1.set_xlabel('Delay ( 1000' + units + ') ; Avg = ' + str(avg) + units)

	fig.tight_layout()
	fig.legend(["histogram", "cumulated", "95%", "hello"])
	plt.grid()

	plt.plot()


while n_plot < 3:
	line = read(False)
	if("----------" in line):
		n_plot+=1
		print("\033[31mHisto " + str(n_plot) + " \033[31mreceived\033[0m")
		decode_histo()
	else:
		print("\033[34mLine not recognized \033[0m >> \033[33m" + line + "\033[0m")
	
raw_input("Press [enter] to continue.")