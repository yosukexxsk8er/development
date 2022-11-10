
def i2h(val, digit=1):
    """ return a string as Hex generated from "val" as integer

    Args:
        val (int): value
        digit (int, optional): number of digit. Defaults to 1.

    Returns:
        string: a strings as Hex
    """
    return "0x" + format(val, f"0{digit}X")

def i2b(val, digit=1):
    """ return a string as Bin generated from "val" as integer

    Args:
        val (int): value
        digit (int, optional): number of digit. Defaults to 1.

    Returns:
        string: a strings as Bin
    """
    return format(val, f"0{digit}b") + "b"

def h2i(str, digit=1):
    """ return value as integer genretaed from a string as Hex 

    Args:
        str (string): a string as hex (e.g. 0xF)
        digit (int, optional): number of digit . Defaults to 1.

    Returns:
        int : value generated from a string as Hex
    """
    return int(str,16) 


def b2i(str, digit=1):
    """ return value as integer genretaed from a string as Bin 

    Args:
        str (string): a string as Bin (e.g. 0b0101)
        digit (int, optional): number of digit . Defaults to 1.

    Returns:
        int : value generated from a string as Bin
    """
    return int(str,2) 

def s2i(str):
    for x in [10,2,8,16]:
        try:
            return int(str,x)
        except ValueError:
            continue
    return None

def i2s(int:int,radix:int,digit:int=1)->str:
    dict = {2:("b","0b"),  8:("o", "0o"),  10:("d", ""), 16:("X","0x")}
    try:
        dec, pre = dict[radix]
    except KeyError:
        print(f"Error Illegal radix(radix)")
        return
    fmt=f"0{digit}{dec}"
    return pre + format(int,fmt)
        
            

def main():
    if(False):
        print(i2h(10,4))
        print(i2b(10,4))
        print(h2i("0xB"))
        print(b2i("0b1100"))
    if(False):
        print(s2i("0xF"))
        print(s2i("0b1111"))
        print(s2i("0o17"))
        print(s2i("15"))
        print(s2i("0b1"))
        print(s2i("0o1"))
        print(s2i("1"))
        print(s2i("0x1"))
    if(True):
        print(i2s(10,16,digit=3))
        print(i2s(10,2,digit=8))
        print(i2s(10,8, digit=3))
        print(i2s(10,10, digit=0))
        print(i2s(10,3, digit=0))

if __name__ == "__main__":
    main()




