import mymisc as rt
import time
import datetime


class Exec_sample:
    def __init__(self):
        pass
    def exec(self,s:str):
        print(s)
        s = s.replace("$", "self.")
        exec(s)

    def dump(self):
        #print(vars(self))
        print(vars(self))


def set_round_time()->datetime:
    """return time replaced min and sec as zero.

    Returns:
        datetime: current time replaced min and sec as zero.
    """
    dt = datetime.datetime.today()
    dt = dt.replace(minute=0, second=0, microsecond=0)
    return dt

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
    if(False):
        pickup(0xA,[2,1], name="STAT")
        polling(0b11,range=[3,2],timeout=10, interval=0.5)

    if(False):
        hoge= Exec_sample()
        hoge.exec("$a=100")
        hoge.exec("$b=200")
        hoge.exec("$c = $a + $b")
        hoge.exec("$a=$a*2")
        hoge.dump()

    if(True):
        print(set_round_time())


if __name__ == "__main__":
    main()



