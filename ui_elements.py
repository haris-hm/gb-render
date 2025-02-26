import bpy

from bpy.props import IntProperty, FloatProperty, BoolProperty, StringProperty, PointerProperty, EnumProperty, FloatVectorProperty
from bpy.types import PropertyGroup, Object, Material, Context, Collection
from uuid import uuid4

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

    starting_elevation = ctx.scene.parameter_settings_elements.starting_elevation
    max_elevation = ctx.scene.parameter_settings_elements.max_elevation
    elevation_step = ctx.scene.parameter_settings_elements.elevation_step

    zoom_levels = ctx.scene.parameter_settings_elements.zoom_levels

    starting_liquid_level = ctx.scene.parameter_settings_elements.starting_liquid_level
    liquid_level_step = ctx.scene.parameter_settings_elements.liquid_level_step

    render_sequence = ctx.scene.render_settings_elements.render_sequence

    # Calculate the estimated number of frames
    azimuths_rendered: float = 360 / azimuth_step
    elevations_rendered: int = ((max_elevation-starting_elevation) // elevation_step) + 1
    liquid_levels: int = ((100-starting_liquid_level) / liquid_level_step) + 1

    estimate = azimuths_rendered * elevations_rendered * zoom_levels * liquid_levels
    if int(render_sequence) == 0:
        estimate *= 2
        
    ctx.scene.gb_data.render_estimate = int(round(estimate))

    # Update the UI
    for area in ctx.screen.areas:
        if area.type == 'VIEW_3D':
            for region in area.regions:
                if region.type == 'UI':
                    region.tag_redraw()

def update_seg_colors(self, context):
    def get_rgb_color(material):
        if material and material.node_tree:
            for node in material.node_tree.nodes:
                if node.type == 'RGB':
                    return node.outputs[0].default_value[:3]
        return (0.0, 0.0, 0.0)

    self.bin_interior = get_rgb_color(self.bin_int_mat)
    self.bin_exterior = get_rgb_color(self.bin_ext_mat)
    self.bin_rim = get_rgb_color(self.bin_rim_mat)
    self.grease = get_rgb_color(self.grease_mat)

def update_seg_material_colors(self, context):
    def set_rgb_color(material, color):
        if material and material.node_tree:
            for node in material.node_tree.nodes:
                if node.type == 'RGB':
                    # Set the RGB color with alpha 1.0
                    node.outputs[0].default_value = (*color, 1.0)  

    set_rgb_color(self.bin_int_mat, self.bin_interior)
    set_rgb_color(self.bin_ext_mat, self.bin_exterior)
    set_rgb_color(self.bin_rim_mat, self.bin_rim)
    set_rgb_color(self.grease_mat, self.grease)

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
        name = 'Grease Cutter',
        type = Object,
        description = 'Select the grease cutter',
        update=lambda self, ctx: ctx.area.tag_redraw()  # Update the UI when changed
    )

    seg_bin_cutter: PointerProperty(
        name = 'Seg Grease Cutter',
        type = Object,
        description = 'Select the segmentation grease cutter',
        update=lambda self, ctx: ctx.area.tag_redraw()  # Update the UI when changed
    ) 

    rgb_bin: PointerProperty(
        name = 'RGB Bin',
        type = Collection,
        description = 'Select the textured bin collection',
        update=lambda self, ctx: ctx.area.tag_redraw()  # Update the UI when changed
    ) 

    seg_bin: PointerProperty(
        name = 'SEG Bin',
        type = Collection,
        description = 'Select the segmented bin colleciton',
        update=lambda self, ctx: ctx.area.tag_redraw()  # Update the UI when changed
    ) 

class SegmentationColorsElements(PropertyGroup):
    bin_int_mat: PointerProperty(
        name = 'Interior',
        type = Material,
        description = 'Select the bin interior segmentation material',
        update = update_seg_colors
    ) 

    bin_ext_mat: PointerProperty(
        name = 'Exterior',
        type = Material,
        description = 'Select the bin exterior segmentation material',
        update = update_seg_colors
    ) 

    bin_rim_mat: PointerProperty(
        name = 'Rim',
        type = Material,
        description = 'Select the bin rim segmentation material',
        update = update_seg_colors
    ) 

    grease_mat: PointerProperty(
        name = 'Grease',
        type = Material,
        description = 'Select the grease segmentation material',
        update = update_seg_colors
    ) 

    bin_interior: FloatVectorProperty(
        name="Bin Interior Color",
        subtype='COLOR',
        default=(0.0, 0.0, 1.0),  
        min=0.0, max=1.0,
        description="Select the color for the bin interior",
        update=update_seg_material_colors
    )

    bin_exterior: FloatVectorProperty(
        name="Bin Exterior Color",
        subtype='COLOR',
        default=(0.0, 1.0, 1.0),  
        min=0.0, max=1.0,
        description="Select the color for the bin exterior",
        update=update_seg_material_colors
    )

    bin_rim: FloatVectorProperty(
        name="Bin Rim Color",
        subtype='COLOR',
        default=(1.0, 0.0, 0.0),  
        min=0.0, max=1.0,
        description="Select the color for the bin rim",
        update=update_seg_material_colors
    )

    grease: FloatVectorProperty(
        name="Grease Color",
        subtype='COLOR',
        default=(1.0, 1.0, 0.0),  
        min=0.0, max=1.0,
        description="Select the color for the grease",
        update=update_seg_material_colors
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
    starting_liquid_level: IntProperty(
        name = 'Starting Liquid Level',
        default = 100,
        min = 0,
        max = 100,
        subtype = 'PERCENTAGE',
        update=update_render_btn
    ) 

    liquid_level_step: IntProperty(
        name = 'Liquid Level step',
        default = 20,
        min = 1,
        max = 100,
        subtype = 'FACTOR',
        update = update_render_btn
    ) 

    azimuth_step: IntProperty(
        name = 'Azimuth Step',
        default = 10,
        min = 1,
        max = 360,
        subtype = 'FACTOR',
        update = update_render_btn
    ) 

    starting_elevation: IntProperty(
        name = 'Starting Elevation',
        default = 10,
        min = 1,
        max = 90,
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

    elevation_step: IntProperty(
        name = 'Elevation Step',
        default = 10,
        min = 1,
        max = 360,
        subtype = 'FACTOR',
        update = update_render_btn
    ) 

    starting_zoom: FloatProperty(
        name = 'Starting Zoom',
        default = 1,
        min = 0.5,
        max = 2,
        subtype = 'FACTOR',
        update = update_render_btn
    )

    zoom_step: FloatProperty(
        name = 'Zoom Step',
        default = 0.5,
        min = 0.1,
        max = 1,
        subtype = 'FACTOR',
        update = update_render_btn
    )

    zoom_levels: IntProperty(
        name = 'Zoom Levels',
        default = 3,
        min = 1,
        max = 10,
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

    dataset_name: StringProperty(
        name = 'Dataset Name',
        default = f'gb_dataset_{uuid4()}'
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
