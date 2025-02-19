import bpy

from bpy.props import IntProperty, FloatProperty, BoolProperty, StringProperty, PointerProperty, EnumProperty
from bpy.types import PropertyGroup, Object, Material, Context

class DataElements(PropertyGroup):  
    render_estimate: IntProperty(
        name='Render Estimate',
        default=int(round((360/10) * ((90/10)+1)))
    ) 

    render_progress: FloatProperty(
        name = 'Render Progress',
        min = 0,
        max = 1,
        update=lambda self, ctx: ctx.area.tag_redraw()  # Update the UI when changed
    ) 

    show_render_progress: BoolProperty(
        name = 'Show Render Progress',
        default = False
    ) 

    keyframes_generated: BoolProperty(
        name = 'data_keyframes_generated',
        default = False
    ) 

def update_render_btn(self, ctx: Context):
    # Access properties from their respective classes
    azimuth_step = ctx.scene.parameter_settings_elements.azimuth_step
    elevation_step = ctx.scene.parameter_settings_elements.elevation_step
    max_elevation = ctx.scene.parameter_settings_elements.max_elevation
    render_sequence = ctx.scene.render_settings_elements.render_sequence

    estimate = (360 / azimuth_step) * ((max_elevation / elevation_step) + 1)
    if int(render_sequence) == 0:
        estimate *= 2

    ctx.scene.gb_data.render_estimate = int(round(estimate))

    for area in ctx.screen.areas:
        if area.type == 'VIEW_3D':
            for region in area.regions:
                if region.type == 'UI':
                    region.tag_redraw()

class ObjectSelectionElements(PropertyGroup):
    grease: PointerProperty(
        name = 'Bin',
        type = Object,
        description = 'Select the bin',
        update=lambda self, ctx: ctx.area.tag_redraw()  # Update the UI when changed
    ) 

    camera: PointerProperty(
        name = 'Camera',
        type = Object,
        description = 'Select the camera',
        update=lambda self, ctx: ctx.area.tag_redraw()  # Update the UI when changed
    ) 

    camera_track: PointerProperty(
        name = 'Camera Track',
        type = Object,
        description = 'Select the camera track curve',
        update=lambda self, ctx: ctx.area.tag_redraw()  # Update the UI when changed
    ) 

    bin_cutter: PointerProperty(
        name = 'Bin Cutter',
        type = Object,
        description = 'Select the bin cutter',
        update=lambda self, ctx: ctx.area.tag_redraw()  # Update the UI when changed
    ) 

class MaterialElements(PropertyGroup):
    bin_int_mat: PointerProperty(
        name = 'Interior',
        type = Material,
        description = 'Select the bin interior material'
    ) 

    bin_ext_mat: PointerProperty(
        name = 'Exterior',
        type = Material,
        description = 'Select the bin exterior material'
    ) 

    grease_mat: PointerProperty(
        name = 'Grease',
        type = Material,
        description = 'Select the grease material'
    ) 

    grease_group: bpy.props.StringProperty(
        name="Group",
        description="Select the grease node group"
    ) 

    bin_ext_group: bpy.props.StringProperty(
        name="Group",
        description="Select the bin node group"
    ) 

    bin_int_group: bpy.props.StringProperty(
        name="Group",
        description="Select the bin node group"
    ) 

class ParameterSettingsElements(PropertyGroup):
    liquid_level: IntProperty(
        name = 'Liquid Level',
        default = 100,
        min = 0,
        max = 100,
        subtype = 'PERCENTAGE'
    ) 

    azimuth_step: IntProperty(
        name = 'Azimuth Step',
        default = 10,
        min = 1,
        max = 360,
        subtype = 'FACTOR',
        update = update_render_btn
    ) 

    elevation_step: IntProperty(
        name = 'Elevation Step',
        default = 10,
        min = 1,
        max = 360,
        subtype = 'FACTOR',
        update = update_render_btn
    ) 

    max_elevation: IntProperty(
        name = 'Max Elevation',
        default = 60,
        min = 0,
        max = 90,
        subtype = 'FACTOR',
        update = update_render_btn
    ) 

    focal_length: IntProperty(
        name = 'Focal length',
        default = 50,
        min = 1,
        max = 150,
        subtype = 'DISTANCE_CAMERA'
    ) 

class RenderSettingsElements(PropertyGroup):
    directory: StringProperty(
        name = 'Directory',
        subtype ='DIR_PATH'
    ) 

    mask_prefix: StringProperty(
        name = 'Mask Prefix',
        default = 'MASK'
    ) 

    image_prefix: StringProperty(
        name = 'Image Prefix',
        default = 'RGB'
    ) 

    width: IntProperty(
        name = 'Width',
        default = 1920,
        min = 1,
    ) 

    height: IntProperty(
        name = 'Height',
        default = 1080,
        min = 1
    ) 

    sample_amount: IntProperty(
        name = 'Sample Amount',
        default = 256,
        min = 1,
        max = 2048
    ) 

    render_sequence: EnumProperty(
        items = [
            ('0', 'Masks then Images', 'All masks are rendered, followed by all images', '', 0),
            ('1', 'Images Only', 'Only the images are rendered', '', 1),
            ('2', 'Masks Only', 'Only the masks are rendered', '', 2)
        ],
        name = '',
        default = '0',
        update = update_render_btn
    )  
