"""
================================================================================
"Секреты фундамента с синьорой Лисой" - Animated 3D Background
Blender 5.3.0 Compatible Script
================================================================================

HOW TO RUN:
1. Open Blender 5.3.0
2. Switch to the "Scripting" workspace (top tab)
3. Click "New" to create a new text block
4. Paste this entire script
5. Click "Run Script" (or press Alt+P)
6. The scene will be generated automatically
7. Save the file as "foundation_background.blend"

The script creates:
- Full 1080x1920, 30fps, 1800 frame animation
- 5 storyboard sections with smooth transitions
- All geometry, materials, lighting procedurally generated
- Organized collections: ENVIRONMENT, ARCHITECTURE, FOUNDATION_DEMO,
  PRESSURE_DEMO, GRAPHICS, LIGHTING, CAMERA

================================================================================
"""

import bpy
import math
import random
from mathutils import Vector, Euler

# =============================================================================
# SECTION 0: SCENE INITIALIZATION & CLEANUP
# =============================================================================

def clear_scene():
    """Remove all existing objects and data from the scene."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    
    # Clear orphan data
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)
    for block in bpy.data.materials:
        if block.users == 0:
            bpy.data.materials.remove(block)
    for block in bpy.data.lights:
        if block.users == 0:
            bpy.data.lights.remove(block)
    for block in bpy.data.cameras:
        if block.users == 0:
            bpy.data.cameras.remove(block)


def setup_render_settings():
    """Configure render resolution, frame rate, and frame range."""
    scene = bpy.context.scene
    scene.render.resolution_x = 1080
    scene.render.resolution_y = 1920
    scene.render.resolution_percentage = 100
    scene.render.fps = 30
    scene.frame_start = 1
    scene.frame_end = 1800
    
    # Use EEVEE for fast rendering
    scene.render.engine = 'BLENDER_EEVEE_NEXT'
    
    # Color management - bright and warm
    scene.view_settings.view_transform = 'Standard'
    scene.view_settings.look = 'None'
    scene.view_settings.exposure = 0.0
    scene.view_settings.gamma = 1.0
    
    # Output settings
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGB'
    scene.render.film_transparent = False


def create_collections():
    """Create and return organized collections."""
    collections = {}
    names = ['ENVIRONMENT', 'ARCHITECTURE', 'FOUNDATION_DEMO', 
             'PRESSURE_DEMO', 'GRAPHICS', 'LIGHTING', 'CAMERA']
    
    for name in names:
        col = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(col)
        collections[name] = col
    
    return collections


def link_to_collection(obj, collection):
    """Link object to a specific collection, removing from others."""
    for col in obj.users_collection:
        col.objects.unlink(obj)
    collection.objects.link(obj)
    return obj

# =============================================================================
# SECTION 1: MATERIALS
# =============================================================================

def create_material(name, color, roughness=0.7, metallic=0.0, emission=None):
    """Create a simple Principled BSDF material."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (300, 0)
    
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic
    
    if emission:
        bsdf.inputs['Emission Color'].default_value = (*emission, 1.0)
        bsdf.inputs['Emission Strength'].default_value = 1.0
    
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    return mat


def create_all_materials():
    """Create all materials used in the scene."""
    mats = {}
    
    # Palette: #FFF4E0, #1F4E79, #FF8A3D, #3DAA8C, #222222
    mats['warm_bg'] = create_material('MAT_WarmBackground', (1.0, 0.957, 0.878), 0.9)
    mats['deep_blue'] = create_material('MAT_DeepBlue', (0.122, 0.306, 0.475), 0.6)
    mats['orange'] = create_material('MAT_Orange', (1.0, 0.541, 0.239), 0.5)
    mats['teal'] = create_material('MAT_Teal', (0.239, 0.667, 0.549), 0.5)
    mats['dark'] = create_material('MAT_Dark', (0.133, 0.133, 0.133), 0.7)
    
    # Concrete and soil
    mats['concrete'] = create_material('MAT_Concrete', (0.72, 0.70, 0.67), 0.8)
    mats['concrete_light'] = create_material('MAT_ConcreteLight', (0.82, 0.80, 0.77), 0.85)
    mats['soil'] = create_material('MAT_Soil', (0.45, 0.35, 0.25), 0.95)
    mats['soil_light'] = create_material('MAT_SoilLight', (0.55, 0.45, 0.33), 0.95)
    mats['sand'] = create_material('MAT_Sand', (0.93, 0.84, 0.65), 0.95)
    mats['snow'] = create_material('MAT_Snow', (0.95, 0.96, 0.98), 0.7)
    
    # Building
    mats['building_main'] = create_material('MAT_BuildingMain', (0.88, 0.85, 0.80), 0.75)
    mats['building_trim'] = create_material('MAT_BuildingTrim', (0.122, 0.306, 0.475), 0.6)
    mats['window'] = create_material('MAT_Window', (0.4, 0.55, 0.65), 0.3, 0.2)
    mats['window_lit'] = create_material('MAT_WindowLit', (1.0, 0.9, 0.7), 0.4, 
                                          emission=(1.0, 0.85, 0.5))
    
    # Blueprint
    mats['blueprint_bg'] = create_material('MAT_BlueprintBg', (0.95, 0.94, 0.92), 0.95)
    mats['blueprint_line'] = create_material('MAT_BlueprintLine', (0.122, 0.306, 0.475), 0.9)
    
    # Flashcard
    mats['card_bg'] = create_material('MAT_CardBg', (1.0, 0.957, 0.878), 0.85)
    mats['card_accent_blue'] = create_material('MAT_CardBlue', (0.122, 0.306, 0.475), 0.5)
    mats['card_accent_orange'] = create_material('MAT_CardOrange', (1.0, 0.541, 0.239), 0.5)
    
    # Shoe
    mats['shoe'] = create_material('MAT_Shoe', (0.15, 0.12, 0.10), 0.4)
    mats['shoe_sole'] = create_material('MAT_ShoeSole', (0.08, 0.06, 0.05), 0.6)
    
    # Ski
    mats['ski'] = create_material('MAT_Ski', (0.9, 0.15, 0.1), 0.3)
    
    return mats

# =============================================================================
# SECTION 2: CAMERA & LIGHTING
# =============================================================================

def create_camera(collections):
    """Create the main camera for vertical 9:16 composition."""
    cam_data = bpy.data.cameras.new('CAM_Main')
    cam_data.lens = 35
    cam_data.sensor_width = 36
    cam_obj = bpy.data.objects.new('CAM_Main', cam_data)
    collections['CAMERA'].objects.link(cam_obj)
    
    # Position: slightly elevated three-quarter view
    # Looking at central area around z=2, leaving foreground clear
    cam_obj.location = (8.0, -14.0, 7.0)
    cam_obj.rotation_euler = Euler((
        math.radians(72),  # tilt down
        0,
        math.radians(30)   # rotate to look at scene center
    ), 'XYZ')
    
    bpy.context.scene.camera = cam_obj
    return cam_obj


def create_lighting(collections):
    """Create soft studio-style lighting."""
    
    # Main area light - key light
    key_data = bpy.data.lights.new('LIGHT_Key', type='AREA')
    key_data.energy = 800
    key_data.size = 8.0
    key_data.color = (1.0, 0.97, 0.92)
    key_obj = bpy.data.objects.new('LIGHT_Key', key_data)
    key_obj.location = (-6, -8, 12)
    key_obj.rotation_euler = Euler((math.radians(35), math.radians(-15), math.radians(-30)), 'XYZ')
    collections['LIGHTING'].objects.link(key_obj)
    
    # Fill light - soft
    fill_data = bpy.data.lights.new('LIGHT_Fill', type='AREA')
    fill_data.energy = 300
    fill_data.size = 10.0
    fill_data.color = (0.9, 0.95, 1.0)
    fill_obj = bpy.data.objects.new('LIGHT_Fill', fill_data)
    fill_obj.location = (8, -5, 8)
    fill_obj.rotation_euler = Euler((math.radians(50), math.radians(20), math.radians(40)), 'XYZ')
    collections['LIGHTING'].objects.link(fill_obj)
    
    # Ambient world lighting
    world = bpy.context.scene.world
    if world is None:
        world = bpy.data.worlds.new('World')
        bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get('Background')
    if bg:
        bg.inputs['Color'].default_value = (0.98, 0.96, 0.94, 1.0)
        bg.inputs['Strength'].default_value = 0.6


# =============================================================================
# SECTION 3: UTILITY FUNCTIONS
# =============================================================================

def create_box(name, size, location, material, collection, parent=None):
    """Create a box mesh object."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (size[0]/2, size[1]/2, size[2]/2)
    bpy.ops.object.transform_apply(scale=True)
    
    if material:
        obj.data.materials.append(material)
    
    link_to_collection(obj, collection)
    
    if parent:
        obj.parent = parent
    
    return obj


def create_cylinder(name, radius, depth, location, material, collection, parent=None):
    """Create a cylinder mesh object."""
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, location=location)
    obj = bpy.context.active_object
    obj.name = name
    
    if material:
        obj.data.materials.append(material)
    
    link_to_collection(obj, collection)
    
    if parent:
        obj.parent = parent
    
    return obj


def create_plane(name, size, location, material, collection, rotation=(0,0,0)):
    """Create a plane mesh object."""
    bpy.ops.mesh.primitive_plane_add(size=1, location=location, rotation=rotation)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (size[0]/2, size[1]/2, 1)
    bpy.ops.object.transform_apply(scale=True)
    
    if material:
        obj.data.materials.append(material)
    
    link_to_collection(obj, collection)
    return obj


def set_animation_keyframe(obj, frame, location=None, rotation=None, scale=None, 
                           interpolation='BEZIER'):
    """Set keyframes with smooth interpolation."""
    if location is not None:
        obj.location = location
        obj.keyframe_insert(data_path='location', frame=frame)
    if rotation is not None:
        obj.rotation_euler = rotation
        obj.keyframe_insert(data_path='rotation_euler', frame=frame)
    if scale is not None:
        obj.scale = scale
        obj.keyframe_insert(data_path='scale', frame=frame)
    
    # Set interpolation for smooth motion
    if obj.animation_data and obj.animation_data.action:
        for fcurve in obj.animation_data.action.fcurves:
            for kp in fcurve.keyframe_points:
                kp.interpolation = interpolation
                kp.easing = 'AUTO'


def animate_fade_in(obj, start_frame, end_frame):
    """Animate object fading in via scale."""
    obj.scale = (0.001, 0.001, 0.001)
    obj.keyframe_insert(data_path='scale', frame=start_frame)
    obj.scale = (1.0, 1.0, 1.0)
    obj.keyframe_insert(data_path='scale', frame=end_frame)
    _smooth_fcurves(obj)


def animate_fade_out(obj, start_frame, end_frame):
    """Animate object fading out via scale."""
    obj.scale = (1.0, 1.0, 1.0)
    obj.keyframe_insert(data_path='scale', frame=start_frame)
    obj.scale = (0.001, 0.001, 0.001)
    obj.keyframe_insert(data_path='scale', frame=end_frame)
    _smooth_fcurves(obj)


def _smooth_fcurves(obj):
    """Apply bezier interpolation to all fcurves."""
    if obj.animation_data and obj.animation_data.action:
        for fcurve in obj.animation_data.action.fcurves:
            for kp in fcurve.keyframe_points:
                kp.interpolation = 'BEZIER'
                kp.easing = 'AUTO'

# =============================================================================
# SECTION 4: ENVIRONMENT
# =============================================================================

def create_environment(collections, mats):
    """Create ground plane and background elements."""
    
    # Main ground plane - large, warm light
    ground = create_plane('ENV_Ground', (60, 60), (0, 0, 0), 
                          mats['warm_bg'], collections['ENVIRONMENT'])
    
    # Subtle soil layer visible on sides
    soil_side = create_box('ENV_SoilLayer', (40, 40, 0.5), (0, 0, -0.25),
                           mats['soil'], collections['ENVIRONMENT'])
    
    # Background gradient plane (vertical backdrop)
    backdrop = create_plane('ENV_Backdrop', (40, 30), (0, 15, 12),
                            mats['warm_bg'], collections['ENVIRONMENT'],
                            rotation=(math.radians(90), 0, 0))
    
    return ground

# =============================================================================
# SECTION 5: ARCHITECTURE - MAIN BUILDING (0:00-0:05)
# =============================================================================

def create_main_building(collections, mats):
    """Create the monumental stylized building for the intro."""
    
    building_root = bpy.data.objects.new('ARCH_BuildingRoot', None)
    collections['ARCHITECTURE'].objects.link(building_root)
    building_root.location = (0, 6, 0)
    
    # Main tower - tall rectangular volume
    tower = create_box('ARCH_MainTower', (4.0, 3.0, 18.0), (0, 0, 9.0),
                       mats['building_main'], collections['ARCHITECTURE'],
                       parent=building_root)
    
    # Facade divisions - vertical strips
    for i in range(5):
        x = -1.6 + i * 0.8
        strip = create_box(f'ARCH_FacadeStrip_{i}', (0.15, 0.1, 18.0), 
                          (x, 1.55, 9.0), mats['building_trim'],
                          collections['ARCHITECTURE'], parent=building_root)
    
    # Horizontal floor lines
    for i in range(9):
        z = 1.0 + i * 2.0
        floor_line = create_box(f'ARCH_FloorLine_{i}', (4.1, 0.1, 0.08),
                               (0, 1.55, z), mats['building_trim'],
                               collections['ARCHITECTURE'], parent=building_root)
    
    # Windows - repeating pattern
    window_index = 0
    for floor in range(8):
        for col_idx in range(4):
            x = -1.2 + col_idx * 0.8
            z = 1.8 + floor * 2.0
            mat = mats['window_lit'] if (floor + col_idx) % 3 == 0 else mats['window']
            win = create_box(f'ARCH_Window_{window_index}', (0.45, 0.1, 0.7),
                            (x, 1.56, z), mat,
                            collections['ARCHITECTURE'], parent=building_root)
            window_index += 1
    
    # Roof cap
    roof = create_box('ARCH_RoofCap', (4.4, 3.4, 0.4), (0, 0, 18.2),
                     mats['building_trim'], collections['ARCHITECTURE'],
                     parent=building_root)
    
    # Building base - wider foundation visible
    base = create_box('ARCH_BuildingBase', (5.0, 4.0, 1.0), (0, 0, 0.5),
                     mats['concrete'], collections['ARCHITECTURE'],
                     parent=building_root)
    
    # Animate building slight scale to show weight/monumentality
    set_animation_keyframe(building_root, 1, scale=(1,1,1))
    set_animation_keyframe(building_root, 150, scale=(1,1,1))
    
    return building_root

# =============================================================================
# SECTION 6: PRESSURE DEMO (0:05-0:20)
# =============================================================================

def create_pressure_demo(collections, mats):
    """Create the pressure demonstration: sand with shoe heel, then snow with skis."""
    
    root = bpy.data.objects.new('PRESSURE_Root', None)
    collections['PRESSURE_DEMO'].objects.link(root)
    root.location = (0, -4, 0)  # In front, visible area
    
    # Initially hidden
    root.scale = (0, 0, 0)
    
    # --- SAND SECTION ---
    sand_group = bpy.data.objects.new('PRESSURE_SandGroup', None)
    collections['PRESSURE_DEMO'].objects.link(sand_group)
    sand_group.parent = root
    
    # Sand surface
    sand = create_box('PRESSURE_Sand', (6, 4, 0.3), (0, 0, 0.15),
                     mats['sand'], collections['PRESSURE_DEMO'], parent=sand_group)
    
    # Sand indentation (appears when heel presses)
    indent = create_box('PRESSURE_SandIndent', (0.3, 0.3, 0.15), (0, 0, 0.1),
                       mats['soil_light'], collections['PRESSURE_DEMO'], parent=sand_group)
    indent.scale = (0, 0, 0)
    indent.keyframe_insert(data_path='scale', frame=1)
    indent.scale = (0, 0, 0)
    indent.keyframe_insert(data_path='scale', frame=260)
    indent.scale = (1, 1, 1)
    indent.keyframe_insert(data_path='scale', frame=320)
    _smooth_fcurves(indent)
    
    # Elegant shoe heel
    heel_group = bpy.data.objects.new('PRESSURE_HeelGroup', None)
    collections['PRESSURE_DEMO'].objects.link(heel_group)
    heel_group.parent = sand_group
    
    heel = create_cylinder('PRESSURE_Heel', 0.08, 0.6, (0, 0, 0.7),
                          mats['shoe'], collections['PRESSURE_DEMO'], parent=heel_group)
    heel.rotation_euler = Euler((0, 0, 0))
    
    shoe_body = create_box('PRESSURE_ShoeBody', (0.5, 0.25, 0.15), (0.15, 0, 0.95),
                          mats['shoe'], collections['PRESSURE_DEMO'], parent=heel_group)
    shoe_sole = create_box('PRESSURE_ShoeSole', (0.5, 0.25, 0.04), (0.15, 0, 0.87),
                          mats['shoe_sole'], collections['PRESSURE_DEMO'], parent=heel_group)
    
    # Animate heel pressing down
    heel_group.location = (0, 0, 1.5)
    heel_group.keyframe_insert(data_path='location', frame=200)
    heel_group.location = (0, 0, 0.3)  # sink into sand
    heel_group.keyframe_insert(data_path='location', frame=300)
    heel_group.location = (0, 0, 1.5)  # lift back
    heel_group.keyframe_insert(data_path='location', frame=400)
    _smooth_fcurves(heel_group)
    
    # --- SNOW SECTION ---
    snow_group = bpy.data.objects.new('PRESSURE_SnowGroup', None)
    collections['PRESSURE_DEMO'].objects.link(snow_group)
    snow_group.parent = root
    snow_group.location = (0, -6, 0)
    snow_group.scale = (0, 0, 0)
    
    # Snow surface
    snow = create_box('PRESSURE_Snow', (6, 4, 0.3), (0, 0, 0.15),
                     mats['snow'], collections['PRESSURE_DEMO'], parent=snow_group)
    
    # Skis
    for side in [-1, 1]:
        ski = create_box(f'PRESSURE_Ski_{side}', (0.12, 2.5, 0.06), 
                        (side * 0.25, 0, 0.33),
                        mats['ski'], collections['PRESSURE_DEMO'], parent=snow_group)
    
    # Animate skis gliding over snow
    for side in [-1, 1]:
        ski = bpy.data.objects[f'PRESSURE_Ski_{side}']
        ski.location = (side * 0.25, -2.5, 0.33)
        ski.keyframe_insert(data_path='location', frame=500)
        ski.location = (side * 0.25, 2.5, 0.33)
        ski.keyframe_insert(data_path='location', frame=650)
        _smooth_fcurves(ski)
    
    # --- WIDE VS NARROW CONTACT COMPARISON ---
    compare_group = bpy.data.objects.new('PRESSURE_CompareGroup', None)
    collections['PRESSURE_DEMO'].objects.link(compare_group)
    compare_group.parent = root
    compare_group.location = (0, -10, 0)
    compare_group.scale = (0, 0, 0)
    
    # Narrow contact indicator
    narrow = create_box('PRESSURE_NarrowContact', (0.15, 0.15, 0.5), (-1.5, 0, 0.25),
                       mats['orange'], collections['PRESSURE_DEMO'], parent=compare_group)
    narrow_label = create_box('PRESSURE_NarrowBar', (0.15, 0.8, 0.1), (-1.5, 0, 0.6),
                             mats['orange'], collections['PRESSURE_DEMO'], parent=compare_group)
    
    # Wide contact indicator
    wide = create_box('PRESSURE_WideContact', (1.0, 1.0, 0.15), (1.5, 0, 0.15),
                     mats['teal'], collections['PRESSURE_DEMO'], parent=compare_group)
    wide_label = create_box('PRESSURE_WideBar', (1.5, 0.8, 0.1), (1.5, 0, 0.4),
                           mats['teal'], collections['PRESSURE_DEMO'], parent=compare_group)
    
    # Animate sections appearing
    # Sand appears
    root.scale = (0, 0, 0)
    root.keyframe_insert(data_path='scale', frame=160)
    root.scale = (1, 1, 1)
    root.keyframe_insert(data_path='scale', frame=200)
    
    # Snow appears
    snow_group.scale = (0, 0, 0)
    snow_group.keyframe_insert(data_path='scale', frame=380)
    snow_group.scale = (1, 1, 1)
    snow_group.keyframe_insert(data_path='scale', frame=420)
    
    # Compare appears
    compare_group.scale = (0, 0, 0)
    compare_group.keyframe_insert(data_path='scale', frame=480)
    compare_group.scale = (1, 1, 1)
    compare_group.keyframe_insert(data_path='scale', frame=540)
    
    # Fade out everything by frame 720 (before foundation demo)
    root.scale = (1, 1, 1)
    root.keyframe_insert(data_path='scale', frame=680)
    root.scale = (0, 0, 0)
    root.keyframe_insert(data_path='scale', frame=720)
    _smooth_fcurves(root)
    
    return root

# =============================================================================
# SECTION 7: FOUNDATION DEMO (0:20-0:40)
# =============================================================================

def create_foundation_demo(collections, mats):
    """Create the three foundation types with cutaway soil visualization."""
    
    root = bpy.data.objects.new('FOUNDATION_Root', None)
    collections['FOUNDATION_DEMO'].objects.link(root)
    root.location = (0, -4, 0)
    root.scale = (0, 0, 0)
    
    # --- CUTAWAY SOIL ---
    soil_block = create_box('FOUNDATION_SoilBlock', (8, 5, 3), (0, 0, -1.5),
                           mats['soil'], collections['FOUNDATION_DEMO'], parent=root)
    
    # Front face cutaway (slightly lighter)
    soil_face = create_plane('FOUNDATION_SoilFace', (8, 5), (0, -2.5, -1.5),
                            mats['soil_light'], collections['FOUNDATION_DEMO'],
                            rotation=(math.radians(90), 0, 0))
    soil_face.parent = root
    
    # Ground surface line
    ground_line = create_box('FOUNDATION_GroundLine', (8, 0.1, 0.05), (0, -2.5, 0.02),
                            mats['dark'], collections['FOUNDATION_DEMO'], parent=root)
    
    # Building on top (simplified)
    building_demo = create_box('FOUNDATION_BuildingDemo', (5, 3, 2.5), (0, 0, 1.25),
                              mats['building_main'], collections['FOUNDATION_DEMO'],
                              parent=root)
    
    # --- STRIP FOUNDATION ---
    strip_group = bpy.data.objects.new('FOUNDATION_StripGroup', None)
    collections['FOUNDATION_DEMO'].objects.link(strip_group)
    strip_group.parent = root
    strip_group.scale = (0, 0, 0)
    
    # Strip strips under walls
    strip_positions = [
        (-2.0, -1.2), (-2.0, 1.2),  # left wall
        (2.0, -1.2), (2.0, 1.2),    # right wall
        (-2.0, 0), (2.0, 0),        # middle
        (0, -1.2), (0, 1.2),        # front/back
    ]
    for i, (x, y) in enumerate(strip_positions):
        strip = create_box(f'FOUNDATION_Strip_{i}', (0.6, 0.6, 1.2), (x, y, -0.6),
                          mats['concrete'], collections['FOUNDATION_DEMO'],
                          parent=strip_group)
        # Outline
        outline = create_box(f'FOUNDATION_StripOutline_{i}', (0.65, 0.65, 0.05),
                            (x, y, 0.02), mats['orange'],
                            collections['FOUNDATION_DEMO'], parent=strip_group)
    
    # --- SLAB FOUNDATION ---
    slab_group = bpy.data.objects.new('FOUNDATION_SlabGroup', None)
    collections['FOUNDATION_DEMO'].objects.link(slab_group)
    slab_group.parent = root
    slab_group.scale = (0, 0, 0)
    
    slab = create_box('FOUNDATION_Slab', (4.5, 2.8, 0.5), (0, 0, -0.25),
                     mats['concrete'], collections['FOUNDATION_DEMO'], parent=slab_group)
    slab_outline = create_box('FOUNDATION_SlabOutline', (4.6, 2.9, 0.06), (0, 0, 0.02),
                             mats['orange'], collections['FOUNDATION_DEMO'], parent=slab_group)
    
    # --- PILE FOUNDATION ---
    pile_group = bpy.data.objects.new('FOUNDATION_PileGroup', None)
    collections['FOUNDATION_DEMO'].objects.link(pile_group)
    pile_group.parent = root
    pile_group.scale = (0, 0, 0)
    
    # Horizontal cap
    pile_cap = create_box('FOUNDATION_PileCap', (4.5, 2.8, 0.3), (0, 0, -0.15),
                         mats['concrete'], collections['FOUNDATION_DEMO'], parent=pile_group)
    
    # Vertical piles
    pile_positions = [
        (-1.8, -1.0), (1.8, -1.0), (-1.8, 1.0), (1.8, 1.0),
        (0, -1.0), (0, 1.0), (-1.8, 0), (1.8, 0), (0, 0)
    ]
    for i, (x, y) in enumerate(pile_positions):
        pile = create_cylinder(f'FOUNDATION_Pile_{i}', 0.15, 2.5, (x, y, -1.5),
                              mats['concrete'], collections['FOUNDATION_DEMO'],
                              parent=pile_group)
        # Pile outline
        pile_outline = create_cylinder(f'FOUNDATION_PileOutline_{i}', 0.17, 0.06, 
                                      (x, y, -0.3), mats['orange'],
                                      collections['FOUNDATION_DEMO'], parent=pile_group)
    
    # --- ANIMATION TIMELINE ---
    # Root appears at frame 660 (after pressure demo)
    root.scale = (0, 0, 0)
    root.keyframe_insert(data_path='scale', frame=640)
    root.scale = (1, 1, 1)
    root.keyframe_insert(data_path='scale', frame=680)
    
    # Strip foundation appears (frames 700-750)
    strip_group.scale = (0, 0, 0)
    strip_group.keyframe_insert(data_path='scale', frame=700)
    strip_group.scale = (1, 1, 1)
    strip_group.keyframe_insert(data_path='scale', frame=760)
    
    # Strip fades, slab appears (frames 880-940)
    strip_group.scale = (1, 1, 1)
    strip_group.keyframe_insert(data_path='scale', frame=860)
    strip_group.scale = (0, 0, 0)
    strip_group.keyframe_insert(data_path='scale', frame=900)
    
    slab_group.scale = (0, 0, 0)
    slab_group.keyframe_insert(data_path='scale', frame=900)
    slab_group.scale = (1, 1, 1)
    slab_group.keyframe_insert(data_path='scale', frame=960)
    
    # Slab fades, piles appear (frames 1020-1080)
    slab_group.scale = (1, 1, 1)
    slab_group.keyframe_insert(data_path='scale', frame=1000)
    slab_group.scale = (0, 0, 0)
    slab_group.keyframe_insert(data_path='scale', frame=1040)
    
    pile_group.scale = (0, 0, 0)
    pile_group.keyframe_insert(data_path='scale', frame=1040)
    pile_group.scale = (1, 1, 1)
    pile_group.keyframe_insert(data_path='scale', frame=1100)
    
    # Animate piles growing from ground
    for i, (x, y) in enumerate(pile_positions):
        pile = bpy.data.objects[f'FOUNDATION_Pile_{i}']
        pile.scale = (1, 1, 0.1)
        pile.keyframe_insert(data_path='scale', frame=1060 + i * 10)
        pile.scale = (1, 1, 1)
        pile.keyframe_insert(data_path='scale', frame=1120 + i * 10)
        _smooth_fcurves(pile)
    
    # Fade out foundation demo by frame 1300
    root.scale = (1, 1, 1)
    root.keyframe_insert(data_path='scale', frame=1260)
    root.scale = (0, 0, 0)
    root.keyframe_insert(data_path='scale', frame=1300)
    _smooth_fcurves(root)
    
    return root

# =============================================================================
# SECTION 8: GRAPHICS - FLASHCARD & TELEGRAM (0:40-0:55)
# =============================================================================

def create_flashcard(collections, mats):
    """Create floating educational flashcard with Telegram-inspired symbol."""
    
    root = bpy.data.objects.new('GRAPHICS_FlashcardRoot', None)
    collections['GRAPHICS'].objects.link(root)
    root.location = (3, -6, 4)
    root.rotation_euler = Euler((math.radians(-10), math.radians(10), math.radians(-15)), 'XYZ')
    
    # Card body
    card = create_box('GRAPHICS_Flashcard', (2.0, 3.0, 0.1), (0, 0, 0),
                     mats['card_bg'], collections['GRAPHICS'], parent=root)
    
    # Card border accent
    border_top = create_box('GRAPHICS_CardBorderTop', (2.1, 0.15, 0.12), (0, 1.45, 0),
                           mats['card_accent_blue'], collections['GRAPHICS'], parent=root)
    border_bottom = create_box('GRAPHICS_CardBorderBottom', (2.1, 0.15, 0.12), (0, -1.45, 0),
                              mats['card_accent_orange'], collections['GRAPHICS'], parent=root)
    
    # Color accent blocks (placeholder for text areas)
    accent_block = create_box('GRAPHICS_CardAccentBlock', (1.8, 0.8, 0.05), (0, 0.7, 0.06),
                             mats['card_accent_blue'], collections['GRAPHICS'], parent=root)
    accent_block2 = create_box('GRAPHICS_CardAccentBlock2', (1.8, 1.2, 0.05), (0, -0.5, 0.06),
                               mats['warm_bg'], collections['GRAPHICS'], parent=root)
    
    # Telegram-inspired symbol (simplified paper plane shape)
    # Not reproducing copyrighted interface, just a simple geometric reference
    tg_group = bpy.data.objects.new('GRAPHICS_TelegramSymbol', None)
    collections['GRAPHICS'].objects.link(tg_group)
    tg_group.parent = root
    tg_group.location = (0, -1.8, 0.1)
    
    # Simple circular badge
    badge = create_cylinder('GRAPHICS_TelegramBadge', 0.25, 0.05, (0, 0, 0),
                           mats['card_accent_blue'], collections['GRAPHICS'], parent=tg_group)
    badge.rotation_euler = Euler((math.radians(90), 0, 0))
    
    # Arrow/plane shape (simplified)
    plane_body = create_box('GRAPHICS_PlaneBody', (0.3, 0.15, 0.03), (0, 0, 0.04),
                           mats['warm_bg'], collections['GRAPHICS'], parent=tg_group)
    plane_tail = create_box('GRAPHICS_PlaneTail', (0.15, 0.08, 0.03), (-0.12, 0.12, 0.04),
                           mats['warm_bg'], collections['GRAPHICS'], parent=tg_group)
    
    # --- ANIMATION ---
    # Card appears at frame 1320 (after foundation demo)
    root.scale = (0, 0, 0)
    root.keyframe_insert(data_path='scale', frame=1300)
    root.scale = (1, 1, 1)
    root.keyframe_insert(data_path='scale', frame=1360)
    
    # Gentle floating animation
    root.location = (3, -6, 4)
    root.keyframe_insert(data_path='location', frame=1400)
    root.location = (3, -6, 4.3)
    root.keyframe_insert(data_path='location', frame=1520)
    root.location = (3, -6, 4)
    root.keyframe_insert(data_path='location', frame=1640)
    root.location = (3, -6, 4.2)
    root.keyframe_insert(data_path='location', frame=1700)
    
    # Gentle rotation wobble
    root.rotation_euler = Euler((math.radians(-10), math.radians(10), math.radians(-15)), 'XYZ')
    root.keyframe_insert(data_path='rotation_euler', frame=1400)
    root.rotation_euler = Euler((math.radians(-8), math.radians(12), math.radians(-12)), 'XYZ')
    root.keyframe_insert(data_path='rotation_euler', frame=1550)
    root.rotation_euler = Euler((math.radians(-10), math.radians(10), math.radians(-15)), 'XYZ')
    root.keyframe_insert(data_path='rotation_euler', frame=1700)
    _smooth_fcurves(root)
    
    return root

# =============================================================================
# SECTION 9: BLUEPRINT ENVIRONMENT (0:55-1:00)
# =============================================================================

def create_blueprint(collections, mats):
    """Create stylized architectural blueprint environment for the outro."""
    
    root = bpy.data.objects.new('GRAPHICS_BlueprintRoot', None)
    collections['GRAPHICS'].objects.link(root)
    root.location = (0, 5, 0)
    root.scale = (0, 0, 0)
    
    # Blueprint background plane
    bp_bg = create_plane('GRAPHICS_BlueprintBg', (20, 15), (0, 0, 0),
                        mats['blueprint_bg'], collections['GRAPHICS'])
    bp_bg.parent = root
    bp_bg.rotation_euler = Euler((math.radians(90), 0, 0))
    
    # Building outline (blueprint lines)
    line_width = 0.08
    
    # Main building outline
    building_outline = []
    outline_points = [
        (-2, -2), (2, -2), (2, 2), (-2, 2), (-2, -2)  # rectangle
    ]
    for i in range(len(outline_points) - 1):
        x1, y1 = outline_points[i]
        x2, y2 = outline_points[i + 1]
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        dx, dy = x2 - x1, y2 - y1
        length = math.sqrt(dx**2 + dy**2)
        angle = math.atan2(dy, dx)
        
        line = create_box(f'GRAPHICS_BP_BuildingLine_{i}', (length, line_width, 0.02),
                         (cx, cy, 0.02), mats['blueprint_line'],
                         collections['GRAPHICS'], parent=root)
        line.rotation_euler = Euler((0, 0, angle))
    
    # Interior lines
    interior_lines = [
        ((-2, 0), (2, 0)),  # horizontal divider
        ((0, -2), (0, 2)),  # vertical divider
        ((-1, -1), (1, -1)),  # window row
        ((-1, 1), (1, 1)),
    ]
    for i, (p1, p2) in enumerate(interior_lines):
        x1, y1 = p1
        x2, y2 = p2
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        dx, dy = x2 - x1, y2 - y1
        length = math.sqrt(dx**2 + dy**2)
        angle = math.atan2(dy, dx)
        
        line = create_box(f'GRAPHICS_BP_InteriorLine_{i}', (length, line_width, 0.02),
                         (cx, cy, 0.03), mats['blueprint_line'],
                         collections['GRAPHICS'], parent=root)
        line.rotation_euler = Euler((0, 0, angle))
    
    # Foundation cross-section lines
    found_lines = [
        ((-2.5, -3), (2.5, -3)),  # ground line
        ((-2.5, -4), (2.5, -4)),  # foundation bottom
        ((-2, -3), (-2, -4)),     # left pile
        ((2, -3), (2, -4)),       # right pile
        ((0, -3), (0, -4)),       # center pile
    ]
    for i, (p1, p2) in enumerate(found_lines):
        x1, y1 = p1
        x2, y2 = p2
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        dx, dy = x2 - x1, y2 - y1
        length = math.sqrt(dx**2 + dy**2)
        angle = math.atan2(dy, dx)
        
        line = create_box(f'GRAPHICS_BP_FoundLine_{i}', (length, line_width, 0.02),
                         (cx, cy, 0.03), mats['blueprint_line'],
                         collections['GRAPHICS'], parent=root)
        line.rotation_euler = Euler((0, 0, angle))
    
    # Dimension markers (small ticks)
    dimension_positions = [(-2.5, -3), (2.5, -3), (-2.5, -4), (2.5, -4)]
    for i, (x, y) in enumerate(dimension_positions):
        tick = create_box(f'GRAPHICS_BP_Tick_{i}', (0.15, 0.02, 0.02), (x, y, 0.04),
                         mats['orange'], collections['GRAPHICS'], parent=root)
    
    # Decorative circles (technical drawing symbols)
    for i, (x, y) in enumerate([(-3, 2), (3, 2), (0, -5)]):
        circle = create_cylinder(f'GRAPHICS_BP_Circle_{i}', 0.2, 0.02, (x, y, 0.03),
                                mats['blueprint_line'], collections['GRAPHICS'],
                                parent=root)
        circle.rotation_euler = Euler((0, 0, 0))
    
    # --- ANIMATION ---
    # Blueprint fades in at frame 1650
    root.scale = (0, 0, 0)
    root.keyframe_insert(data_path='scale', frame=1630)
    root.scale = (1, 1, 1)
    root.keyframe_insert(data_path='scale', frame=1700)
    
    # Subtle drawing effect - animate lines scaling in sequence
    all_lines = [obj for obj in root.children if 'Line' in obj.name]
    for i, line in enumerate(all_lines):
        line.scale = (0, 1, 1)
        line.keyframe_insert(data_path='scale', frame=1660 + i * 8)
        line.scale = (1, 1, 1)
        line.keyframe_insert(data_path='scale', frame=1700 + i * 8)
        _smooth_fcurves(line)
    
    return root

# =============================================================================
# SECTION 10: MAIN BUILDING VISIBILITY ANIMATION
# =============================================================================

def animate_building_visibility(building_root):
    """Control when the main building is visible throughout the animation."""
    
    # Building visible during intro (0:00-0:05) and pressure demo intro
    building_root.scale = (1, 1, 1)
    building_root.keyframe_insert(data_path='scale', frame=1)
    building_root.keyframe_insert(data_path='scale', frame=150)
    
    # Building hides during pressure demo
    building_root.scale = (0, 0, 0)
    building_root.keyframe_insert(data_path='scale', frame=200)
    
    # Building reappears for foundation demo context
    building_root.scale = (0, 0, 0)
    building_root.keyframe_insert(data_path='scale', frame=640)
    building_root.scale = (0.6, 0.6, 0.6)  # smaller, background
    building_root.keyframe_insert(data_path='scale', frame=700)
    
    # Building hides during flashcard
    building_root.scale = (0.6, 0.6, 0.6)
    building_root.keyframe_insert(data_path='scale', frame=1260)
    building_root.scale = (0, 0, 0)
    building_root.keyframe_insert(data_path='scale', frame=1300)
    
    _smooth_fcurves(building_root)

# =============================================================================
# SECTION 11: GROUND VISIBILITY & TRANSITIONS
# =============================================================================

def animate_environment_transitions(ground, backdrop):
    """Animate environment elements across sections."""
    
    # Ground always visible but scale for emphasis
    ground.scale = (1, 1, 1)
    ground.keyframe_insert(data_path='scale', frame=1)
    ground.keyframe_insert(data_path='scale', frame=1800)
    
    # Backdrop subtle color shift
    backdrop.keyframe_insert(data_path='scale', frame=1)
    backdrop.keyframe_insert(data_path='scale', frame=1800)

# =============================================================================
# SECTION 12: MAIN EXECUTION
# =============================================================================

def main():
    """Main execution function."""
    
    print("=" * 60)
    print("Starting: Секреты фундамента с синьорой Лисой")
    print("Animated 3D Background Generation")
    print("=" * 60)
    
    # Step 1: Clear scene
    print("[1/12] Clearing scene...")
    clear_scene()
    
    # Step 2: Setup render
    print("[2/12] Setting up render settings...")
    setup_render_settings()
    
    # Step 3: Create collections
    print("[3/12] Creating collections...")
    collections = create_collections()
    
    # Step 4: Create materials
    print("[4/12] Creating materials...")
    mats = create_all_materials()
    
    # Step 5: Create camera
    print("[5/12] Creating camera...")
    cam = create_camera(collections)
    
    # Step 6: Create lighting
    print("[6/12] Creating lighting...")
    create_lighting(collections)
    
    # Step 7: Create environment
    print("[7/12] Creating environment...")
    ground = create_environment(collections, mats)
    
    # Step 8: Create main building
    print("[8/12] Creating main building...")
    building = create_main_building(collections, mats)
    animate_building_visibility(building)
    
    # Step 9: Create pressure demo
    print("[9/12] Creating pressure demo...")
    pressure = create_pressure_demo(collections, mats)
    
    # Step 10: Create foundation demo
    print("[10/12] Creating foundation demo...")
    foundation = create_foundation_demo(collections, mats)
    
    # Step 11: Create graphics
    print("[11/12] Creating graphics...")
    flashcard = create_flashcard(collections, mats)
    blueprint = create_blueprint(collections, mats)
    
    # Step 12: Animate environment
    print("[12/12] Finalizing animations...")
    
    # Set current frame to 1
    bpy.context.scene.frame_set(1)
    
    print("=" * 60)
    print("SCENE GENERATION COMPLETE!")
    print("=" * 60)
    print(f"Resolution: {bpy.context.scene.render.resolution_x}x{bpy.context.scene.render.resolution_y}")
    print(f"Frame rate: {bpy.context.scene.render.fps} FPS")
    print(f"Frame range: {bpy.context.scene.frame_start}-{bpy.context.scene.frame_end}")
    print(f"Total duration: {(bpy.context.scene.frame_end - bpy.context.scene.frame_start + 1) / bpy.context.scene.render.fps:.1f} seconds")
    print("=" * 60)
    print("\nCollections created:")
    for col in bpy.data.collections:
        count = len(col.objects)
        print(f"  - {col.name}: {count} objects")
    print("\nSave your file: File > Save As > foundation_background.blend")
    print("=" * 60)


# Run the script
if __name__ == "__main__":
    main()
