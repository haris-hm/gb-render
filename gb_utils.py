import bpy
import os

from bpy.types import Scene, Object
from enum import Enum

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

    def __init__(self, scene: Scene, azimuth: int=0, elevation: int=0, focal_length: int=35, liquid_level:int=100):
        self.__scene = scene
        self.__azimuth = azimuth
        self.__elevation = elevation
        self.__focal_length = focal_length  
        self.__liquid_level = liquid_level

        self.__get_scene_objects()

    def setup_scene(self):
        bin_cutter_location = self.__grease.dimensions.z*(self.__liquid_level*.01)

        self.__camera.constraints["Follow Path"].offset_factor = self.__azimuth/360
        self.__camera_track.location.z += 1/self.__elevation if self.__elevation > 0 else 0
        self.__camera.data.lens = self.__focal_length
        self.__bin_cutter.location.z = bin_cutter_location

    def __get_scene_objects(self):
        objects = get_objects(self.__scene)
        self.__camera = objects['camera']
        self.__camera_track = objects['camera_track']
        self.__bin_cutter = objects['bin_cutter']
        self.__grease = objects['grease']

class RenderFrame():
    def __init__(self, root_path: str, file_name: str, scene: Scene, type: FrameType, scene_data: SceneData, width: int=1920, height: int=1080, samples: int=1024):
        self.__filepath = os.path.join(root_path, f'{file_name}_{type.value}.png')
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
        self.__curr_frame: int = 0
        for item in items:
            self.add(item)

    def add(self, item):
        self.__queue.append(item)
        self.__length += 1
        return self

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
        
    def copy(self):
        copy = RenderQueue()
        for i in self.__queue:
            copy.add(i)
        return copy
        
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
