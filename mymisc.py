
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

def main():
    print(i2h(10,4))
    print(i2b(10,4))
    print(h2i("0xB"))
    print(b2i("0b1100"))

if __name__ == "__main__":
    main()




