import taichi as ti
from taichi.math import vec3, mat3

'''
。输入转换矩阵将 RGB 颜色空间的值转换到 ACES 定义的 ACES2065-1 线性 RGB 颜色空间中。
'''
ACESInputMat = mat3(
    0.59719, 0.35458, 0.04823,
    0.07600, 0.90834, 0.01566,
    0.02840, 0.13383, 0.83777
)
'''
输出转换矩阵将 ACES 颜色空间中的值转换到最终显示设备的颜色空间中（例如 sRGB）。
'''
ACESOutputMat = mat3(
    +1.60475, -0.53108, -0.07367,
    -0.10208, +1.10813, -0.00605,
    -0.00327, -0.07276, +1.07602
)

'''
RRTAndODTFit 函数是 ACES 的 RRT (Reference Rendering Transform) 和 ODT (Output Display Transform) 的组合函数
它将 ACES 颜色空间中的值转换为最终显示设备上的颜色值。
'''
@ti.func
def RRTAndODTFit(v: vec3) -> vec3:
    a = v * (v + 0.0245786) - 0.000090537
    b = v * (0.983729 * v + 0.4329510) + 0.238081
    return a / b

'''
ACESFitted 函数是 ACES 的完整色调映射函数，它将 RGB 颜色空间的值转换为最终显示设备上的颜色值。
具体来说，它将 RGB 颜色空间的值通过 ACESInputMat 转换到 ACES 颜色空间中，
然后通过 RRTAndODTFit 函数进行 RRT 和 ODT 的转换，最后通过 ACESOutputMat 转换到最终显示设备的颜色空间中。
'''
@ti.func
def ACESFitted(rgb: vec3) -> vec3:
    rgb = ACESInputMat  @ rgb
    rgb = RRTAndODTFit(rgb)
    rgb = ACESOutputMat @ rgb
    return rgb
