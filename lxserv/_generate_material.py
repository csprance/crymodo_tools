import lx

from cs_cry_export.commander import CommanderClass
import cs_cry_export.generate_material as generate_material


class GenerateMaterial(CommanderClass):

    def commander_execute(self, msg, flags):
        reload(generate_material)
        generate_material.main()


lx.bless(GenerateMaterial, "cs_cry_export.generate_material")
