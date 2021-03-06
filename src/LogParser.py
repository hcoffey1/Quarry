import matplotlib.pyplot as plt
import sys


def drawNumQubitWallClockGraph(data):

    ax = plt.axes()

    for key in data.keys():
        ax.scatter(data[key]['num_qubits'], data[key]['wall_clock'], label=key)

    #ax.set_ylim(0, 100)
    ax.legend()
    ax.set_xlabel("Circuit Qubit Count")
    ax.set_ylabel("Wall Clock Time")
    ax.set_title("Wall Clock Time vs. Circuit Qubit Count : n = 10")
    plt.show()


def drawNumQubitPeakRSSGraph(data):

    ax = plt.axes()

    for key in data.keys():
        ax.scatter(data[key]['num_qubits'], data[key]['peak_rss'], label=key)

    ax.legend()
    ax.set_xlabel("Circuit Qubit Count")
    ax.set_ylabel("Peak RSS (KB)")
    ax.set_title("Peak RSS vs. Circuit Qubit Count : n = 10")
    plt.show()

def drawCircuitSizeWallClockGraph(data):

    ax = plt.axes()

    for key in data.keys():
        ax.scatter(data[key]['circuit_size'], data[key]['wall_clock'], label=key)

    #ax.set_ylim(0, 100)
    ax.legend()
    ax.set_xlabel("Circuit Size")
    ax.set_ylabel("Wall Clock Time")
    ax.set_title("Wall Clock Time vs. Circuit Size : n = 10")
    plt.show()


def drawCircuitSizePeakRSSGraph(data):

    ax = plt.axes()

    for key in data.keys():
        ax.scatter(data[key]['circuit_size'], data[key]['peak_rss'], label=key)

    ax.legend()
    ax.set_xlabel("Circuit Size")
    ax.set_ylabel("Peak RSS (KB)")
    ax.set_title("Peak RSS vs. Circuit Size : n = 10")
    plt.show()


def get_sec(time_str):
    """Get seconds from time."""
    if len(time_str.split(':')) == 3:
        h, m, s = time_str.split(':')
        return int(h) * 3600 + int(m) * 60 + float(s)
    else:
        m, s = time_str.split(':')
        return int(m) * 60 + float(s)


def cleanLog(file):
    with open(file) as f:
        lines = f.readlines()

    for l in lines:
        if "QUARRY LOG HEADER" in l:
            print(l, end='')
            continue
        elif "Mode" in l:
            print(l, end='')
            continue

        elif 'CircuitSize' in l:
            print(l, end='')
            continue

        elif 'NumQubits' in l:
            print(l, end='')
            continue

        elif 'User time' in l:
            print(l, end='')
            continue

        elif 'System time' in l:
            print(l, end='')
            continue

        elif 'wall clock' in l:
            print(l, end='')
            continue

        elif 'Maximum resident set size' in l:
            print(l, end='')
            continue

    exit(0)


def main():

    #cleanLog(sys.argv[1])

    files = sys.argv[1:]

    data = {}
    for file in files:
        with open(file) as f:
            lines = f.readlines()

        for l in lines:
            if "QUARRY LOG HEADER" in l:
                continue
            elif "Mode" in l:
                mode = (l.split(' ')[1]).strip()
                if mode not in data:
                    data[mode] = {}
                    data[mode]['num_qubits'] = []
                    data[mode]['user_time'] = []
                    data[mode]['system_time'] = []
                    data[mode]['wall_clock'] = []
                    data[mode]['peak_rss'] = []
                    data[mode]['circuit_size'] = []
                continue

            elif 'CircuitSize' in l:
                circuitSize = int(l.split(' ')[1])
                data[mode]['circuit_size'].append(circuitSize)
                continue

            elif 'NumQubits' in l:
                numQubits = int(l.split(' ')[1])
                data[mode]['num_qubits'].append(numQubits)
                continue

            elif 'User time' in l:
                utime = float(l.split(' ')[3])
                data[mode]['user_time'].append(utime)
                continue

            elif 'System time' in l:
                systime = float(l.split(' ')[3])
                data[mode]['system_time'].append(systime)
                continue

            elif 'wall clock' in l:
                wctime = get_sec(l.split(' ')[7])
                data[mode]['wall_clock'].append(wctime)
                continue

            elif 'Maximum resident set size' in l:
                prss = int(l.split(' ')[5])
                data[mode]['peak_rss'].append(prss)
                continue

    drawNumQubitWallClockGraph(data)
    drawNumQubitPeakRSSGraph(data)
    drawCircuitSizeWallClockGraph(data)
    drawCircuitSizePeakRSSGraph(data)


if __name__ == "__main__":
    main()
