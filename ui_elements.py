import bpy

from bpy.props import *
from bpy.types import PropertyGroup, Object, Material, Context

class DataElements(PropertyGroup):  
    render_estimate: IntProperty(
        name='Render Estimate',
        default=int(round((360/10) * ((90/10)+1)))
    ) # type: ignore

    render_progress: FloatProperty(
        name = 'Render Progress',
        min = 0,
        max = 1,
        update=lambda self, ctx: ctx.area.tag_redraw()  # Update the UI when changed
    ) # type: ignore

    show_render_progress: BoolProperty(
        name = 'Show Render Progress',
        default = False
    ) # type: ignore

    keyframes_generated: BoolProperty(
        name = 'data_keyframes_generated',
        default = False
    ) # type: ignore


def update_render_btn(self, ctx: Context):
    azimuth_step = self.azimuth_step
    elevation_step = self.elevation_step
    max_elevation = self.max_elevation

    estimate = (360/azimuth_step) * ((max_elevation/elevation_step)+1)
    if (int(self.render_sequence) == 0 or int(self.render_sequence) == 1):
        estimate *= 2

    self.render_estimate = int(round(estimate))

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

class MaterialElements(PropertyGroup):
    bin_int_mat: PointerProperty(
        name = 'Interior',
        type = Material,
        description = 'Select the bin interior material'
    ) # type: ignore

    bin_ext_mat: PointerProperty(
        name = 'Exterior',
        type = Material,
        description = 'Select the bin exterior material'
    ) # type: ignore

    grease_mat: PointerProperty(
        name = 'Grease',
        type = Material,
        description = 'Select the grease material'
    ) # type: ignore

    grease_group: bpy.props.StringProperty(
        name="Group",
        description="Select the grease node group"
    ) # type: ignore

    bin_ext_group: bpy.props.StringProperty(
        name="Group",
        description="Select the bin node group"
    ) # type: ignore

    bin_int_group: bpy.props.StringProperty(
        name="Group",
        description="Select the bin node group"
    ) # type: ignore

class ParameterSettingsElements(PropertyGroup):
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
        min = 0,
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

class RenderSettingsElements(PropertyGroup):
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

    sample_amount: IntProperty(
        name = 'Sample Amount',
        default = 256,
        min = 1,
        max = 2048
    ) # type: ignore

    render_sequence: EnumProperty(
        items = [
            ('0', 'Pairs', 'The raw image is rendered, subsequently followed by rendering the mask image', '', 0),
            ('1', 'Masks then Images', 'All masks are rendered, followed by all images', '', 1),
            ('2', 'Images Only', 'Only the images are rendered', '', 2),
            ('3', 'Masks Only', 'Only the masks are rendered', '', 3)
        ],
        name = '',
        default = '1',
        update = update_render_btn
    )  # type: ignore
