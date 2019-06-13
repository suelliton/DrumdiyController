import cython


def read_serial(ser):     
    if ser.isOpen():
        rxData = ser.read(1)
        if len(rxData) <= 0:
            return  153,0,0      
        cmd = rxData[0]
        rxData = ser.read(2)
        note = rxData[0]
        vel = rxData[1]        
        return cmd,note,vel
    return 153,0,0                    

 