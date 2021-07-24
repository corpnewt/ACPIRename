from Scripts import *
import os, sys, binascii

class ACPIRename:
    def __init__(self, **kwargs):
        self.dl = downloader.Downloader()
        self.u  = utils.Utils("ACPI Rename")
        self.r  = run.Run()
        try:
            self.d = dsdt.DSDT()
        except Exception as e:
            print("Something went wrong :( - Aborting!\n - {}".format(e))
            exit(1)
        self.dsdt = None
        self.scripts = "Scripts"

    def select_dsdt(self):
        self.u.head("Select DSDT")
        print(" ")
        print("M. Main")
        print("Q. Quit")
        print(" ")
        dsdt = self.u.grab("Please drag and drop a DSDT.aml or origin folder here:  ")
        if dsdt.lower() == "m":
            return self.dsdt
        if dsdt.lower() == "q":
            self.u.custom_quit()
        out = self.u.check_path(dsdt)
        if out:
            if self.d.load(out):
                return out
        return self.select_dsdt()

    def ensure_dsdt(self):
        if self.dsdt and self.d.dsdt:
            # Got it already
            return True
        # Need to prompt
        self.dsdt = self.select_dsdt()
        if self.dsdt and self.d.dsdt:
            return True
        return False

    def ensure_path(self, plist_data, path_list, final_type = list):
        if not path_list: return plist_data
        last = plist_data
        for index,path in enumerate(path_list):
            if not path in last:
                if index >= len(path_list)-1:
                    last[path] = final_type()
                else:
                    last[path] = {}
            last = last[path]
        return plist_data

    def list_paths(self, path_type="Device"):
        if not self.ensure_dsdt(): return
        self.u.head()
        print("")
        paths = []
        for path in self.d.dsdt_paths:
            if path[-1].lower() != path_type.lower(): continue
            print("{} ({})".format(path[0],path[1]))
        print("")
        self.u.grab("Press [enter] to return...")

    def gen_rename(self):
        if not self.ensure_dsdt(): return
        device = None
        while True:
            self.u.head()
            print("")
            print("M. Return To Main Menu")
            print("Q. Quit")
            print("")
            path = self.u.grab("Please input the path/search term:  ")
            if not path: continue
            if path.lower() == "m": return
            if path.lower() == "q": self.u.custom_quit()
            print("")
            # See if we get a device/method that matches that
            d = self.d.get_device_paths(path)
            m = self.d.get_method_paths(path)
            n = self.d.get_name_paths(path)
            if not any((d,m,n)):
                self.u.head()
                print("")
                print("No device/method/name found for that search!")
                print("")
                self.u.grab("Press [enter] to return...")
                continue
            # Get the first entry in order of Device -> Method -> Name
            if d: device   = d[0]
            elif m: device = m[0]
            else: device   = n[0]
            # We have something now - prompt for a rename
            find_t = device[0].split(".")[-1]
            find_h = binascii.hexlify(find_t.encode("utf-8") if sys.version_info >= (3,0) else find_t).upper()
            if sys.version_info >= (3,0): find_h = find_h.decode("utf-8")
            padl,padr = self.d.get_shortest_unique_pad(find_h,self.d.find_next_hex(device[1])[1])
            while True:
                self.u.head()
                print("")
                print("Current Path: {}".format(device[0]))
                print(" -----> Find: {} - {}".format(find_t,padl+find_h+padr))
                print("")
                print("S. Return To Search")
                print("M. Return To Main Menu")
                print("Q. Quit")
                print("")
                repl_t = self.u.grab("Please input the replace ascii:  ")
                if not repl_t: continue
                if repl_t.lower() == "s": break
                if repl_t.lower() == "m": return
                if repl_t.lower() == "q": self.u.custom_quit()
                # Got our replace text - make sure it's the same length as the find
                if not len(find_t) == len(repl_t):
                    self.u.head()
                    print("")
                    print("Length mismatch!  Replace must be {:,} characters!".format(len(find_t)))
                    print("")
                    self.u.grab("Press [enter] to return...")
                    continue
                # Same length - make sure they're not the same
                if find_t == repl_t:
                    self.u.head()
                    print("")
                    print("Find and replace are the same - nothing to do...")
                    print("")
                    self.u.grab("Press [enter] to return...")
                    continue
                # Should have a find and replace that are valid now - get the padding, and generate the rename
                repl_h = binascii.hexlify(repl_t.encode("utf-8") if sys.version_info >= (3,0) else repl_t).upper()
                if sys.version_info >= (3,0): repl_h = repl_h.decode("utf-8")
                self.u.head()
                print("")
                print("Current Path: {}".format(device[0]))
                print(" -----> Find: {} - {}".format(find_t,padl+find_h+padr))
                print(" --> Replace: {} - {}".format(repl_t,padl+repl_h+padr))
                print("")
                self.u.grab("Press [enter] to return...")
                break

    def main(self):
        cwd = os.getcwd()
        self.u.head()
        print("")
        print("Current DSDT:  {}".format(self.dsdt))
        print("")
        print("1. Generate Unique Rename")
        print("2. List Device Paths")
        print("3. List Method Paths")
        print("4. List Name Paths")
        print("")
        print("D. Select DSDT or origin folder")
        print("Q. Quit")
        print("")
        menu = self.u.grab("Please make a selection:  ")
        if not len(menu):
            return
        if menu.lower() == "q":
            self.u.custom_quit()
        if menu.lower() == "d":
            self.dsdt = self.select_dsdt()
            return
        if menu == "1":
            self.gen_rename()
        elif menu == "2":
            self.list_paths(path_type="Device")
        elif menu == "3":
            self.list_paths(path_type="Method")
        elif menu == "4":
            self.list_paths(path_type="Name")
        return

if __name__ == '__main__':
    if 2/3 == 0: input = raw_input
    a = ACPIRename()
    while True:
        try:
            a.main()
        except Exception as e:
            print("An error occurred: {}".format(e))
            input("Press [enter] to continue...")
