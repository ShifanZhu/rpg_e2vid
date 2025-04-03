#!/usr/bin/python

import sys, getopt
from dv import AedatFile
import numpy as np

class Struct:
    pass

def main(argv):
    inputfile = ''
    outputfile = ''
    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["ifile=", "ofile="])
    except getopt.GetoptError:
        print('aedat4totxt.py -i <inputfile> -o <outputfile>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('aedat4totxt.py -i <inputfile> -o <outputfile>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
    print('Input file is "', inputfile)
    print('Output file is "', outputfile)
    
    # Define output struct
    out = Struct()
    out.data = Struct()
    out.data.polarity = Struct()
    out.data.frame = Struct()
    out.data.imu6 = Struct()

    # Events
    out.data.polarity.polarity = []
    out.data.polarity.timeStamp = []
    out.data.polarity.x = []
    out.data.polarity.y = []

    # Frames
    out.data.frame.samples = []
    out.data.frame.position = []
    out.data.frame.sizeAll = []
    out.data.frame.timeStamp = []
    out.data.frame.frameStart = []
    out.data.frame.frameEnd = []
    out.data.frame.expStart = []
    out.data.frame.expEnd = []

    # IMU
    out.data.imu6.accelX = []
    out.data.imu6.accelY = []
    out.data.imu6.accelZ = []
    out.data.imu6.gyroX = []
    out.data.imu6.gyroY = []
    out.data.imu6.gyroZ = []
    out.data.imu6.temperature = []
    out.data.imu6.timeStamp = []

    with AedatFile(inputfile) as f:
        # Check for the presence of each stream and process if available
        print("f['events']: ", f['events'].size[1], f['events'].size[0])

        if 'events' in f.names:
            # Print the first few events for debugging
            print("First few events:")
            for i, e in enumerate(f['events']):
                if i < 10:  # Adjust the number of events to print for debugging
                    print(f"Event {i}: timestamp={e.timestamp}, x={e.x}, y={e.y}, polarity={int(e.polarity)}")
                else:
                    break

            # Loop through the "events" stream
            for e in f['events']:
                out.data.polarity.timeStamp.append(e.timestamp)
                out.data.polarity.polarity.append(int(e.polarity))  # Convert boolean to int (0 or 1)
                out.data.polarity.x.append(e.x)
                out.data.polarity.y.append(e.y)
            print("finish reading events")

        if 'frames' in f.names:
            # Loop through the "frames" stream
            for frame in f['frames']:
                try:
                    out.data.frame.samples.append(frame.image)
                    out.data.frame.position.append(frame.position)
                    out.data.frame.sizeAll.append(frame.size)
                    out.data.frame.timeStamp.append(frame.timestamp)
                    out.data.frame.frameStart.append(frame.timestamp_start_of_frame)
                    out.data.frame.frameEnd.append(frame.timestamp_end_of_frame)
                    out.data.frame.expStart.append(frame.timestamp_start_of_exposure)
                    out.data.frame.expEnd.append(frame.timestamp_end_of_exposure)
                except RuntimeError as e:
                    print(f"Skipping corrupted frame data: {e}")
        print("finish reading frames")

        if 'imu' in f.names:
            # Loop through the "imu" stream
            for i in f['imu']:
                a = i.accelerometer
                g = i.gyroscope
                m = i.magnetometer
                out.data.imu6.accelX.append(a[0])
                out.data.imu6.accelY.append(a[1])
                out.data.imu6.accelZ.append(a[2])
                out.data.imu6.gyroX.append(g[0])
                out.data.imu6.gyroY.append(g[1])
                out.data.imu6.gyroZ.append(g[2])
                out.data.imu6.temperature.append(i.temperature)
                out.data.imu6.timeStamp.append(i.timestamp)
        print("finish reading imu data")

    # Add counts
    out.data.polarity.numEvents = len(out.data.polarity.x)
    out.data.imu6.numEvents = len(out.data.imu6.accelX)

    # Save data to text file
    with open(outputfile, 'w') as f:
        if out.data.polarity.numEvents > 0:
            # f.write('{} {}\n'.format(f['events'].size[1], f['events'].size[0]))
            # f.write('numEvents: {}\n'.format(out.data.polarity.numEvents))
            for i in range(out.data.polarity.numEvents):
                f.write('{:.6f} {} {} {}\n'.format(
                    out.data.polarity.timeStamp[i] / 1e6,
                    out.data.polarity.x[i],
                    out.data.polarity.y[i],
                    out.data.polarity.polarity[i]
                ))

        if len(out.data.frame.samples) > 0:
            f.write('\nFrame Data:\n')
            for i in range(len(out.data.frame.samples)):
                f.write('Sample: {}, Position: {}, Size: {}, Timestamp: {}, FrameStart: {}, FrameEnd: {}, ExpStart: {}, ExpEnd: {}\n'.format(
                    out.data.frame.samples[i],
                    out.data.frame.position[i],
                    out.data.frame.sizeAll[i],
                    out.data.frame.timeStamp[i],
                    out.data.frame.frameStart[i],
                    out.data.frame.frameEnd[i],
                    out.data.frame.expStart[i],
                    out.data.frame.expEnd[i]
                ))

        if out.data.imu6.numEvents > 0:
            f.write('\nIMU Data:\n')
            for i in range(out.data.imu6.numEvents):
                f.write('Timestamp: {}, AccelX: {}, AccelY: {}, AccelZ: {}, GyroX: {}, GyroY: {}, GyroZ: {}, Temperature: {}\n'.format(
                    out.data.imu6.timeStamp[i],
                    out.data.imu6.accelX[i],
                    out.data.imu6.accelY[i],
                    out.data.imu6.accelZ[i],
                    out.data.imu6.gyroX[i],
                    out.data.imu6.gyroY[i],
                    out.data.imu6.gyroZ[i],
                    out.data.imu6.temperature[i]
                ))

if __name__ == "__main__":
   main(sys.argv[1:])
