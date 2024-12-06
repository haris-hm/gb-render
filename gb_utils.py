import bpy
import os
import math

from bpy.types import Scene, Object, Context
from enum import Enum
from .ui import UIProperties

class FrameType(Enum):
    MASK = 'mask'
    RAW = 'raw'

class EngineType(Enum):
    EEVEE = 'BLENDER_EEVEE_NEXT'
    CYCLES = 'CYCLES'

class SceneData():
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

    def setup_scene(self):
        # Setting elevation
        self.__camera.constraints["Follow Path"].offset_factor = 0.25 + self.__elevation/360

        # Setting azimuth
        self.__camera_track.rotation_mode = 'XYZ'
        self.__camera_track.rotation_euler[2] = math.radians(self.__azimuth)

        # Other
        self.__camera.data.lens = self.__focal_length
        self.__bin_cutter.location.z = self.__bin_cutter_location

    def generate_keyframe(self, frame_num: int):
        self.setup_scene()

        # Add keyframes for all objects
        self.__camera.constraints["Follow Path"].keyframe_insert(data_path="offset_factor", frame=frame_num)
        self.__camera_track.keyframe_insert(data_path="rotation_euler", index=2, frame=frame_num)
        self.__bin_cutter.keyframe_insert(data_path="location", index=2, frame=frame_num)

    def __get_scene_objects(self):
        objects = get_objects(self.__scene)
        self.__camera = objects['camera']
        self.__camera_track = objects['camera_track']
        self.__bin_cutter = objects['bin_cutter']
        self.__grease = objects['grease']
        self.__bin_cutter_location = self.__grease.dimensions.z*(self.__liquid_level*.01)

class RenderFrame():
    def __init__(self, root_path: str, file_name: str, scene: Scene, type: FrameType, scene_data: SceneData, width: int=1920, height: int=1080, samples: int=1024):
        self.__filepath = os.path.join(root_path, file_name)
        self.__scene = scene
        self.__engine = EngineType.CYCLES if type == FrameType.RAW else EngineType.EEVEE
        self.__type = type
        self.__width = width
        self.__height = height
        self.__samples = samples if type == FrameType.RAW else None
        self.__scene_data = scene_data

    def render(self):
        self.__switch_engine()
        self.__scene_data.setup_scene()
        self.__scene.render.filepath = self.__filepath
        bpy.ops.render.render('INVOKE_DEFAULT', write_still=True)

    def generate_keyframe(self, frame_num: int):
        self.__scene_data.generate_keyframe(frame_num)

    def get_type(self) -> FrameType:
        return self.__type
    
    def __toggle_shadows(self, val: bool):
        for obj in self.__scene.objects:
            if hasattr(obj, "visible_shadow"):
                obj.visible_shadow = val
            else:
                raise Exception('Invalid object.')

    def __switch_engine(self):
        if (self.__samples == None and self.__engine == EngineType.CYCLES):
            raise Exception('Cycles must have a sample amount specified.')
        
        self.__scene.render.resolution_x = self.__width
        self.__scene.render.resolution_y = self.__height
        self.__scene.render.engine = self.__engine.value

        # Toggle settings for rendering seg masks
        if self.__engine == EngineType.CYCLES:
            self.__scene.cycles.samples = self.__samples
            self.__toggle_shadows(True)
            self.__scene.view_settings.view_transform = 'AgX'
        else:
            self.__toggle_shadows(False)
            self.__scene.view_settings.view_transform = 'Raw'

class RenderQueue():
    def __init__(self, *items: RenderFrame):
        self.__queue: list[RenderFrame] = []
        self.__length: int = 0
        self.__full_length: int = 0
        self.__curr_frame: int = 0
        for item in items:
            self.add(item)

    def add(self, item):
        self.__queue.append(item)
        self.__length += 1
        self.__full_length += 1
        return self

    def pop(self):
        if len(self) > 0:
            curr_frame: RenderFrame = self.__queue[self.__curr_frame]
            self.__curr_frame += 1
            self.__length -= 1

            if len(self) == 0:
                self.__curr_frame = 0
                self.__full_length = 0
                self.__queue = []

            return curr_frame
        else:
            raise IndexError('This RenderQueue does not have any items.')
        
    def copy(self):
        copy = RenderQueue()
        for i in self.__queue:
            copy.add(i)
        return copy
    
    def full_length(self):
        return self.__full_length
    
    def current_frame(self):
        return self.__curr_frame
    
    def generate_keyframes(self, ctx: Context):
        ctx.scene.frame_start = 1
        ctx.scene.frame_end = len(self.__queue)

        for i, frame in enumerate(self.__queue):
            frame.generate_keyframe(i)
        
    def __len__(self):
        return self.__length
        
    def __add__(self, other):
        self_copy = self.copy()
        other_copy = other.copy()
        while len(other_copy) > 0:
            self_copy.add(other_copy.pop())
        return self_copy
    
    def __repr__(self):
        repr_str: str = '['
        for i in self.__queue:
            repr_str += f'{i.get_type().value}, '

        repr_str = repr_str.removesuffix(', ')
        repr_str += ']'
        return repr_str

class RenderConfig():
    def __init__(self, scene: Scene):
        props: UIProperties = scene.ui_properties

        # Scene Settings
        self.liquid_level: int = props.liquid_level
        self.azimuth_step: int = props.azimuth_step
        self.elevation_step: int = props.elevation_step
        self.max_elevation: int = props.max_elevation
        self.focal_length: int = props.focal_length

        # Render Settings
        self.directory: str = bpy.path.abspath(props.directory)
        self.mask_dir: str = os.path.join(self.directory, 'masks')
        self.image_dir: str = os.path.join(self.directory, 'images')
        self.sequence_setting: int = int(props.render_sequence)
        self.mask_prefix: str = props.mask_prefix
        self.image_prefix: str = props.image_prefix
        self.sample_amount: int = props.sample_amount
        self.width: int = props.width
        self.height: int = props.height
    
class AnimationSequence():
    def __init__(self, ctx: Context, frames: RenderQueue):
        self.__scene: Scene = ctx.scene
        self.__cfg: RenderConfig = RenderConfig(self.__scene)
        self.__frames = frames
        self.__frames.generate_keyframes(ctx)
        self.rendered_masks: bool = False
        self.fully_rendered: bool = False

    def render_masks(self):
        self.__scene.render.filepath = os.path.join(self.__cfg.mask_dir, f'{self.__cfg.mask_prefix}_000000')
        self.rendered_masks = True
        self.__switch_engine(EngineType.EEVEE)
        bpy.ops.render.render('INVOKE_DEFAULT', animation=True, write_still=True)

    def render_images(self):
        self.__scene.render.filepath = os.path.join(self.__cfg.image_dir, f'{self.__cfg.image_prefix}_000000')
        self.fully_rendered = True
        self.__switch_engine(EngineType.CYCLES)
        bpy.ops.render.render('INVOKE_DEFAULT', animation=True, write_still=True)

    def __toggle_shadows(self, val: bool):
        for obj in self.__scene.objects:
            if hasattr(obj, "visible_shadow"):
                obj.visible_shadow = val
            else:
                raise Exception('Invalid object.')

    def __switch_engine(self, engine: EngineType):
        if (self.__cfg.sample_amount == None and engine == EngineType.CYCLES):
            raise Exception('Cycles must have a sample amount specified.')
        
        self.__scene.frame_current = 1
        self.__scene.render.resolution_x = self.__cfg.width
        self.__scene.render.resolution_y = self.__cfg.height
        self.__scene.render.engine = engine.value

        # Toggle settings for rendering seg masks
        if engine == EngineType.CYCLES:
            self.__scene.cycles.samples = self.__cfg.sample_amount
            self.__toggle_shadows(True)
            self.__scene.view_settings.view_transform = 'AgX'
        else:
            self.__toggle_shadows(False)
            self.__scene.view_settings.view_transform = 'Raw'

def get_objects(scene: Scene) -> dict[str, Object]:
    ui_props = scene.ui_properties
    objects = {
        'camera':       ui_props.camera,
        'camera_track': ui_props.camera_track,
        'bin_cutter':   ui_props.bin_cutter,
        'grease':       ui_props.grease
    }
    
    # Object Validation
    if(objects['camera'] == None or objects['camera'].type != 'CAMERA'):
        objects['camera'] = None
        raise Exception('Invalid camera object. Please pick a camera in the scene.')
    elif(objects['camera_track'] == None or objects['camera_track'].type != 'CURVE'):
        objects['camera_track'] = None
        raise Exception('Invalid camera track object. Please pick a curve object.')
    elif(objects['bin_cutter'] == None or objects['bin_cutter'].type != 'MESH'):
        objects['bin_cutter'] = None
        raise Exception('Invalid bin cutter object. Please pick a mesh object.')
    elif(objects['grease'] == None or objects['grease'].type != 'MESH'):
        objects['grease'] = None
        raise Exception('Invalid grease object. Please pick a mesh object.')
    
    # Constraint Validation
    try: 
        objects['camera'].constraints["Follow Path"].use_fixed_location = True
        objects['camera'].constraints["Follow Path"].use_curve_follow = True
        objects['camera'].constraints["Follow Path"].use_curve_radius = True
        objects['camera'].constraints["Follow Path"].target = objects['camera_track']
    except:
        raise Exception("Please add a \"Follow Path\" constraint onto the camera.")
    
    return objects
