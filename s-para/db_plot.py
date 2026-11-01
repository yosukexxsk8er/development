import math
import cProfile
#import skrf as rf
#from matplotlib import pyplot as plt # for advanced smith chart only
#from skrf import Network

#a=rf.Network("./s-para-files/tpx205950mt-7010a4.s4p")
#a.plot_s_db()

#ring_slot = Network('./s-para-files/tpx205950mt-7010a4.s4p')
#ring_slot = Network('./s-para-files/dea070787lt-4002a1.s2p')
#ring_slot.plot_s_smith()



import skrf as rf
from skrf import Network
import matplotlib.pyplot as plt

#line = Network('./s-para-files/dea070787lt-4002a1.s2p')
#line = Network('./s-para-files/tpx205950mt-7010a4.s4p')
line = Network('./s-para-files/NRC_reference_package_PCIE5_08_01_2019.s24p')
print(line)
#line.plot_s_smith()
line.plot_s_db(m=4, n=5)
line.plot_s_db(m=4, n=4)
line.plot_s_db(m=6, n=7)
plt.plot([16 * 1e9, 16*1e9],[-40, 0], label="16GHz")
plt.grid()
plt.savefig("AAAA_S56_S55.png")
#plt.xscale("log")
#plt.xlim([1,  100 * 1000 * 1000 * 1000])
plt.xlim([0,  16 * 1e9])
pass
plt.show()
plt.savefig("AAAA_S56.png")

#line.plot_s_db()
#plt.show()
#plt.savefig("AAAA_all.png")


pass
