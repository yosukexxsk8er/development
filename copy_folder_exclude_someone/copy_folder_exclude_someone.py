import os
import shutil


class MyCopy:
    def __init__(self, from_base_dir, to_base_dir, exclude_list=[]):
        if(not os.path.exists(from_base_dir)):
            raise FileNotFoundError(f"{from_base_dir} is not found")

        self.from_base_dir = from_base_dir
        self.to_base_dir   = to_base_dir + "/" + os.path.basename(from_base_dir)
        self.copy_list     = []
        self.mkdir_list    = []
        self.mkdir_list.append(to_base_dir + "/" + os.path.basename(from_base_dir))
        self.exclude_list  = exclude_list


    def dive_folder(self, cur_folder_path):
        for file_or_folder_name in os.listdir(cur_folder_path):
            file_or_folder_path = cur_folder_path + "/" + file_or_folder_name
            for exclude_name in self.exclude_list:
                if(exclude_name in file_or_folder_path):
                    break
            else:
                if os.path.isfile(file_or_folder_path):
                    self.copy_list.append(file_or_folder_path)
                else:
                    self.mkdir_list.append(file_or_folder_path.replace(self.from_base_dir, self.to_base_dir))
                    self.dive_folder(file_or_folder_path)
        return

    def dump_list(self):
        print (f"from {self.from_base_dir} to {self.to_base_dir}")
        command_list = []
        for item in self.mkdir_list:
            if(os.path.exists(item)):
                raise FileExistsError(f"{item} is already exists")
            print(f"making dir {item}")
            os.makedirs(item)
            self.copy_metadata(item.replace(self.from_base_dir, self.to_base_dir), item)
        for item in self.copy_list:
            print(f"copying from {item} to {item.replace(self.from_base_dir, self.to_base_dir)}")
            shutil.copy2(item,item.replace(self.from_base_dir, self.to_base_dir))

    def copy_metadata(self, source_dir, dest_dir):
        # メタデータを元ディレクトリから取得
        source_stat = os.stat(source_dir)

        # タイムスタンプのコピー (アクセス時間と修正時間)
        os.utime(dest_dir, (source_stat.st_atime, source_stat.st_mtime))

        # パーミッションのコピー
        os.chmod(dest_dir, source_stat.st_mode)

    


def main():
    pass
    from_base_dir = r"C:\Users\yosuk\Downloads\test"
    to_base_dir   = r"C:\Users\yosuk\Downloads\CopyTemp"
    exclude_list  = ["aaa", "01-122-722x1024"]
    my_copy = MyCopy(from_base_dir=from_base_dir, to_base_dir=to_base_dir, exclude_list=exclude_list)
    my_copy.dive_folder(from_base_dir)
    my_copy.dump_list()
    pass



if __name__ == "__main__":
    main()
