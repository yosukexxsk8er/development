import os
import re

import logging
import copy

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s:%(name)s - %(message)s")


#Pythonでカレントディレクトリをスクリプトのディレクトリに固定
os.chdir(os.path.dirname(os.path.abspath(__file__)))

class Keywords:
    DICT = {}
    DICT["port_definition"] = [
        "input"
        ,"output"
        ,"inout"
    ]
    DICT["local_definition"] = [
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

    DICT["module_start"] = [
        "module"
        ,"primitive"
    ]

    DICT["module_end"] = [
        "endmodule"
        ,"endprimitive"
    ]


    DICT["logic_start"] = [
        "assign"
        ,"always"
    ]

    DICT["others"] = [
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
    DICT["begin_end"] = [ "begin", "end"]

    @classmethod
    def is_no_keyword(cls,word):
        for  key, str_list in cls.DICT.items():
            if(word in str_list):
                return False
        return True



            
class Words:
    def __init__(self,words):
        # /* ~~ */ を削除
        self.words = []
        i=0
        while(i<len(words)):
            if(words[i]=="/*"):
                i+=1
                while(i<=len(words)):
                    if(words[i]=="*/"):
                        i+=1
                        break
                    else:
                        i+=1
            else:
                self.words.append(words[i])
                i+=1
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
            #logging.debug(f'adv :{self.words[self.ptr]}')
            return self.words[self.ptr]
        except IndexError:
            self._index_err()
            return None

    def skip(self,mark):
        self.save_ptr = self.ptr
        skipped_words = []
        while(True):
            try:
                m = re.fullmatch(mark,self.now())
                if(m):
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

    def skip_nest(self, smark, emark):
        depth = 0
        while(self.does_reach_to_end() is False):
            if(re.fullmatch(smark,self.now())):
                depth += 1
                self.advance()
                continue
            if(re.fullmatch(emark,self.now())):
                depth -= 1
                self.advance()
                if(depth==0):
                    break
                else:
                    continue
            self.advance()
        

                


    def _index_err(self):
        print(f'Over index (ptr:{self.ptr}, Len:{len(self.words)})')

    def does_reach_to_end(self):
        return self.ptr>=len(self.words)

            
            


class Port():
    def __init__(self,words:Words):
        self.dir = None
        self.name = None
        self.msb = 0
        self.lsb = 0
        self.value = ""
        if(words.now() in Keywords.DICT["port_definition"]):
            self.dir = words.now()
            #output reg や input wire 対策
            while(words.advance() in Keywords.DICT["local_definition"]):
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
        logging.debug(f'Instance:{words.now()}')
        self.module_name  = None
        self.instance_name = None
        save_ptr = words.ptr
        if(Keywords.is_no_keyword(words.now())):
            m = re.fullmatch(r"\w+", words.now())
            if(m):
                module_name = words.now()
                words.advance()
                if(words.now()=="#("):
                    words.skip_nest(smark=r"#?\(", emark=r"\)")
                    m = re.fullmatch("\w+", words.now())
                if(Keywords.is_no_keyword(words.now())):
                    m = re.fullmatch(r"\w+", words.now())
                    if(m):
                        instance_name = words.now()
                        self.module_name   = module_name
                        self.instance_name = instance_name
                        words.advance()
                        return
        #見つからなとき(ここまでにreturn がCallされなかったとき)Pointerを戻す
        words.ptr = save_ptr



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
    def __init__(self,words:Words,type, end_mark=r";"):
        self.names = []
        super().__init__(type=type, msb=0, lsb=0)
        if(words.now() == type):
            self.dir = words.now()
            #output reg や input wire 対策
            while(words.advance() in Keywords.DICT["local_definition"]):
                continue
            m = re.fullmatch(r"\[(?P<msb>[^:]+):(?P<lsb>[^\]]+)\]", words.now())
            if(m):
                self.msb = m.group("msb")
                self.lsb = m.group("lsb")
                words.advance()
            name = words.now(advance=1)
            # memory宣言 (reg [7:0] mem[1023:0]))かどうかのチェック
            m = re.fullmatch(r"\[(?P<msb>[^:]+):(?P<lsb>[^\]]+)\]", words.now())
            if(m):
                name += f'[{m.group("msb")}:{m.group("lsb")}]'
                words.advance()
            self.names.append(name)
            while(True):
                matched_mark = words.check(r"[,;=]",advance=0)
                if(matched_mark==";"):
                    break
                elif(matched_mark=="="):
                    words.advance()
                    self.value = words.skip(mark=end_mark)
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
    def __init__(self,words:Words):
        self.name = None
        self.signals_dict = {}
        for sig_type in self.SIG_TYPE_LIST:
            self.signals_dict[sig_type]        = []
        #self.signals["instances"]    = []
        self.instances               = []

        
        #モジュール名、(paramter、)を取得
        while(words.does_reach_to_end() is False):
            if(words.now() in Keywords.DICT["module_start"]):
                self.name = words.advance()
                words.advance()
                if(words.now()=="#("):
                    type="parameter"
                    while(True):
                        words.advance()
                        locals = Locals(words, type=type, end_mark=r"[,\)]").expand()
                        if(len(locals)!=0):
                            any_detected = True
                            self.signals_dict[type+"s"].extend(locals)
                        if(words.now()=="("):
                            break
                    words.check(r"\(",advance=1)
                    break
                elif(words.now()=="("):
                    words.advance()
                    break
                else:
                    print(f'Illegal format')
                    raise ValueError
            else:
                words.advance()
        #ポートを取得
        while(words.does_reach_to_end() is False):
            port = Port(words)
            if(port.name is not None):
                self.signals_dict["ports"].append(port)
            else:
                break
        #ローカル信号、インスタンスを取得、モジュール(orプリミティブ)の終了を検出
        while(words.does_reach_to_end() is False):
            any_detected = False
            for type in ["reg", "wire", "genvar", "localparam", "parameter"]:
                locals = Locals(words, type=type).expand()
                if(len(locals)!=0):
                    any_detected = True
                    self.signals_dict[type+"s"].extend(locals)
                    break
            if(any_detected):
                continue
            skipped = words.skip_from_begin_to_end()
            if(skipped):
                continue
            instance = Instance(words)
            if(instance.exist()):
                self.instances.append(instance)
                continue
            if(words.now() in Keywords.DICT["module_end"]):
                break
            words.advance()

    def instance_info(self,how_to_specify, name):
        list = []
        if(how_to_specify=="module_name"):
            for instance in self.instances:
                m = re.fullmatch(name, instance.module_name)
                if(m):
                    list.append(m.group())
        elif(how_to_specify=="instance_name"):
            for instance in self.instances:
                m = re.fullmatch(name, instance.instance_name)
                if(m):
                    list.append(m.group())
        else:
            print(f'Allable value of how_specify are "module_name" or "instance_name".')
            raise ValueError
        return list


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
        for instance in self.instances:
            list = []
            list.append(instance.instance_name)
            list.append(instance.module_name)
            print("\t".join(list))



class Modules:
    def __init__(self):
        self.modules = []
    
    def add(self, module:Module):
        self.modules.append(module)

    def pickup(self,module_name)-> Module:
        list = []
        for module in self.modules:
            m = re.fullmatch(module_name, module.name)
            if(m):
                list.append(module)
        return list


    def disp_tree(self, top_module_name):
        self.depth = 0
        print(f'###### Start to display a tree. #############')
        module_list = self.pickup(top_module_name)
        for module in module_list:
            for instance in module.instances:
                self.dive(instance=instance, func=self.print_instance)

    def dive (self, instance:Instance, func):
        func(instance=instance)
        self.depth+=1
        module_name = instance.module_name
        for module in self.pickup(module_name):
            for instance in module.instances:
                self.dive(instance=instance,func=func)
        self.depth-=1

    def print_instance(self,instance:Instance)->None:
        instance_name = instance.instance_name
        module_name   = instance.module_name
        indent_mark = "\t"
        print(f'{indent_mark * self.depth}{instance_name} ({module_name})')
        



def main():
    dir=r"C:\Work\GitLocals\development\core_usb_host\src_v"

    modules = Modules()
    for filename in os.listdir(dir):
        if(re.fullmatch(r"\w+\.v", filename)):
            with open(os.path.join("files", dir + "/" + filename), 'r') as f:
                print(f'Reading...{filename}')
                words_str = ""
                for line in f:
                    line = re.sub("//.*","", line)
                    line = re.sub("\n"," ", line)
                    if(line==""):
                        continue
                    words_str += line
                
                #words_str = re.sub(r"([^\w])", r" \1 ", words_str)
                words_str = re.sub(r"([\(\);,])", r" \1 ", words_str)
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
                module = Module(words)
                if(module.name is None):
                    print(f'{filename} was not a module nor primitive.')
                else:
                    modules.add(module)



                pass


                

                
                    


                #
                #print('"\n"'.join(words.words))
                module.dump()
    #print(modules.pickup(r"\w+crc\w+"))
    modules.disp_tree("usbh_host")



if __name__ == "__main__":
    main()
