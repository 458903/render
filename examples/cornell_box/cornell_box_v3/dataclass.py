import taichi as ti
from taichi.math import *


@ti.dataclass
class Ray:
    origin: vec3
    direction: vec3
    color: vec3


@ti.dataclass
class Material:
    albedo: vec3
    emission: vec3
    roughness: float
    metallic: float
    transmission: float
    ior: float


@ti.dataclass
class Transform:
    position: vec3
    rotation: vec3
    scale: vec3


@ti.dataclass
class SDFObject:
    distance: float
    transform: Transform
    material: Material


@ti.dataclass
class HitRecord:
    object: SDFObject
    position: vec3
    hit: bool


@ti.dataclass
class Camera:
    lookfrom: vec3
    lookat: vec3
    vup: vec3
    vfov: float
    aspect: float
    aperture: float
    focus: float
