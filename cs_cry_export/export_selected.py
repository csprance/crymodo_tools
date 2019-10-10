import os
import sys
from datetime import datetime
from lxml import etree
from lxml.builder import ElementMaker

import lx
import modo

from cs_cry_export import rc


class CryDAEBuilder:
    E = ElementMaker()
    # the dae element
    xml = E.COLLADA()
    # the lxo file path
    scene_root = ""
    # The path of the DAE file created by the builder
    path = ""

    def __init__(self):
        self.scene_root = lx.eval1("query sceneservice scene.file ? current")
        if not self.scene_root:
            modo.dialogs.alert("Save File", "Please save file before exporting.")
            sys.exit()
        self.path = os.path.join(
            os.path.dirname(self.scene_root), "cry_collada_temp.dae"
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
        node = self.E.node(
            {"id": id},
            self.E.translate({"sid": "translation"}, trans),
            self.E.rotate({"sid": "rotation_z"}, rot_z),
            self.E.rotate({"sid": "rotation_y"}, rot_y),
            self.E.rotate({"sid": "rotation_x"}, rot_x),
            self.E.scale({"sid": "scale"}, scale),
            self.E.extra(
                self.E.technique(
                    {"profile": "CryEngine"},
                    self.E.helper(
                        {"type": "dummy"},
                        self.E.bound_box_min("-5 -5 -5"),
                        self.E.bound_box_max("5 5 5"),
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
        return self.E.effect(
            {"id": id},
            self.E.profile_COMMON(
                self.E.technique(
                    {"sid": "default"},
                    self.E.phong(
                        self.E.emission(self.E.color({"sid": "emission"}, emission)),
                        self.E.ambient(self.E.color({"sid": "ambient"}, ambient)),
                        self.E.diffuse(self.E.color({"sid": "diffuse"}, diffuse)),
                        self.E.specular(self.E.color({"sid": "specular"}, specular)),
                        self.E.shininess(self.E.float({"sid": "shininess"}, shininess)),
                        self.E.reflective(
                            self.E.color({"sid": "reflective"}, reflective)
                        ),
                        self.E.reflectivity(
                            self.E.float({"sid": "reflectivity"}, reflectivity)
                        ),
                        self.E.transparent(
                            {"opaque": "RGB_ZERO"},
                            self.E.color({"sid": "transparent"}, transparent),
                        ),
                        self.E.transparency(
                            self.E.float({"sid": "transparency"}, transparency)
                        ),
                        self.E.index_of_refraction(
                            self.E.float(
                                {"sid": "index_of_refraction"}, index_of_refraction
                            )
                        ),
                    ),
                )
            ),
        )

    def compile(self):
        """
        Create the XML Structure of the DAE file given all the parameters in the class
        """
        self.xml = self.E.COLLADA(
            {
                "xmlns": "http://www.collada.org/2005/11/COLLADASchema",
                "version": "1.4.1",
            },
            self.E.asset(
                self.E.contributor(
                    self.E.author(os.environ.get("USERNAME")),
                    self.E.authoring_tool("CRYENGINE modo COLLADA Exporter 1.0.0"),
                    self.E.source_data("file://" + self.scene_root.replace("\\", "/")),
                ),
                self.E.created(str(datetime.now())),
                self.E.modified(str(datetime.now())),
                self.E.revision("1.4.1"),
                self.E.unit({"name": "meter", "meter": "1.0000000000e+000"}),
                self.E.up_axis("Z_UP"),
            ),
            self.E.library_animation_clips(),
            self.E.library_animations(),
            self.E.library_effects(
                self.create_effect(id="test5"),
                self.create_effect(id="test1"),
                self.create_effect(id="test2"),
            ),
            self.E.library_materials(
                self.E.material(
                    {"id": "mat-id"}, self.E.instance_effect({"url": "#mat-id"})
                ),
                self.E.material(
                    {"id": "mat-id1"}, self.E.instance_effect({"url": "#mat-id1"})
                ),
            ),
            self.E.library_geometries(),
            self.E.library_controllers(),
            self.E.library_visual_scenes(self.create_helper_node()),
            self.E.library_images(),
            self.E.scene(),
        )

    def write(self):
        """
        Write the DAE file out to disk @self.path
        :return:
        """
        with open(self.path, "w") as f:
            f.write('<?xml version="1.0" encoding="utf-8"?>\n')
            f.write(etree.tostring(self.xml, pretty_print=True))


def main():
    dae = CryDAEBuilder()
    dae.compile()
    dae.write()
    rc.run(path=dae.path)


if __name__ == "__main__":
    main()
