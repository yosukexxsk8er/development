import mymisc as rt
import time

def pickup(org:int, range:list[int], name="")->int:
    msb=range[0]
    lsb=range[1]
    width = msb - lsb
    byte  = int((width-1)/8) + 1
    mask = ((2**(msb-lsb+1)) -1 ) << lsb
    mod = (org & mask)  >> lsb
    print(f"{name}[{msb}:{lsb}] = {rt.i2h(mod,byte)}")
    return mod

def polling(exp:int, range:list[int]=[0,0], timeout:int=3, interval:float=10)->bool:
    test = [0b0001, 0b0010, 0b0101, 0b1100, 0b1111]
    loop = 0
    for x in test:
        x = pickup(x,range=range)
        if(x==exp):
            print(f"Detect(elapsed time={loop*interval}, (loop={loop})")
            return True
        elif(loop==timeout):
            print(f"Timeout:{interval*loop}[sec], Loop={loop}, x={x}")
            return False
        else:
            loop+=1
            time.sleep(interval)
            print(f"loop={loop}, x={x}")
    print("Illegal")
        
            




def main():
    pickup(0xA,[2,1], name="STAT")
    polling(0b11,range=[3,2],timeout=10, interval=0.5)

if __name__ == "__main__":
    main()




