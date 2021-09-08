from ciscoconfparse import CiscoConfParse
from os import listdir, path, remove,mkdir
from datetime import datetime
import os


class cleaning:
    # cleaning dictionnary 
    cleaning = {
        'basic' : True,
        'username' : True,
        'access-list' : True,
        'management' : True,
        'shutdown_interfaces' : True, 
        'vrf' : [],
        'files' : [],
    }

    folders = ['input', 'output','templates','static']

    ## will create the folder if not existing
    def createFolders(self,listFol):
        for f in listFol:
            if not path.isdir(f):
                mkdir(f)

    ## fill the files list in the cleaning dictionary
    def fileList(self,listFiles):
        self.cleaning['files'] = listFiles

    ## return the list of VRF on all the fileList
    def vrfList(self, fileList):
        output = []
        for myfile in fileList:
            parse = CiscoConfParse(path.join('input',myfile), syntax='nxos')
            vrf = parse.find_objects('^vrf context')
            for v in vrf:
                output.append(v.text.split(' ')[2])
            del parse
        output = list(dict.fromkeys(output))
        if 'management' in output:
            output.remove('management')
        
        return output
 
    ## fill tthe VRF list to be clean in the cleaning dictionary
    def vrfToClean(self,vrfListClean):
        self.cleaning['vrf'] = list(dict.fromkeys(vrfListClean))
        if 'management' in self.cleaning['vrf']:
            self.cleaning['vrf'].remove('management')
            

    ## init instance
    ## will create the folder missing
    ## will fill the file list inside 'input' directory
    def __init__(self):
        self.createFolders(self.folders)
        self.fileList(listdir('input'))

    ## update the file list inside 'input' folder
    def update(self):
        self.fileList(listdir('input'))

    ## execute the cleaning depending the cleaning dictionary and save in 'output' folder
    def confclean(self):
        directory = datetime.now().strftime("%Y_%m_%d_%H%M%S")
        for f in self.cleaning['files']:
            parse = CiscoConfParse(path.join('input',f), syntax='nxos')
            #clean the basic configuration
            if self.cleaning['basic'] :
                # version OS of the configuration
                parse.delete_lines('^version')
                # all non-applicable configuration
                parse.delete_lines('^!')
                # domain
                parse.delete_lines('^ip domain-name')
                # tacacas configuration
                parse.delete_lines('^tacacs-server')
                # snmp configuration
                parse.delete_lines('^snmp-server')
                # rmon 
                parse.delete_lines('^rmon')
                # ntp
                parse.delete_lines('^ntp server')
                # boot version
                parse.delete_lines('^boot')
                # ssh key
                parse.delete_lines('^ssh key')
                # aaa conf + children
                parse.replace_all_children('^aaa','.*','')
                parse.delete_lines('^aaa')
                #logging server
                parse.replace_all_children('^logging','.*','')
                parse.delete_lines('^logging')
                # console and vty configurations
                parse.replace_all_children('^line','.*','')
                parse.delete_lines('^line')

            # remove username and add username admin/cisco!123 
            if self.cleaning['username'] :
                parse.delete_lines('^username')
                parse.insert_before('^vlan 1$',insertstr='username admin password cisco!123 role network-admin')

            # remove all the access lists
            if self.cleaning['access-list'] :
                parse.replace_all_children('^ip access-list','.*','')
                parse.delete_lines('^ip access-list')

            # remove the vrf manamgenent context and the references of mgmt0 to avoid conflict
            if self.cleaning['management'] :
                parse.replace_all_children('^vrf context management','.*','')
                parse.delete_lines('^vrf context management')
                parse.replace_all_children('mgmt0','.*','')
                parse.delete_lines('mgmt0')

            # remove all the physical interfaces shutdown
            if self.cleaning['shutdown_interfaces']:
                for int in parse.find_parents_wo_child('interface Ethernet','no shutdown'):
                    parse.replace_all_children('^'+int+'$','.*','')
                    parse.delete_lines('^'+int+'$')

            # remove the checked vrf 
            for vrf in self.cleaning['vrf']:
                # vrf context with all the static routes
                for v in parse.find_objects('^vrf context '+vrf):
                    parse.replace_all_children(v.text+'$','.*','')
                    parse.delete_lines('^'+v.text+'$')
                # routing protocol (OSPF, BGP etc ...) where the vrf is configured
                for v in parse.find_objects('vrf '+vrf):
                    parse.replace_all_children(v.text+'$','.*','')
                    parse.delete_lines(v.text+'$')
                # interfaces where 'vrf member' are mentioned
                for v in parse.find_parents_w_child('.*','vrf member '+vrf,):
                    parse.replace_all_children('^'+v+'$','.*','')
                    parse.delete_lines('^'+v+'$')

            
            parse.save_as(path.join('output',directory,f))    

## only for troubleshooting
def main():
    pass

if __name__ == '__main__' :
    main()      
