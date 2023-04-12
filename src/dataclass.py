import taichi as ti
from taichi.math import vec3, mat3


@ti.dataclass
class Ray:
    origin: vec3
    direction: vec3
    color: vec3
    depth: int


@ti.dataclass
class Material:
    albedo: vec3        # 材质颜色（反照率），反照率可以粗略表示为光线入射物体表面后，物体出射光的颜色与物体入射光之比
    emission: vec3      # 自发光
    roughness: float    # 粗糙度
    metallic: float     # 金属度
    transmission: float # 透明度
    ior: float          # 折射率


@ti.dataclass
class Transform:
    position: vec3
    rotation: vec3
    scale: vec3
    matrix: mat3


@ti.dataclass
class SDFObject:
    type: int
    transform: Transform
    material: Material


@ti.dataclass
class Camera:
    lookfrom: vec3
    lookat: vec3
    vup: vec3
    vfov: float      # 纵向视野
    aspect: float    # 传感器长宽比
    aperture: float  # 光圈大小
    focus: float
