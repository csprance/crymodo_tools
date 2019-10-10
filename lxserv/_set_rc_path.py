import lx

from cs_cry_export import rc
from cs_cry_export.commander import CommanderClass


class SetRCPath(CommanderClass):
    """
    This is used in the preferences to open up a file dialog and set the RC path
    """

    def commander_execute(self, msg, flags):
        reload(rc)
        rc.set_rc_path()


lx.bless(SetRCPath, "cs_cry_export.set_rc_path")
