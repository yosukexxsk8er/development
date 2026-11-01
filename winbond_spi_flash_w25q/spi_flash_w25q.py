from pyftdi.spi import SpiController
import time


class SpiFlash(SpiController):
    COMMAND = {}
    COMMAND[0x06] =  { "name": "WRITE_ENABLE"              , "need_addr": False}
    COMMAND[0x50] =  { "name": "VOLATILE_SR_WRITE_ENABLE"  , "need_addr": False}
    COMMAND[0x04] =  { "name": "WRITE_DISABLE"             , "need_addr": False}
    COMMAND[0x05] =  { "name": "READ_STATUS_REGISTER1"     , "need_addr": False}
    COMMAND[0x35] =  { "name": "READ_STATUS_REGISTER2"     , "need_addr": False}
    COMMAND[0x01] =  { "name": "WRITE_STATUS_REGISTER"     , "need_addr": False}
    COMMAND[0x02] =  { "name": "PAGE_PROGRAM"              , "need_addr": True }
    COMMAND[0x20] =  { "name": "SECTOR_ERASE"              , "need_addr": True }
    COMMAND[0x52] =  { "name": "BLOCK_ERASE_32KB"          , "need_addr": True }
    COMMAND[0xD8] =  { "name": "BLOCK_ERASE"               , "need_addr": True }
    COMMAND[0x60] =  { "name": "CHIP_ERASE"                , "need_addr": False}
    COMMAND[0xC7] =  { "name": "CHIP_ERASE"                , "need_addr": False}
    COMMAND[0x75] =  { "name": "ERASE_OR_PROGRAM_SUSPEND"  , "need_addr": False}
    COMMAND[0x7A] =  { "name": "ERASE_OR_PROGRAM_RESUME"   , "need_addr": False}
    COMMAND[0xB9] =  { "name": "POWER_DOWN"                , "need_addr": False}
    COMMAND[0x03] =  { "name": "READ_DATA"                 , "need_addr": True }
    COMMAND[0x0B] =  { "name": "FAST_READ"                 , "need_addr": True }
    COMMAND[0xAB] =  { "name": "RELEASE_POWERDOWN_OR_ID"   , "need_addr": False}
    COMMAND[0x90] =  { "name": "MANUFACTURERORDEVICE_ID"   , "need_addr": False}
    COMMAND[0x9F] =  { "name": "JEDEC_ID"                  , "need_addr": False}
    COMMAND[0x4B] =  { "name": "READ_UNIQUE_ID"            , "need_addr": False}
    COMMAND[0x5A] =  { "name": "READ_SFDP_REGISTER"        , "need_addr": True }
    COMMAND[0x44] =  { "name": "ERASE_SECURITY_REGISTERS"  , "need_addr": True }
    COMMAND[0x42] =  { "name": "PROGRAM_SECURITY_REGISTERS", "need_addr": True }
    COMMAND[0x48] =  { "name": "READ_SECURITY_REGISTERS"   , "need_addr": True }
    COMMAND[0x38] =  { "name": "ENABLE_QPI"                , "need_addr": False}
    COMMAND[0x66] =  { "name": "ENABLE_RESET"              , "need_addr": False}
    COMMAND[0x99] =  { "name": "RESET"                     , "need_addr": False}

    for key, value in COMMAND.items():
        exec(f'{value.get("name")}={key}')
    
    def __init__(self,cs=0, freq=1000000, mode=0, page_size=256, sector_size=16, block_size=16,url="ftdi://ftdi:232h/1", addr_len=3):
        """_summary_

        Args:
            cs (int, optional): _description_. Defaults to 0.
            freq (int, optional): _description_. Defaults to 1000000.
            mode (int, optional): _description_. Defaults to 0.
            page_size (int, optional): Unit is byte. Defaults to 256.
            sector_size (int, optional): unit is page. Defaults to 16.
            block_size (int, optional): unit is sector. Defaults to 16.
            url (str, optional): _description_. Defaults to "ftdi://ftdi:232h/1".
            addr_len (int, optional): _description_. Defaults to 3.
        """
        self.ctrl = SpiController()
        self.ctrl.configure(url)
        self.spi = self.ctrl.get_port(cs=cs, mode=mode)
        self.spi.set_frequency(freq)
        self.page_size=page_size
        self.sector_size=sector_size
        self.block_size=block_size
        self.addr_len=addr_len

    def _list_int2str(self, list, with_command=False, prefix=""):
        """convert list[int] --> list[str(hex)].

        Args:
            list (_type_): _description_
            with_command (bool, optional): _description_. Defaults to False.
            prefix (str, optional): _description_. Defaults to "".

        Raises:
            KeyError: _description_
        """
        if(with_command):
            try:
                cmd_name = self.COMMAND[list[0]].get("name")
            except KeyError as e:
                print(f'The value "{list[0]}" is illegal as command')
                raise KeyError
        msg = []
        for i, value in enumerate(list):
            if(with_command and i==0):
                continue
            msg.append(f'{list[i]:02x}')
        return msg

    def _write(self,wdat):
        print(self._dec_spi_write_data(wdat))
        self.spi.write(wdat)


    def _dec_spi_write_data(self,wdat):
        msg = []
        addr = []
        for i, value in enumerate(wdat):
            if(i==0):
                try:
                    cmd_name = self.COMMAND[wdat[0]].get("name")
                    continue
                except KeyError as e:
                    print(f'The value "{wdat[0]}" is illegal as command')
                    raise KeyError
            elif(1<=i<=(self.addr_len) and self.COMMAND[wdat[0]].get("need_addr")):
                addr.append(wdat[i])
                if(i==(self.addr_len)):
                    msg.append(f'Address: 0x{"".join(self._list_int2str(addr))}')
            else:
                msg.append(f'0x{wdat[i]:02x}')
        return f'{cmd_name:30s} : {", ".join(msg)}'

    def _exchange(self, wdat, read_len=1, display=True):
        print(self._dec_spi_write_data(wdat),end="")
        rdat = self.spi.exchange(wdat, read_len)
        rdat_str = []
        for dat in rdat:
            rdat_str.append(f'0x{dat:02x}')
        print(f': {", ".join(rdat_str)}')
        return rdat

    def write_enable(self):
        self._write([self.WRITE_ENABLE])
    
    def read_data(self,addr=0,read_len=1,display=True):
        wdat = []
        wdat.append(self.READ_DATA)
        wdat.extend(self._split(addr, num=self.addr_len))
        rdat = self._exchange(wdat,read_len,display=display)
        return rdat

    def read_status1(self,display=True):
        rdat = self._exchange([self.READ_STATUS_REGISTER1],1,display=display)
        return rdat

    def read_status2(self,display=True):
        rdat = self._exchange([self.READ_STATUS_REGISTER2],1,display=display)
        return rdat

    def jedec_id(self):
        rdat = self._exchange([self.JEDEC_ID],1)
        return rdat

    def sector_erase(self,addr):
        wdat = []
        wdat.append(self.SECTOR_ERASE)
        wdat.extend(self._split(addr, num=self.addr_len))
        self._write(wdat)

    def page_program(self,addr, wdat:list[int]=[]):
        if(len(wdat)!=self.page_size):
            print(f'byte num of  wdat (len(wdat) byte) is not {self.page_size}[byte]')
            raise ValueError
        wdat_spi = []
        wdat_spi.append(self.PAGE_PROGRAM)
        wdat_spi.extend(self._split(addr,num=self.addr_len))
        wdat_spi.extend(wdat)
        self._write(wdat_spi)

    def polling_busy_0(self):
        while True:
            rdat = self.read_status1()
            busy = rdat[0] & 0x01
            if(busy==0):
                break
        



    def _split(self, value, num=1):
        list = []
        for i in reversed(range(num)):
            list.append((value & (0xFF << (i*8))) >> (i*8))
        return list


def main():
    import random
    spi = SpiFlash()
    spi.write_enable()
    spi.sector_erase(addr=0x00)
    spi.polling_busy_0()
    spi.write_enable()
    wdat = []
    wdat_str = []
    for i in range(256):
        val = random.randint(0, 255)
        wdat.append(val)
        wdat_str.append(f'0x{val:02x}')
    #print(f'wdat_str {", ".join(wdat_str)}')
    spi.page_program(addr=0x00,wdat=wdat)
    spi.polling_busy_0()
    spi.read_data(addr=0x00,read_len=256)
    pass

def test():
    spi = SpiFlash()
    # send 1 bytes, then receive 1 bytes
    pass
    #Read
    out = spi.read_data(0x000000, 4)
    out = spi.read_status1()
    out = spi.read_status2()
    #Read JID
    out = spi.exchange([0x9F], 3)
    # WriteEnable
    spi.write([0x06])
    out = spi.exchange([0x05], 1)
    out = spi.exchange([0x35], 1)
    # Sector Erase(4kB)
    spi.write([0x20, 0x00, 0x00, 0x00])
    out = spi.exchange([0x05], 1)
    out = spi.exchange([0x35], 1)
    # WriteEnable
    spi.write([0x06])
    out = spi.exchange([0x05], 1)
    out = spi.exchange([0x35], 1)
    #Program
    spi.write([0x02, 0x00, 0x00, 0x00, 0x01, 0x02, 0x03, 0xFF])
    out = spi.exchange([0x05], 1)
    out = spi.exchange([0x35], 1)
    #Read
    out  = spi.exchange([0x03, 0x00, 0x00, 0x00], 4)
    out = spi.exchange([0x05], 1)
    out = spi.exchange([0x35], 1)
    # send 2 bytes, then receive 4 bytes, manage the transaction
    # out = spi.exchange([0x12, 0x34], 2, True, False)
    # out.extend(spi.exchange([], 2, False, True))
    pass



if __name__ == "__main__":
    main()
