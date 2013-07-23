import numpy as np
from numpy.testing.utils import assert_allclose, assert_equal

from brian2 import *

# We can only test C++ if weave is availabe
try:
    import scipy.weave
    languages = ['numpy', 'weave']
except ImportError:
    # Can't test C++
    languages = ['numpy']


def test_spike_monitor():
    language_before = brian_prefs.codegen.target
    for language in languages:
        brian_prefs.codegen.target = language
        defaultclock.t = 0*second
        G = NeuronGroup(2, '''dv/dt = rate : 1
                              rate: Hz''', threshold='v>1', reset='v=0')
        # We don't use 100 and 1000Hz, because then the membrane potential would
        # be exactly at 1 after 10 resp. 100 timesteps. Due to floating point
        # issues this will not be exact,
        G.rate = [101, 1001] * Hz

        mon = SpikeMonitor(G)
        net = Network(G, mon)
        net.run(10*ms)

        assert_allclose(mon.t[mon.i == 0], [9.9]*ms)
        assert_allclose(mon.t[mon.i == 1], np.arange(10)*ms + 0.9*ms)
        assert_equal(mon.count, np.array([1, 10]))

    brian_prefs.codegen.target = language_before


if __name__ == '__main__':
    test_spike_monitor()

