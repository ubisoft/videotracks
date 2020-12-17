import bpy
from ..utils import utils


# Patch to upgrade the shot manager data created with a shot manager version older than V.1.2.25

# v1_2_25: 1002025
def data_patch_to_v1_2_25():
    for scn in bpy.data.scenes:
        # if "UAS_shot_manager_props" in scn:
        if getattr(bpy.context.scene, "UAS_shot_manager_props", None) is not None:
            #  print("\n   Shot Manager instance found in scene " + scn.name)
            props = scn.UAS_shot_manager_props

            # print("     Data version: ", props.dataVersion)
            # print("     Shot Manager version: ", bpy.context.window_manager.UAS_shot_manager_version)
            if props.dataVersion <= 0 or props.dataVersion < bpy.context.window_manager.UAS_shot_manager_version:

                # apply patch and apply new data version
                #   print("       Applying data patch data_patch_to_v1_2_25 to scenes")
                takes = props.getTakes()
                for take in takes:
                    take.getParentScene()
                    shots = props.getShotsList()
                    for shot in shots:
                        shot.getParentScene()

                # set right data version
                # props.dataVersion = bpy.context.window_manager.UAS_shot_manager_version
                props.dataVersion = 1002025
                print("       Data upgraded to version V.", utils.convertVersionIntToStr(props.dataVersion))
