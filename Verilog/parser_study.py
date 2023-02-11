import os
import re

import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s:%(name)s - %(message)s")


#Pythonでカレントディレクトリをスクリプトのディレクトリに固定
os.chdir(os.path.dirname(os.path.abspath(__file__)))

KEYWORDS = {}
KEYWORDS["port_definition"] = [
    "input"
    ,"output"
    ,"inout"
]
KEYWORDS["local_definition"] = [
    "wire"
    ,"reg"
    ,"logic"
    ,"localparam"
    ,"real"
    ,"realtime"
    ,"var"
    ,"integer"
    ,"genvar"
]

KEYWORDS["module_start"] = [
    "module"
    ,"primitive"
]

KEYWORDS["module_end"] = [
    "endmodule"
    ,"endprimitive"
]


KEYWORDS["logic_start"] = [
    "assign"
    ,"always"
]

KEYWORDS["others"] = [
    "posedge"
    ,"negedge"
    ,"or"
    ,"and"
    ,"if"
    ,"else"
    ,"generate"
    ,"for"
    ,"initial"
    ,"forever"
]

KEYWORDS["begin_end"] = [ "begin", "end"]
            
class Words:
    def __init__(self,words):
        self.words = words.copy()
        self.ptr = 0

    def now(self,advance=0):
        try:
            now = self.words[self.ptr]
            self.ptr+=advance
            #logging.debug(f'now :{now}')
            return now
        except IndexError:
            self._index_err()
            return None

    def advance(self,num=1):
        self.ptr += num
        try:
            logging.debug(f'adv :{self.words[self.ptr]}')
            return self.words[self.ptr]
        except IndexError:
            self._index_err()
            return None

    def skip(self,mark):
        self.save_ptr = self.ptr
        skipped_words = []
        while(True):
            try:
                if(self.now() == mark):
                    self.ptr +=1
                    return "".join(skipped_words)
                else:
                    skipped_words.append(self.now())
                    self.ptr +=1
            except IndexError:
                print(f'[Error] makr "{mark}" was not detect from {self.save_ptr} to {self.ptr}')
                raise ValueError
    
    def check(self,mark,advance=0):
        if(not re.fullmatch(mark,self.now())):
            print(f'[Error] Expect "{mark}" but "{self.words[self.ptr]}" (ptr:{self.ptr})')
            raise ValueError
        now = self.now()
        self.ptr+=advance
        return now

    def skip_from_begin_to_end(self):
        if(self.now()=="begin"):
            depth = 1
            self.advance()
            while(True):
                if(self.now()=="begin"):
                    depth += 1
                if(self.now()=="end"):
                    depth -= 1
                self.advance()
                if(depth==0):
                    return True
        else:
            return False
                


    def _index_err(self):
        print(f'Over index (ptr:{self.ptr}, Len:{len(self.words)})')
            


class Port():
    def __init__(self,words:Words):
        self.dir = None
        self.name = None
        self.msb = 0
        self.lsb = 0
        self.value = ""
        if(words.now() in KEYWORDS["port_definition"]):
            self.dir = words.now()
            #output reg や input wire 対策
            while(words.advance() in KEYWORDS["local_definition"]):
                continue
            m = re.fullmatch(r"\[(?P<msb>[^:]+):(?P<lsb>[^\]]+)\]", words.now())
            if(m):
                self.msb = m.group("msb")
                self.lsb = m.group("lsb")
                words.advance()
            self.name = words.now(advance=1)
            matched_mark = words.check(r"[,\)]",advance=1)
            if(matched_mark==")"):
                words.check(";", advance=1)
    def dump(self):
        list = [self.dir, f'[{self.msb}:{self.lsb}]', self.name]
        print("\t".join(list))

                
class Instance:
    def __init__(self,words:Words):
        self.module_name  = None
        self.instance_name = None
        not_instance = False
        word_1st = words.now()
        try:
            word_2nd = words.words[words.ptr+1]
        except IndexError:
            return
        for word in [word_1st, word_2nd]:
            if(re.search(r"[^\w]",word)):
                not_instance = True
                break
            else:
                for  key, str_list in KEYWORDS.items():
                    if(word in str_list):
                        not_instance = True
                        break
                if(not_instance):
                    break
        if(not_instance is False):
            logging.debug(f'Instance : {word_1st} {word_2nd}')
            self.module_name   = word_1st
            self.instance_name = word_2nd
            words.advance(num=2)
        return

    def exist(self):
        if(self.module_name is None):
            return False
        else:
            return True



class Local_base():
    def __init__(self, type, msb, lsb, value=""):
        self.type = type
        self.msb  = msb
        self.lsb  = lsb
        self.value = value

class Local(Local_base):
    def __init__(self, name, type, msb,lsb,value):
        super().__init__(type=type, msb=msb, lsb=lsb,value=value)
        self.name = name

class Locals(Local_base):
    def __init__(self,words:Words,type):
        self.names = []
        super().__init__(type=type, msb=0, lsb=0)
        if(words.now() == type):
            self.dir = words.now()
            #output reg や input wire 対策
            while(words.advance() in KEYWORDS["local_definition"]):
                continue
            m = re.fullmatch(r"\[(?P<msb>[^:]+):(?P<lsb>[^\]]+)\]", words.now())
            if(m):
                self.msb = m.group("msb")
                self.lsb = m.group("lsb")
                words.advance()
            self.names.append(words.now(advance=1))
            while(True):
                matched_mark = words.check(r"[,;=]",advance=0)
                if(matched_mark==";"):
                    break
                elif(matched_mark=="="):
                    words.advance()
                    self.value = words.skip(mark=";")
                    break
                else:
                    self.names.append(words.advance())
    def expand(self):
        #name_list を展開
        locals = []
        for name in self.names:
            locals.append(Local(name=name, type=self.type, msb=self.msb, lsb=self.lsb, value=self.value))
        return locals

            

            


class Module:
    SIG_TYPE_LIST= ["ports", "regs", "wires", "genvars", "localparams", "parameters"]
    def __init__(self):
        self.module = None
        self.signals_dict = {}
        for sig_type in self.SIG_TYPE_LIST:
            self.signals_dict[sig_type]        = []
        #self.signals["instances"]    = []
        self.instances               = []

    def dump(self):
        for type in self.SIG_TYPE_LIST:
            for signal in self.signals_dict[type]:
                list = []
                if(type=="ports"):
                    list.append(signal.dir)
                else:
                    list.append(signal.type)
                list.append(str(signal.msb))
                list.append(str(signal.lsb))
                list.append(signal.name)
                list.append(signal.value)
                print("\t".join(list))


            




def main():
    dir=r"C:\Work\GitLocals\development\core_usb_host\src_v"

    for filename in os.listdir(dir):
        if(re.fullmatch(r"\w+\.v", filename)):
            filename="usbh_sie.v"
            with open(os.path.join("files", dir + "/" + filename), 'r') as f:
                print(f'Reading...{filename}')
                words_str = ""
                for line in f:
                    line = re.sub("//.*","", line)
                    line = re.sub("\n"," ", line)
                    if(line==""):
                        continue
                    words_str += line
                
                words_str = re.sub(r"([^\w])", r" \1 ", words_str)
                #words_str = re.sub(r"\s*([\+\-\*/%^\&\|\'\?])\s*",r"\1",words_str)
                words_str = re.sub(r"\s*([\(\)])\s*",r" \1 ",words_str)

                words_str = re.sub(r"\[\s*(\d+)\s*:\s*(\d+)\s*\]", r"[\1:\2]", words_str)
                words_str = re.sub(r"\[\s*(\d+)\s*\]", r"[\1]", words_str)

                #[ ] 内の空白を削除
                p = re.compile(r'\[([^\]]+)\]')
                m_list = p.finditer(words_str)
                for m in m_list:
                    words_str = re.sub(r"\[" + m.group(1) + r"\]", f'[{m.group(1).replace(" ","")}]',words_str)

                words_str = re.sub(r"([#])\s*",r"\1",words_str) # 一部の記号は後ろの単語にくっつける。


                _ = re.split(r"\s+",words_str)
                _ = [a for a in _ if a != '']
                words = Words(_)

                module = Module()
                if(words.now() in KEYWORDS["module_start"]):
                    module.name = words.advance()
                    if(words.advance()=="#("):
                        words.skip(")")
                    words.check(r"\(",advance=1)
                    while(True):
                        port = Port(words)
                        if(port.name is not None):
                            module.signals_dict["ports"].append(port)
                        else:
                            break

                    while(True):
                        any_detected = False
                        for type in ["reg", "wire", "genvar", "localparam", "parameter"]:
                            locals = Locals(words, type=type).expand()
                            if(len(locals)!=0):
                                any_detected = True
                                module.signals_dict[type+"s"].extend(locals)
                                break
                        if(any_detected):
                            continue
                        skipped = words.skip_from_begin_to_end()
                        if(skipped):
                            continue
                        instance = Instance(words)
                        if(instance.exist()):
                            module.instances.append(instance)
                            continue
                        if(words.now() in KEYWORDS["module_end"]):
                            break
                        words.advance()

                pass

                

                
                    


                #
                #print('"\n"'.join(words.words))
                module.dump()
            break
    pass


if __name__ == "__main__":
    main()
