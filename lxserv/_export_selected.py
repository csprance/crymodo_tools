import lx

from cs_cry_export.commander import CommanderClass
import cs_cry_export.export_selected as export_selected


class ExportSelected(CommanderClass):

    def commander_execute(self, msg, flags):
        reload(export_selected)
        export_selected.main()


lx.bless(ExportSelected, "cs_cry_export.export")
