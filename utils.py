import bpy
import os
import math

from bpy.types import Scene, Object, Context, Collection
from enum import Enum

class FrameType(Enum):
    MASK = 'mask'
    RAW = 'raw'

class RenderConfig():
    def __init__(self, scene: Scene):
        param_props = scene.parameter_settings_elements
        render_props = scene.render_settings_elements
        seg_props = scene.segmentation_colors_elements

        # Scene Settings
        self.liquid_level: int = param_props.liquid_level
        self.azimuth_step: int = param_props.azimuth_step
        self.elevation_step: int = param_props.elevation_step
        self.max_elevation: int = param_props.max_elevation
        self.focal_length: int = param_props.focal_length

        # Render Settings
        self.directory: str = bpy.path.abspath(render_props.directory)
        self.mask_dir: str = os.path.join(self.directory, 'masks')
        self.image_dir: str = os.path.join(self.directory, 'images')
        self.sequence_setting: int = int(render_props.render_sequence)
        self.mask_prefix: str = render_props.mask_prefix
        self.image_prefix: str = render_props.image_prefix
        self.sample_amount: int = render_props.sample_amount
        self.width: int = render_props.width
        self.height: int = render_props.height

        # Segmentation colors
        self.segmentation_colors: dict[str, tuple[int]] = {
            'bin_interior': tuple(seg_props.bin_interior),
            'bin_exterior': tuple(seg_props.bin_exterior),
            'bin_rim': tuple(seg_props.bin_rim),
            'grease': tuple(seg_props.grease)
        }

class FrameData():
    __camera: Object = None
    __camera_track: Object = None
    __bin_cutter: Object = None
    __grease: Object = None
    __bin_cutter_location: float = 0

    def __init__(self, scene: Scene, azimuth: int=0, elevation: int=0, focal_length: int=35, liquid_level:int=100):
        self.__scene = scene
        self.__azimuth = azimuth
        self.__elevation = elevation
        self.__focal_length = focal_length  
        self.__liquid_level = liquid_level

        self.__get_scene_objects()

    def generate_keyframe(self, frame_num: int):
        # Setting elevation
        self.__camera.constraints["Follow Path"].offset_factor = 0.25 + self.__elevation/360

        # Setting azimuth
        self.__camera_track.rotation_mode = 'XYZ'
        self.__camera_track.rotation_euler[2] = math.radians(self.__azimuth)

        # Other
        self.__camera.data.lens = self.__focal_length
        self.__bin_cutter.location.z = self.__bin_cutter_location

        # Add keyframes for all objects
        self.__camera.constraints["Follow Path"].keyframe_insert(data_path="offset_factor", frame=frame_num)
        self.__camera_track.keyframe_insert(data_path="rotation_euler", index=2, frame=frame_num)
        self.__bin_cutter.keyframe_insert(data_path="location", index=2, frame=frame_num)

    def __get_scene_objects(self):
        objects: dict[str, Object] = get_objects(self.__scene)
        self.__camera = objects['camera']
        self.__camera_track = objects['camera_track']
        self.__bin_cutter = objects['bin_cutter']
        self.__grease = objects['grease']
        self.__bin_cutter_location = self.__grease.dimensions.z*(self.__liquid_level*.01)

class RenderQueue():
    def __init__(self, *items: FrameData):
        self.__queue: list[FrameData] = []
        self.__length: int = 0
        self.__max_len: int = 0
        self.__curr_frame: int = 0
        for item in items:
            self.add(item)

    def add(self, item):
        self.__queue.append(item)
        self.__length += 1
        self.__max_len += 1
        return self

    def pop(self) -> FrameData:
        if len(self) > 0:
            curr_frame: FrameData = self.__queue[self.__curr_frame]
            self.__curr_frame += 1
            self.__length -= 1

            if len(self) == 0:
                self.__curr_frame = 0
                self.__max_len = 0
                self.__queue = []

            return curr_frame
        else:
            raise IndexError('This RenderQueue does not have any items.')
    
    def max_length(self) -> int:
        return self.__max_len
        
    def __len__(self) -> int:
        return self.__length
    
    def __repr__(self) -> str:
        repr_str: str = '['
        for i in self.__queue:
            repr_str += f'{i.get_type().value}, '

        repr_str = repr_str.removesuffix(', ')
        repr_str += ']'
        return repr_str
    
class AnimationSequence():
    def __init__(self, ctx: Context, frames: RenderQueue):
        self.__scene: Scene = ctx.scene
        self.__cfg: RenderConfig = RenderConfig(self.__scene)

        self.__generate_keyframes(ctx, frames)

    def render(self, frame_type: FrameType):
        self.__setup_engine(frame_type)
        bpy.ops.render.render('INVOKE_DEFAULT', animation=True, write_still=False)

    def save_frame(self, frame_type: FrameType):
        frame: int = self.__scene.frame_current
        render_result: bpy.types.Image = bpy.data.images.get("Render Result")

        if render_result is None:
            self.report({"ERROR"}, "Render Result not found")
            return

        print(f'{frame_type=}')

        match frame_type:
            case FrameType.MASK:
                path: str = os.path.join(self.__cfg.mask_dir, f'{self.__cfg.mask_prefix}_{frame:08d}.png')
                render_result.save_render(filepath=path)
            case FrameType.RAW:
                path: str = os.path.join(self.__cfg.image_dir, f'{self.__cfg.image_prefix}_{frame:08d}.png')
                render_result.save_render(filepath=path)

    def __generate_keyframes(self, ctx: Context, frames: RenderQueue):
        ctx.scene.frame_start = 1
        ctx.scene.frame_end = frames.max_length()

        # Clear old keyframes
        for obj in get_objects(ctx.scene).values():
            if isinstance(obj, Collection):
                continue
            if obj.animation_data:
                obj.animation_data_clear()

        for i in range(1, frames.max_length()):
            frame: FrameData = frames.pop()
            frame.generate_keyframe(i)

        ctx.scene.gb_data.keyframes_generated = True

    def __setup_engine(self, frame_type: FrameType):    
        objects: dict[str, Object] = get_objects(self.__scene)
        rgb_bin_collection: Collection = objects['rgb_bin']
        seg_bin_collection: Collection = objects['seg_bin']

        self.__scene.render.engine = 'CYCLES'

        self.__scene.frame_current = 1
        self.__scene.render.resolution_x = self.__cfg.width
        self.__scene.render.resolution_y = self.__cfg.height

        # Enable emmision pass; Used for masks
        self.__scene.view_layers["ViewLayer"].use_pass_emit = True
        
        if frame_type == FrameType.RAW: # Settings for rendering RGB images
            # Set samples, time limit, and anti-aliasing
            self.__scene.cycles.samples = self.__cfg.sample_amount
            self.__scene.cycles.time_limit = 60
            self.__scene.cycles.filter_width = 1.5
            
            # Enable denoising and adaptive sampling ('noise threshold')
            self.__scene.cycles.use_denoising = True
            self.__scene.cycles.use_adaptive_sampling = True

            # Change color profile to one that adds color grading
            self.__scene.view_settings.view_transform = 'AgX'

            # Setup render visibility
            rgb_bin_collection.hide_render = False
            seg_bin_collection.hide_render = True

            # Setup compositor
            self.__scene.node_tree.nodes['Switch'].check = False
        else: # Settings for rendering seg masks
            # Lower samples, set time limit to 0, and disable anti-aliasing
            self.__scene.cycles.samples = 1
            self.__scene.cycles.time_limit = 0
            self.__scene.cycles.filter_width = 0.01

            # Disable denoising and adaptive sampling
            self.__scene.cycles.use_denoising = False
            self.__scene.cycles.use_adaptive_sampling = False

            # Change color profile to one which doesn't change the colors
            self.__scene.view_settings.view_transform = 'Raw'

            # Setup render visibility
            rgb_bin_collection.hide_render = True
            seg_bin_collection.hide_render = False

            # Setup compositor
            self.__scene.node_tree.nodes['Switch'].check = True

def get_objects(scene: Scene) -> dict[str, Object | Collection]:
    object_selection_props = scene.object_selection_elements
    objects = {
        'camera':       object_selection_props.camera,
        'camera_track': object_selection_props.camera_track,
        'bin_cutter':   object_selection_props.bin_cutter,
        'grease':       object_selection_props.grease,
        'rgb_bin':      object_selection_props.rgb_bin,
        'seg_bin':      object_selection_props.seg_bin
    }
    
    # Object Validation
    if(objects['camera'] is None or objects['camera'].type != 'CAMERA'):
        objects['camera'] = None
        raise Exception('Invalid camera object. Please pick a camera in the scene.')
    elif(objects['camera_track'] is None or objects['camera_track'].type != 'CURVE'):
        objects['camera_track'] = None
        raise Exception('Invalid camera track object. Please pick a curve object.')
    elif(objects['bin_cutter'] is None or objects['bin_cutter'].type != 'MESH'):
        objects['bin_cutter'] = None
        raise Exception('Invalid bin cutter object. Please pick a mesh object.')
    elif(objects['grease'] is None or objects['grease'].type != 'MESH'):
        objects['grease'] = None
        raise Exception('Invalid grease object. Please pick a mesh object.')
    
    # Constraint Validation
    try: 
        objects['camera'].constraints["Follow Path"].use_fixed_location = True
        objects['camera'].constraints["Follow Path"].use_curve_follow = True
        objects['camera'].constraints["Follow Path"].use_curve_radius = True
        objects['camera'].constraints["Follow Path"].target = objects['camera_track']
    except Exception as _:
        raise Exception("Please add a \"Follow Path\" constraint onto the camera.")
    
    return objects

def create_frames(scene: Scene) -> RenderQueue:
    cfg: RenderConfig = RenderConfig(scene)

    # Creating Directories
    if (not os.path.exists(cfg.mask_dir)):
        os.mkdir(cfg.mask_dir)
    if (not os.path.exists(cfg.image_dir)):
        os.mkdir(cfg.image_dir)

    # Loop variables
    frames: RenderQueue = RenderQueue()

    curr_azimuth: int = 0
    curr_elevation: int = 0

    while curr_elevation <= cfg.max_elevation:
        while curr_azimuth < 360:
            frame_data: FrameData = FrameData(scene, curr_azimuth, curr_elevation, cfg.focal_length, cfg.liquid_level)
            frames.add(frame_data)

            curr_azimuth += cfg.azimuth_step

        curr_elevation += cfg.elevation_step
        curr_azimuth = 0
        
    return frames
