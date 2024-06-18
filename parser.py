from gnss_tec import rnx

import sys

filename = sys.argv[1]

with open(filename) as obs_file:
    reader = rnx(obs_file)
    a = 0
    for tec in reader:
        print(
            '{} {}: {} {}'.format(
                tec.timestamp,
                tec.satellite,
                tec.phase_tec,
                tec.p_range_tec,
            )
        )
        a += 1
        if a == 5:
            break
