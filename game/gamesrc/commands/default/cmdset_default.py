"""
This module ties together all the commands of the default command set. 
"""
from src.commands.cmdset import CmdSet
from game.gamesrc.commands.default import general, help, admin, system
from game.gamesrc.commands.default import tests, comms, building
from game.gamesrc.commands.default import batchprocess

class DefaultCmdSet(CmdSet):
    """
    Implements the default command set.
    """
    key = "DefaultMUX"

    def at_cmdset_creation(self):
        "Populates the cmdset"

        # The general commands
        self.add(general.CmdLook())
        self.add(general.CmdHome())
        self.add(general.CmdPassword())
        self.add(general.CmdInventory())
        self.add(general.CmdQuit())
        self.add(general.CmdPose())
        self.add(general.CmdNick())
        self.add(general.CmdGet())
        self.add(general.CmdDrop())
        self.add(general.CmdWho())
        self.add(general.CmdSay())
        self.add(general.CmdGroup())
        self.add(general.CmdEncoding())

        # The help system
        self.add(help.CmdHelp())
        self.add(help.CmdSetHelp())

        # System commands
        self.add(system.CmdReload())
        self.add(system.CmdPy())
        self.add(system.CmdListScripts())        
        self.add(system.CmdListObjects())
        self.add(system.CmdService())
        self.add(system.CmdShutdown())
        self.add(system.CmdVersion())
        self.add(system.CmdTime())
        self.add(system.CmdList())
        self.add(system.CmdPs())
        self.add(system.CmdStats())

        # Admin commands
        self.add(admin.CmdBoot())
        self.add(admin.CmdDelPlayer())
        self.add(admin.CmdEmit())
        self.add(admin.CmdNewPassword())
        self.add(admin.CmdPerm())
        self.add(admin.CmdPuppet())
        self.add(admin.CmdWall())

        # Building and world manipulation
        self.add(building.CmdTeleport())
        self.add(building.CmdSetObjAlias())
        self.add(building.CmdListCmdSets())
        self.add(building.CmdDebug())    
        self.add(building.CmdWipe())
        self.add(building.CmdSetAttribute())        
        self.add(building.CmdName())
        self.add(building.CmdDesc())
        #self.add(building.CmdCpAttr()) #TODO - need testing/debugging
        #self.add(building.CmdMvAttr()) #TODO - need testing/debugging
        self.add(building.CmdFind())
        self.add(building.CmdCopy()) #TODO - need testing/debugging
        self.add(building.CmdOpen())
        self.add(building.CmdLink())
        self.add(building.CmdUnLink())
        self.add(building.CmdCreate())        
        self.add(building.CmdDig())
        self.add(building.CmdDestroy())
        self.add(building.CmdExamine())
        self.add(building.CmdTypeclass())

        # Comm commands
        self.add(comms.CmdAddCom())
        self.add(comms.CmdDelCom())
        self.add(comms.CmdComlist())
        self.add(comms.CmdClist())
        self.add(comms.CmdCdestroy())
        self.add(comms.CmdChannelCreate())
        self.add(comms.CmdCdesc())
        self.add(comms.CmdPage())
        
        # Batchprocessor commands
        self.add(batchprocess.CmdBatchCommands())
        self.add(batchprocess.CmdBatchCode())

        # Testing commands 
        self.add(tests.CmdTest())
        self.add(tests.CmdTestPerms())
        self.add(tests.TestCom())

        # Start MUD-type commands, definately needs some clean-up
        from game.gamesrc.commands.fuss_importer import importer
        self.add(importer.CmdFussImport)
