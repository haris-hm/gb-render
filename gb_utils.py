import bpy
import os

from bpy.types import Scene, Object
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
    __bin: Object = None

    def __init__(self, scene: Scene, azimuth: int=0, elevation: int=0, max_elevation: int=90, focal_length: int=35, liquid_level:int=100):
        self.__scene = scene
        self.__azimuth = azimuth
        self.__elevation = elevation
        self.__max_elevation = max_elevation
        self.__focal_length = focal_length  
        self.__liquid_level = liquid_level

        self.__get_scene_objects()

    def setup_scene(self):
        self.__camera.constraints["Follow Path"].offset_factor = self.__azimuth/360
        self.__camera_track.location.z += 1/self.__elevation if self.__elevation > 0 else 0

    def __get_scene_objects(self):
        objects = get_objects(self.__scene)
        self.__camera = objects['camera']
        self.__camera_track = objects['camera_track']
        self.__bin_cutter = objects['bin_cutter']
        self.__bin = objects['bin']

class RenderFrame():
    def __init__(self, root_path: str, file_name: str, scene: Scene, type: FrameType, scene_data: SceneData, width: int=1920, height: int=1080, samples: int=1024):
        self.__filepath = os.path.join(root_path, f'{file_name}_{type.value}.png')
        self.__scene = scene
        self.__engine = EngineType.CYCLES if type == FrameType.RAW else EngineType.EEVEE
        self.__width = width
        self.__height = height
        self.__samples = samples if type == FrameType.RAW else None
        self.__scene_data = scene_data

    def render(self):
        self.__switch_engine()
        self.__scene_data.setup_scene()
        self.__scene.render.filepath = self.__filepath
        bpy.ops.render.render('INVOKE_DEFAULT', write_still=True)  

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
    __queue: list[RenderFrame] = []
    __length: int = 0
    __curr_frame: int = 0

    def __init__(self, *items: RenderFrame):
        for item in items:
            self.add(item)

    def add(self, item):
        self.__queue.append(item)
        self.__length += 1

    def pop(self):
        if len(self) > 0:
            curr_frame: RenderFrame = self.__queue[self.__curr_frame]
            self.__curr_frame += 1
            self.__length -= 1

            if len(self) == 0:
                self.__curr_frame = 0
                self.__queue = []

            return curr_frame
        else:
            raise IndexError('This RenderQueue does not have any items.')
        
    def __len__(self):
        return self.__length
        
    def __add__(self, other):
        while len(other) > 0:
            self.add(other.pop())

        return self

def get_objects(scene: Scene) -> dict[str, Object]:
    ui_props = scene.ui_properties
    objects = {
        'camera':       ui_props.camera,
        'camera_track': ui_props.camera_track,
        'bin_cutter':   ui_props.bin_cutter,
        'bin':          ui_props.bin
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
    elif(objects['bin'] == None or objects['bin'].type != 'MESH'):
        objects['bin'] = None
        raise Exception('Invalid bin object. Please pick a mesh object.')
    
    # Constraint Validation
    try: 
        objects['camera'].constraints["Follow Path"].use_fixed_location = True
        objects['camera'].constraints["Follow Path"].use_curve_follow = True
        objects['camera'].constraints["Follow Path"].use_curve_radius = True
        objects['camera'].constraints["Follow Path"].target = objects['camera_track']
    except:
        raise Exception("Please add a \"Follow Path\" constraint onto the camera.")
    
    return objects
