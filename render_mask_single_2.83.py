"""
blender render based on materials.
blender version: 2.83.
load 3d type: obj.
for singel objects.
"""
import bpy
import numpy as np
import os as os
import sys
import argparse
from math import radians
from mathutils import Vector, Matrix

# define opts
parser = argparse.ArgumentParser(description='Renders given obj file by rotation a camera around it.')
parser.add_argument('--views', type=int, default=30, help='number of views to be rendered')
parser.add_argument('--output_folder', type=str, default='/home/xiangyu/software', help='The path the output will be dumped to.')
parser.add_argument('--cam_mode', type=str, default='cycle', help='Mode of Camera.')
parser.add_argument('--obj_path', type=str, default='/home/xiangyu/models/obj_change/17d4c0f1b707e6dd19fb4103277a6b93/17d4c0f1b707e6dd19fb4103277a6b93.obj', help='Path to target obj file.')

argv = sys.argv[sys.argv.index("--") + 1:]
args = parser.parse_args(argv)


# clear original cube, light and camera.
bpy.data.objects['Cube'].select_set(True)
bpy.ops.object.delete()
bpy.data.objects['Light'].select_set(True)
bpy.ops.object.delete()


# read target obj files.
bpy.ops.import_scene.obj(filepath=args.obj_path)


# pre-process original obj(remove_doubles, edge_splits).
for object in bpy.context.scene.objects:
    if object.name in ['Camera', 'Light']:
        continue
    bpy.context.view_layer.objects.active = object
    # remove doubles.
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.remove_doubles()
    bpy.ops.object.mode_set(mode='OBJECT')
    # edge split.
    bpy.ops.object.modifier_add(type='EDGE_SPLIT')
    bpy.context.object.modifiers["EdgeSplit"].split_angle = 1.32645
    bpy.ops.object.modifier_apply(apply_as='DATA', modifier="EdgeSplit")


# choose for cycles rendering.
bpy.context.scene.render.engine = 'CYCLES'


# give different materials different channels.    
bpy.context.scene.view_layers["View Layer"].use_pass_material_index = True

bpy.context.object.active_material_index = 0
bpy.context.object.active_material.pass_index = 50
bpy.context.object.active_material_index = 1
bpy.context.object.active_material.pass_index = 100
bpy.context.object.active_material_index = 2
bpy.context.object.active_material.pass_index = 150

try:
    bpy.context.object.active_material_index = 3
    bpy.context.object.active_material.pass_index = 200
except:
    print("Only 3 materials!")


# change_nodes.
bpy.context.scene.use_nodes = True
tree = bpy.context.scene.node_tree
links = tree.links
for n in tree.nodes:
    tree.nodes.remove(n)

render_layers = tree.nodes.new('CompositorNodeRLayers')

math_node = tree.nodes.new(type='CompositorNodeMath')
math_node.operation = 'DIVIDE'
math_node.inputs[1].default_value = 255.0

output_node_img = tree.nodes.new(type='CompositorNodeOutputFile')
output_node_img.format.color_mode = 'RGB'
output_node_img.format.file_format = 'JPEG'
output_node_seg = tree.nodes.new(type='CompositorNodeOutputFile')
output_node_seg.format.color_mode = 'BW'

links.new(render_layers.outputs['Image'], output_node_img.inputs[0])
links.new(render_layers.outputs['IndexMA'], math_node.inputs[0])
links.new(math_node.outputs['Value'], output_node_seg.inputs[0])


# lights
lights = ['light_front', 'light_back', 'light_left', 'light_right', 'light_top', 'light_bottom']
lights_poses = np.array([[0, 0, 5], [0, 0, -5], [0, 5, 0], [0, -5, 0], [5, 0, 0], [-5, 0, 0]])
num_lights = len(lights)
for i in range(0, num_lights):
    light_data = bpy.data.lights.new(name=lights[i], type='POINT')
    light_data.energy = 10
    light_object = bpy.data.objects.new(name=lights[i], object_data=light_data)
    bpy.context.collection.objects.link(light_object)
    bpy.context.view_layer.objects.active = light_object
    light_object.location = lights_poses[i]


# Camera
def look_at(obj):
        #point = Vector(0,0,0)
        obj.rotation_mode = 'XYZ'
        loc_obj = obj.location
        #print(type(point))
        print(loc_obj)
        direction = -loc_obj
        # point the cameras '-Z' and use its 'Y' as up
        rot_quat = direction.to_track_quat('-Z', 'Y')
        obj.rotation_euler = rot_quat.to_euler()


cam = bpy.context.scene.objects['Camera']
cam.location = (1, 0, 0.6)
# cam.data.lens = focal_len
cam_constraint = cam.constraints.new(type='TRACK_TO')
cam_constraint.track_axis = 'TRACK_NEGATIVE_Z'
cam_constraint.up_axis = 'UP_Y'


# Camera_change.
def sample_sphere(num_samples, scale=1, use_half=False):
    phi = (np.sqrt(5) - 1.0) / 2.
    pos_list = []
    for n in range(1, num_samples+1):
        z = (2. * n - 1) / num_samples - 1.
        x = np.cos(2*np.pi*n*phi)*np.sqrt(1-z*z)
        y = np.sin(2*np.pi*n*phi)*np.sqrt(1-z*z)
        if use_half and z < 0:
            continue
        pos_list.append((x*scale, y*scale, z*scale))
    return np.array(pos_list)

def sample_cycle(num_samples):
    cam.location = (1, 0, 0.6)
    pos_list = []
    single = 360 / num_samples
    for n in range(1, num_samples+1):
        z = 0.6
        x = np.cos((n*15)*np.pi/180)
        y = -np.sin((n*15)*np.pi/180)
        pos_list.append((x, y, z))
    return np.array(pos_list)
    
def move_camera(cam_loc):
    cam.location = cam_loc
    look_at(cam)

if args.cam_mode == 'cycle':
    cam_loc = sample_cycle(args.views)
else:
    cam_loc = sample_sphere(args.views, scale=1, use_half=False)


# scene
bpy.context.scene.render.resolution_x = 600
bpy.context.scene.render.resolution_y = 600
bpy.context.scene.render.resolution_percentage = 100


# final render.
for output_node in [output_node_img, output_node_seg]:
    output_node.base_path = args.output_folder
for i, loc in enumerate(cam_loc):
    move_camera(loc)
    print('Rendering images.')
    bpy.context.scene.render.filepath = os.path.join('df', '_r_{0:03d}'.format(int(i * 10)))
    output_node_img.file_slots[0].path = bpy.context.scene.render.filepath + 'img'
    output_node_seg.file_slots[0].path = bpy.context.scene.render.filepath + 'img'
    bpy.ops.render.render(write_still=True)
