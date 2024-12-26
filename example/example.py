import numpy as np
import open3d as o3d
import grasp_pose_generator as gpg

# create a open3d box mesh
box = o3d.geometry.TriangleMesh.create_box(width=0.04, height=0.22, depth=0.06)
# sample points from the mesh
points = np.asarray(box.sample_points_uniformly(number_of_points=10000).points)
num_samples = 100
show_grasp = True
gripper_config_file = "gripper_params.cfg"
grasps = gpg.generate_grasps(points, num_samples, show_grasp, gripper_config_file)

pose_list = []
for grasp in grasps:
    pose = np.eye(4)
    pose[:3, 0] = grasp.get_grasp_approach()
    pose[:3, 1] = grasp.get_grasp_binormal()
    pose[:3, 2] = grasp.get_grasp_axis()
    pose[:3, 3] = grasp.get_grasp_bottom()
    pose_list.append(pose)