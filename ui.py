import bpy

from bpy.props import *
from bpy.types import PropertyGroup, Panel, Object, Context, Scene, Operator, Event

class UIProperties(PropertyGroup):
    bin: PointerProperty(
        name = 'Bin',
        type = Object,
        description = 'Select the bin'
    ) # type: ignore

    camera: PointerProperty(
        name = 'Camera',
        type = Object,
        description = 'Select the camera'
    ) # type: ignore

    camera_track: PointerProperty(
        name = 'Camera Track',
        type = Object,
        description = 'Select the camera track curve'
    ) # type: ignore

    bin_cutter: PointerProperty(
        name = 'Bin Cutter',
        type = Object,
        description = 'Select the bin cutter'
    ) # type: ignore

    liquid_level: IntProperty(
        name = 'Liquid Level',
        default = 100,
        min = 0,
        max = 100,
        subtype = 'PERCENTAGE'
    ) # type: ignore

    azimuth_step: IntProperty(
        name = 'Azimuth Step',
        default = 10,
        min = 1,
        max = 360,
        subtype = 'FACTOR'
    ) # type: ignore

    elevation_step: IntProperty(
        name = 'Elevation Step',
        default = 10,
        min = 1,
        max = 360,
        subtype = 'FACTOR'
    ) # type: ignore

    max_elevation: IntProperty(
        name = 'Max Elevation',
        default = 60,
        min = 1,
        max = 90,
        subtype = 'FACTOR'
    ) # type: ignore

    focal_length: IntProperty(
        name = 'Focal length',
        default = 50,
        min = 1,
        max = 150,
        subtype = 'DISTANCE_CAMERA'
    ) # type: ignore

class VIEW3D_PT_controls(Panel):
    # Where to add panel in UI
    bl_space_type = 'VIEW_3D' # 3D Viewport Area
    bl_region_type = 'UI' # Sidebar region
    
    # Add labels
    bl_category = 'Grease Bin Rendering'
    bl_label = 'Grease Bin Rendering'
    
    def draw (self, ctx: Context):
        layout = self.layout
        props = ctx.scene.ui_properties

        layout.label(text="Select Objects:")
        layout.prop_search(props, "bin", bpy.data, "objects", text="Bin")
        layout.prop_search(props, "camera", bpy.data, "objects", text="Camera")
        layout.prop_search(props, "camera_track", bpy.data, "objects", text="Cam Track")
        layout.prop_search(props, "bin_cutter", bpy.data, "objects", text="Bin Cutter")

        row = self.layout.row()
        row.operator("wm.parameter_tuning", text="Adjust Parameters", icon="SETTINGS")

        row = self.layout.row()
        row.operator("render.render_pairs", text="Render Pairs", icon="RENDER_RESULT")

    def register():
        Scene.ui_properties = bpy.props.PointerProperty(type=UIProperties)

    def unregister():
        del Scene.ui_properties


class WM_OT_parameter_tuning(Operator):
    bl_idname = 'wm.parameter_tuning'
    bl_label = 'Parameter Settings'

    def invoke(self, ctx: Context, event: Event):
        wm = ctx.window_manager
        return wm.invoke_props_dialog(self)
    
    def draw(self, ctx: Context):
        ui_properties = ctx.scene.ui_properties
        layout = self.layout

        layout.label(text="Camera Movement (Extrinsic):")
        box = layout.box()
        row = box.row()
        row.label(text= "Azimuth Step:", icon = 'ARROW_LEFTRIGHT')
        row.prop(ui_properties, "azimuth_step")

        row = box.row()
        row.label(text= "Elevation Step:", icon = 'EVENT_UP_ARROW')
        row.prop(ui_properties, "elevation_step")

        row = box.row()
        row.label(text= "Max Elevation", icon = 'EMPTY_SINGLE_ARROW')
        row.prop(ui_properties, "max_elevation")

        layout.separator(factor= 1)

        layout.label(text="Camera Properties (Intrinsic):")
        box = layout.box()
        row = box.row()
        row.label(text= "Focal Length", icon = 'VIEW_CAMERA')
        row.prop(ui_properties, "focal_length")

    def execute(self, ctx: Context):
        return {"FINISHED"}
        