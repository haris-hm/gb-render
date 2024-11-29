import bpy

from bpy.props import *
from bpy.types import PropertyGroup, Panel, Object, Context, Scene, Operator, Event

def update_render_btn(self, ctx: Context):
    azimuth_step = self.azimuth_step
    elevation_step = self.elevation_step
    max_elevation = self.max_elevation

    estimate = (360/azimuth_step) * ((max_elevation/elevation_step)+1)
    print(int(round(estimate)), estimate)
    self.render_estimate = int(round(estimate))

    for area in ctx.screen.areas:
        if area.type == 'VIEW_3D':
            for region in area.regions:
                if region.type == 'UI':
                    region.tag_redraw()

class UIProperties(PropertyGroup):
    bin: PointerProperty(
        name = 'Bin',
        type = Object,
        description = 'Select the bin',
        update=lambda self, ctx: ctx.area.tag_redraw()  # Update the UI when changed
    ) # type: ignore

    camera: PointerProperty(
        name = 'Camera',
        type = Object,
        description = 'Select the camera',
        update=lambda self, ctx: ctx.area.tag_redraw()  # Update the UI when changed
    ) # type: ignore

    camera_track: PointerProperty(
        name = 'Camera Track',
        type = Object,
        description = 'Select the camera track curve',
        update=lambda self, ctx: ctx.area.tag_redraw()  # Update the UI when changed
    ) # type: ignore

    bin_cutter: PointerProperty(
        name = 'Bin Cutter',
        type = Object,
        description = 'Select the bin cutter',
        update=lambda self, ctx: ctx.area.tag_redraw()  # Update the UI when changed
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
        subtype = 'FACTOR',
        update = update_render_btn
    ) # type: ignore

    elevation_step: IntProperty(
        name = 'Elevation Step',
        default = 10,
        min = 1,
        max = 360,
        subtype = 'FACTOR',
        update = update_render_btn
    ) # type: ignore

    max_elevation: IntProperty(
        name = 'Max Elevation',
        default = 60,
        min = 1,
        max = 90,
        subtype = 'FACTOR',
        update = update_render_btn
    ) # type: ignore

    focal_length: IntProperty(
        name = 'Focal length',
        default = 50,
        min = 1,
        max = 150,
        subtype = 'DISTANCE_CAMERA'
    ) # type: ignore

    render_estimate: IntProperty(
        name='Render Estimate',
        default=int(round((360/10) * ((90/10)+1)))
    ) # type: ignore

    render_sequence: EnumProperty(
        items = [
            ('0', 'Pairs', 'The raw image is rendered, subsequently followed by rendering the mask image', '', 0),
            ('1', 'Masks then Images', 'All masks are rendered, followed by all images', '', 1),
            ('2', 'Images Only', 'Only the images are rendered', '', 2),
            ('3', 'Masks Only', 'Only the masks are rendered', '', 3)
        ],
        name = '',
        default = '1'
    )  # type: ignore

    directory: StringProperty(
        name = 'Directory',
        subtype ='DIR_PATH'
    ) # type: ignore

    mask_prefix: StringProperty(
        name = 'Mask Prefix',
        default = 'MASK'
    ) # type: ignore

    image_prefix: StringProperty(
        name = 'Image Prefix',
        default = 'RGB'
    ) # type: ignore

    sample_amount: IntProperty(
        name = 'Sample Amount',
        default = 256,
        min = 1,
        max = 2048
    ) # type: ignore

    width: IntProperty(
        name = 'Width',
        default = 1920,
        min = 1,
    ) # type: ignore

    height: IntProperty(
        name = 'Height',
        default = 1080,
        min = 1
    ) # type: ignore

class VIEW3D_PT_objects(Panel):
    bl_idname = "VIEW3D_PT_objects"
    bl_label = "Objects"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Grease Bin Rendering"

    def draw(self, ctx: Context):
        layout = self.layout
        props = ctx.scene.ui_properties

        layout.label(text="Select Objects:")
        layout.prop_search(props, "bin", bpy.data, "objects", text="Bin")
        layout.prop_search(props, "camera", bpy.data, "objects", text="Camera")
        layout.prop_search(props, "camera_track", bpy.data, "objects", text="Cam Track")
        layout.prop_search(props, "bin_cutter", bpy.data, "objects", text="Bin Cutter")

class VIEW3D_PT_controls(Panel):
    bl_idname = "VIEW3D_PT_controls"
    bl_label = "Settings"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Grease Bin Rendering"
    
    def draw (self, ctx: Context):
        layout = self.layout
        props = ctx.scene.ui_properties

        box = layout.box()
        row = box.row()
        row.operator("wm.parameter_tuning", text="Adjust Parameters", icon="SETTINGS")

        row = box.row()
        row.operator("wm.render_settings", text="Adjust Render Settings", icon="SETTINGS")

        layout.separator(factor= 1)

        row = self.layout.row()
        row.operator("render.render_queued_items", text=f'Render ({props.render_estimate} Images)', icon="RENDER_RESULT")

    def register():
        Scene.ui_properties = bpy.props.PointerProperty(type=UIProperties)

    def unregister():
        del Scene.ui_properties
        
class WM_OT_parameter_tuning(Operator):
    bl_idname = 'wm.parameter_tuning'
    bl_label = 'Parameter Settings'

    def invoke(self, ctx: Context, event: Event):
        wm = ctx.window_manager
        return wm.invoke_props_dialog(self, width=500)
    
    def draw(self, ctx: Context):
        props = ctx.scene.ui_properties
        layout = self.layout

        layout.label(text="Camera Movement (Extrinsic):")
        box = layout.box()
        row = box.row()
        row.label(text= "Azimuth Step:", icon = 'ARROW_LEFTRIGHT')
        row.prop(props, "azimuth_step")

        row = box.row()
        row.label(text= "Elevation Step:", icon = 'EVENT_UP_ARROW')
        row.prop(props, "elevation_step")

        row = box.row()
        row.label(text= "Max Elevation", icon = 'EMPTY_SINGLE_ARROW')
        row.prop(props, "max_elevation")

        layout.separator(factor= 1)

        layout.label(text="Camera Properties (Intrinsic):")
        box = layout.box()
        row = box.row()
        row.label(text= "Focal Length", icon = 'VIEW_CAMERA')
        row.prop(props, "focal_length")

    def execute(self, ctx: Context):
        return {"FINISHED"}
    
    
class WM_OT_render_settings(Operator):
    bl_idname = 'wm.render_settings'
    bl_label = 'Render Settings'

    def invoke(self, ctx: Context, event: Event):
        wm = ctx.window_manager
        return wm.invoke_props_dialog(self, width=700)
    
    def draw(self, ctx: Context):
        props = ctx.scene.ui_properties
        layout = self.layout

        row = layout.row()
        row.label(text='File Settings:')
        box = layout.box()
        row = box.row()
        row.prop(props, 'directory')
        row = box.row()
        row.prop(props, 'mask_prefix')
        row.prop(props, 'image_prefix')

        row = layout.row()
        row.label(text='Image Quality Settings')
        box = layout.box()
        row = box.row()
        row.prop(props, 'width')
        row.prop(props, 'height')
        row = box.row()
        row.prop(props, 'sample_amount')

        row = layout.row()
        row.label(text='Render Sequence:')
        row.prop(props, 'render_sequence')

    def execute(self, ctx: Context):
        return {"FINISHED"}