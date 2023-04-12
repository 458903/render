import taichi as ti
from taichi.math import vec3, mix, sqrt, normalize, dot


from .config import ENV_IOR, MIN_DIS
from .dataclass import Ray, SDFObject
from .util import random_in_unit_sphere, sample_float
from .scene import calc_normal

'''
========================================基于物理的渲染=====================================================================
计算 Fresnel-Schlick 近似模型中的反射率。Fresnel-Schlick 近似模型用于计算光线与表面相交时的反射率，
NoI 是入射光线与法向量的点积，F0 是反射率的基础值。
'''
@ti.func
def fresnel_schlick(NoI: float, F0: float) -> float:
    return mix(pow(abs(1.0 + NoI), 5.0), 1.0, F0) # mix 函数将 pow(abs(1.0 + NoI), 5.0) 和 1.0 之间进行插值
    # pow(abs(1.0 + NoI), 5.0) 的计算是根据 Fresnel-Schlick 近似模型的公式得出的。最终的反射率是通过将插值结果和 F0 相乘得到的
'''
一个半球采样函数
'''
@ti.func
def hemispheric_sampling(normal: vec3) -> vec3: # 输入是一个三维向量normal，代表表面法线的方向
    vector = random_in_unit_sphere() # 在单位球内随机生成一个点，然后将其与法线相加，再通过对其进行归一化来得到半球上的一个随机方向
    return normalize(normal + vector) # 输出是一个三维向量，代表半球上的一个随机方向
'''
光线与物体表面的相互作用。其中，输入为一个光线对象（Ray）和一个物体对象（SDFObject），输出为一个光线对象
'''
@ti.func
def ray_surface_interaction(ray: Ray, object: SDFObject) -> Ray:
    albedo = object.material.albedo # 从物体对象中获取其材质属性（如漫反射系数，粗糙度等）
    roughness = object.material.roughness
    metallic = object.material.metallic
    transmission = object.material.transmission
    ior = object.material.ior

    normal = calc_normal(object, ray.origin) # 计算出表面法线向量（normal）
    outer = dot(ray.direction, normal) < 0.0 # 如果光线是从物体表面外部射入，则将法线向量反向
    normal *= 1.0 if outer else -1.0

    alpha = roughness * roughness # 计算材质的粗糙度参数alpha，生成一个在表面法线周围的半球上的样本向量hemispheric_sample
    hemispheric_sample = hemispheric_sampling(normal)
    # alpha和表面法线向量的混合，生成一个相对更平滑的粗糙度样本向量roughness_sample
    roughness_sample = normalize(mix(normal, hemispheric_sample, alpha))

    N = roughness_sample
    I = ray.direction
    NoI = dot(N, I) # 计算反射光线（ray.direction）和入射光线（I）的夹角NoI

    eta = ENV_IOR / ior if outer else ior / ENV_IOR # 外部/内部反射系数eta
    k = 1.0 - eta * eta * (1.0 - NoI * NoI) # 反射率k,
    F0 = 2.0 * (eta - 1.0) / (eta + 1.0)
    F = fresnel_schlick(NoI, F0*F0) # 反射系数F
    # ToDo: 优化代码以去除if语句的判断分支
    if sample_float() < F + metallic or k < 0.0: # 如果k小于0，则说明光线完全折射
        ray.direction = I - 2.0 * NoI * N
        outer = dot(ray.direction, normal) < 0.0
        ray.direction *= (-1.0 if outer else 1.0)
    elif sample_float() < transmission:
        ray.direction = eta * I - (sqrt(k) + eta * NoI) * N
    else:
        ray.direction = hemispheric_sample
    ray.color *= albedo
    outer = dot(ray.direction, normal) < 0.0 # 计算光线的颜色并根据表面法线调整光线的原点位置，使光线能够在物体表面上正确反射
    ray.origin += normal * MIN_DIS * (-1.0 if outer else 1.0)
    return ray
