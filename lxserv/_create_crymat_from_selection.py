import lx

import cs_cry_export.create_crymat_from_selection as create_crymat
from cs_cry_export.commander import CommanderClass


class CreateCryMatFromSelection(CommanderClass):

    def commander_execute(self, msg, flags):
        reload(create_crymat)
        create_crymat.main()


lx.bless(CreateCryMatFromSelection, "cs_cry_export.create_crymat_from_selection")
