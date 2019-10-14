import lx

import cs_cry_export.create_helper as create_helper
from cs_cry_export.commander import CommanderClass


class CreateCryHelper(CommanderClass):

    def commander_execute(self, msg, flags):
        reload(create_helper)
        create_helper.main()


lx.bless(CreateCryHelper, "cs_cry_export.create_helper")
