import lx

import cs_cry_export.setup as setup
from cs_cry_export.commander import CommanderClass


class Setup(CommanderClass):
    """ This converts a folder into a CRYENGINE read group (replaces cs_crysetup)"""

    def commander_execute(self, msg, flags):
        reload(setup)
        setup.main()


lx.bless(Setup, "cs_cry_export.setup")
