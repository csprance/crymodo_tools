import os
import sys
from datetime import datetime

import lx
import modo

import cs_cry_export.utils as utils
from cs_cry_export import rc, __version__
from cs_cry_export.constants import (
    COLLADA_TEMP_PATH,
    CRYEXPORTNODE_PREFIX,
    CHANNEL_FILETYPE_NAME,
    CHANNEL_EXPORTABLE_NAME,
    CHANNEL_MERGE_OBJECTS_NAME,
)
from lxml import etree
from lxml.builder import ElementMaker

# This doesn't need to be a class attribute
E = ElementMaker()


class CryDAEBuilder:
    # the dae element
    xml = E.COLLADA()
    # the lxo file path
    scene_root = ""
    # The path of the DAE file created by the builder
    path = ""
    # the path to the temp collada file
    collada_temp_path = COLLADA_TEMP_PATH

    def __init__(self, cryexport_node):
        self.cryexport_node = cryexport_node
        self.scene_root = lx.eval1("query sceneservice scene.file ? current")
        if not self.scene_root:
            modo.dialogs.alert("Save File", "Please save file before exporting.")
            sys.exit()
        self.path = os.path.join(
            os.path.dirname(self.scene_root), self.collada_temp_path
        )
        self.wpos_matrix = modo.Matrix4(self.cryexport_node.channel("wposMatrix").get())
        self.submats = utils.get_submats_from_cryexport_node(self.cryexport_node)
        self.neat_name = self.cryexport_node.name.replace(CRYEXPORTNODE_PREFIX, "")
        self.file_type = self.cryexport_node.channel(CHANNEL_FILETYPE_NAME)
        if self.file_type is None:
            self.file_type = "1"

        self.exportable = self.cryexport_node.channel(CHANNEL_EXPORTABLE_NAME)
        if self.exportable is None:
            self.exportable = "1"

        self.merge_objects = self.cryexport_node.channel(CHANNEL_MERGE_OBJECTS_NAME)
        if self.merge_objects is None:
            self.merge_objects = "0"

    def compile(self):
        """
        Call me first to gather the data and compile the dae file
        Create the XML Structure of the DAE file given all the parameters in the class
        """
        self.xml = E.COLLADA(
            {
                "xmlns": "http://www.collada.org/2005/11/COLLADASchema",
                "version": "1.4.1",
            },
            E.asset(
                E.contributor(
                    E.author(os.environ.get("USERNAME")),
                    E.authoring_tool("CRYENGINE modo COLLADA Exporter {0}".format(__version__)),
                    E.source_data("file://" + self.scene_root.replace("\\", "/")),
                ),
                E.created(str(datetime.now())),
                E.modified(str(datetime.now())),
                E.revision("1.4.1"),
                E.unit({"name": "meter", "meter": "1.0000000000e+000"}),
                E.up_axis("Z_UP"),
            ),
            E.library_animation_clips(),
            E.library_animations(),
            E.library_effects(
                *[
                    self.create_effect(id=utils.make_effect_name(mat, idx))
                    for idx, mat in enumerate(self.submats)
                ]
            ),
            E.library_materials(
                *[
                    E.material(
                        {"id": utils.make_phys_material_name(mat, idx)},
                        E.instance_effect(
                            {"url": utils.make_phys_material_name(mat, idx, hash=True)}
                        ),
                    )
                    for idx, mat in enumerate(self.submats)
                ]
            ),
            E.library_geometries(),
            E.library_controllers(),
            E.library_visual_scenes(
                E.visual_scene(
                    {"id": "visual_scene_0", "name": "untitled"},
                    E.node(
                        {"id": self.cryexport_node.name},
                        E.translate({"sid": "translation"}, self.get_root_translate()),
                        E.rotate({"sid": "rotation_z"}, self.get_root_rotation("z")),
                        E.rotate({"sid": "rotation_y"}, self.get_root_rotation("y")),
                        E.rotate({"sid": "rotation_x"}, self.get_root_rotation("x")),
                        E.scale({"sid": "scale"}, self.get_root_scale()),
                        # self.create_helper_node(),
                        self.create_extra(fileType="cgf", customExportPath="..\\"),
                    ),
                )
            ),
            E.library_images(),
            E.scene(E.instance_visual_scene({"url": "#visual_scene_0"})),
        )

    def write(self):
        """
        Call me last to write the file out to the correct path
        Write the DAE file out to disk @self.path
        :return:
        """
        with open(self.path, "w") as f:
            f.write('<?xml version="1.0" encoding="utf-8"?>\n')
            f.write(etree.tostring(self.xml, pretty_print=True))

    # ####################################################################################
    #                   Modo Methods
    #
    # ####################################################################################
    def get_root_translate(self):
        return " ".join(map(str, self.wpos_matrix.position))

    def get_root_rotation(self, axis):
        _axis = {"x": 0, "y": 1, "z": 2}[axis]
        return " ".join(map(str, self.wpos_matrix.asRotateMatrix()[_axis]))

    def get_root_scale(self):
        return " ".join(map(str, self.wpos_matrix.scale()))

    # ####################################################################################
    #                   XML Utility Methods Methods
    #
    # ####################################################################################

    def create_extra(self, **kwargs):
        properties = "\n".join(
            map(
                lambda x: "%s%s%s" % (x[0], x[1], x[2]),
                zip(kwargs.keys(), ["="] * len(kwargs.keys()), kwargs.values()),
            )
        )
        return E.extra(
            E.technique(
                {"profile": "CryEngine"},
                E.properties("DoNotMerge\nUseCustomNormals\n" + properties),
            ),
            E.technique(
                {"profile": "XSI"},
                E.XSI_CustomPSet(
                    {"name": "ExportProperties"},
                    E.propagation("NODE"),
                    E.type("CryExportNodeProperties"),
                    E.XSI_Parameter(
                        {"id": "Filetype", "type": "Integer", "value": self.file_type}
                    ),
                    E.XSI_Parameter(
                        {"id": "Filename", "type": "Text", "value": self.neat_name}
                    ),
                    E.XSI_Parameter(
                        {"id": "Exportable", "type": "Boolean", "value": self.exportable}
                    ),
                    E.XSI_Parameter(
                        {"id": "MergeObjects", "type": "Boolean", "value": self.merge_objects}
                    ),
                ),
            ),
        )

    def create_helper_node(
        self,
        id="default",
        trans="0 0 0",
        rot_z="0 0 1 0",
        rot_y="0 1 0 0",
        rot_x="1 0 0 0",
        scale="1 1 1",
    ):
        node = E.node(
            {"id": id},
            E.translate({"sid": "translation"}, trans),
            E.rotate({"sid": "rotation_z"}, rot_z),
            E.rotate({"sid": "rotation_y"}, rot_y),
            E.rotate({"sid": "rotation_x"}, rot_x),
            E.scale({"sid": "scale"}, scale),
            E.extra(
                E.technique(
                    {"profile": "CryEngine"},
                    E.helper(
                        {"type": "dummy"},
                        E.bound_box_min("-5 -5 -5"),
                        E.bound_box_max("5 5 5"),
                    ),
                )
            ),
        )

        return node

    def create_effect(
        self,
        id="effect-mat-name",
        emission="0.0 0.0 0.0 1.0",
        ambient="0.0 0.0 0.0 1.0",
        diffuse="0.0 0.0 0.0 1.0",
        specular="0.0 0.0 0.0 1.0",
        shininess="1.0",
        reflective="0.0 0.0 0.0 1.0",
        reflectivity="1.0",
        transparent="0.0 0.0 0.0 1.0",
        transparency="1.0",
        index_of_refraction="1.0",
    ):
        return E.effect(
            {"id": id},
            E.profile_COMMON(
                E.technique(
                    {"sid": "default"},
                    E.phong(
                        E.emission(E.color({"sid": "emission"}, emission)),
                        E.ambient(E.color({"sid": "ambient"}, ambient)),
                        E.diffuse(E.color({"sid": "diffuse"}, diffuse)),
                        E.specular(E.color({"sid": "specular"}, specular)),
                        E.shininess(E.float({"sid": "shininess"}, shininess)),
                        E.reflective(E.color({"sid": "reflective"}, reflective)),
                        E.reflectivity(E.float({"sid": "reflectivity"}, reflectivity)),
                        E.transparent(
                            {"opaque": "RGB_ZERO"},
                            E.color({"sid": "transparent"}, transparent),
                        ),
                        E.transparency(E.float({"sid": "transparency"}, transparency)),
                        E.index_of_refraction(
                            E.float({"sid": "index_of_refraction"}, index_of_refraction)
                        ),
                    ),
                )
            ),
        )


def main():
    reload(rc)
    reload(utils)
    for cryexport_node in utils.get_cryexportnodes():
        dae = CryDAEBuilder(cryexport_node)
        dae.compile()
        dae.write()
        rc.run(path=dae.path)
    # if (
    #     modo.dialogs.yesNo(
    #         "Export Success",
    #         "Would you like to open the folder containing the exported objects?",
    #     )
    #     is "yes"
    # ):
    #     subprocess.Popen(r'explorer "%s"' % os.path.dirname(dae.path))


if __name__ == "__main__":
    main()
