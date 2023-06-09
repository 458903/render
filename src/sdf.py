import taichi as ti
from taichi import sin
from taichi.math import length, vec2, vec3, min, max, dot, normalize, vec4, mat4
from enum import IntEnum

from .dataclass import Transform, SDFObject
from .config import MAX_DIS


class SHAPE(IntEnum):
    NONE = 0
    SPHERE = 1
    BOX = 2
    CYLINDER = 3
    CONE = 4
    PLANE = 5
    BUNNY = 6


@ti.func
def sd_none(_: vec3, __: vec3) -> float:
    return MAX_DIS


@ti.func
def sd_sphere(p: vec3, r: vec3) -> float:  # 球的 SDF 函数是到球心的距离减去球半径
    return length(p) - r.x


@ti.func
def sd_box(p: vec3, b: vec3) -> float:
    q = abs(p) - b
    return length(max(q, 0)) + min(q.max(), 0) - 0.03


@ti.func
def sd_cylinder(p: vec3, rh: vec3) -> float:
    d = abs(vec2(length(p.xz), p.y)) - rh.xy
    return min(d.max(), 0) + length(max(d, 0))


@ti.func
def sd_cone(p: vec3, rh: vec3) -> float:
    q = length(p.xz)
    return max(dot(rh.xz, vec2(q, p.y)), -rh.y - p.y)


@ti.func
def sd_plane(p: vec3, h: vec3) -> float:
    return p.y - h.y


@ti.func
def sd_bunny(p: vec3, _: vec3) -> float:
    sd = 0.0
    if length(p) > 1.0:
        sd =  length(p) - 0.8
    else:
        # neural networks can be really compact... when they want to be
        f00=sin(p.y*vec4(-3.02,1.95,-3.42,-.60)+p.z*vec4(3.08,.85,-2.25,-.24)-p.x*vec4(-.29,1.16,-3.74,2.89)+vec4(-.71,4.50,-3.24,-3.50))
        f01=sin(p.y*vec4(-.40,-3.61,3.23,-.14)+p.z*vec4(-.36,3.64,-3.91,2.66)-p.x*vec4(2.90,-.54,-2.75,2.71)+vec4(7.02,-5.41,-1.12,-7.41))
        f02=sin(p.y*vec4(-1.77,-1.28,-4.29,-3.20)+p.z*vec4(-3.49,-2.81,-.64,2.79)-p.x*vec4(3.15,2.14,-3.85,1.83)+vec4(-2.07,4.49,5.33,-2.17))
        f03=sin(p.y*vec4(-.49,.68,3.05,.42)+p.z*vec4(-2.87,.78,3.78,-3.41)-p.x*vec4(-2.65,.33,.07,-.64)+vec4(-3.24,-5.90,1.14,-4.71))
        f10=sin(f00@mat4(-.34,.06,-.59,-.76,.10,-.19,-.12,.44,.64,-.02,-.26,.15,-.16,.21,.91,.15)+
            f01@mat4(.01,.54,-.77,.11,.06,-.14,.43,.51,-.18,.08,.39,.20,.33,-.49,-.10,.19)+
            f02@mat4(.27,.22,.43,.53,.18,-.17,.23,-.64,-.14,.02,-.10,.16,-.13,-.06,-.04,-.36)+
            f03@mat4(-.13,.29,-.29,.08,1.13,.02,-.83,.32,-.32,.04,-.31,-.16,.14,-.03,-.20,.39)+
            vec4(.73,-4.28,-1.56,-1.80))+f00
        f11=sin(f00@mat4(-1.11,.55,-.12,-1.00,.16,.15,-.30,.31,-.01,.01,.31,-.42,-.29,.38,-.04,.71)+
            f01@mat4(.96,-.02,.86,.52,-.14,.60,.44,.43,.02,-.15,-.49,-.05,-.06,-.25,-.03,-.22)+
            f02@mat4(.52,.44,-.05,-.11,-.56,-.10,-.61,-.40,-.04,.55,.32,-.07,-.02,.28,.26,-.49)+
            f03@mat4(.02,-.32,.06,-.17,-.59,.00,-.24,.60,-.06,.13,-.21,-.27,-.12,-.14,.58,-.55)+
            vec4(-2.24,-3.48,-.80,1.41))+f01
        f12=sin(f00@mat4(.44,-.06,-.79,-.46,.05,-.60,.30,.36,.35,.12,.02,.12,.40,-.26,.63,-.21)+
            f01@mat4(-.48,.43,-.73,-.40,.11,-.01,.71,.05,-.25,.25,-.28,-.20,.32,-.02,-.84,.16)+
            f02@mat4(.39,-.07,.90,.36,-.38,-.27,-1.86,-.39,.48,-.20,-.05,.10,-.00,-.21,.29,.63)+
            f03@mat4(.46,-.32,.06,.09,.72,-.47,.81,.78,.90,.02,-.21,.08,-.16,.22,.32,-.13)+
            vec4(3.38,1.20,.84,1.41))+f02
        f13=sin(f00@mat4(-.41,-.24,-.71,-.25,-.24,-.75,-.09,.02,-.27,-.42,.02,.03,-.01,.51,-.12,-1.24)+
            f01@mat4(.64,.31,-1.36,.61,-.34,.11,.14,.79,.22,-.16,-.29,-.70,.02,-.37,.49,.39)+
            f02@mat4(.79,.47,.54,-.47,-1.13,-.35,-1.03,-.22,-.67,-.26,.10,.21,-.07,-.73,-.11,.72)+
            f03@mat4(.43,-.23,.13,.09,1.38,-.63,1.57,-.20,.39,-.14,.42,.13,-.57,-.08,-.21,.21)+
            vec4(-.34,-3.28,.43,-.52))+f03
        f00=sin(f10@mat4(-.72,.23,-.89,.52,.38,.19,-.16,-.88,.26,-.37,.09,.63,.29,-.72,.30,-.95)+
            f11@mat4(-.22,-.51,-.42,-.73,-.32,.00,-1.03,1.17,-.20,-.03,-.13,-.16,-.41,.09,.36,-.84)+
            f12@mat4(-.21,.01,.33,.47,.05,.20,-.44,-1.04,.13,.12,-.13,.31,.01,-.34,.41,-.34)+
            f13@mat4(-.13,-.06,-.39,-.22,.48,.25,.24,-.97,-.34,.14,.42,-.00,-.44,.05,.09,-.95)+
            vec4(.48,.87,-.87,-2.06))/1.4+f10
        f01=sin(f10@mat4(-.27,.29,-.21,.15,.34,-.23,.85,-.09,-1.15,-.24,-.05,-.25,-.12,-.73,-.17,-.37)+
            f11@mat4(-1.11,.35,-.93,-.06,-.79,-.03,-.46,-.37,.60,-.37,-.14,.45,-.03,-.21,.02,.59)+
            f12@mat4(-.92,-.17,-.58,-.18,.58,.60,.83,-1.04,-.80,-.16,.23,-.11,.08,.16,.76,.61)+
            f13@mat4(.29,.45,.30,.39,-.91,.66,-.35,-.35,.21,.16,-.54,-.63,1.10,-.38,.20,.15)+
            vec4(-1.72,-.14,1.92,2.08))/1.4+f11
        f02=sin(f10@mat4(1.00,.66,1.30,-.51,.88,.25,-.67,.03,-.68,-.08,-.12,-.14,.46,1.15,.38,-.10)+
            f11@mat4(.51,-.57,.41,-.09,.68,-.50,-.04,-1.01,.20,.44,-.60,.46,-.09,-.37,-1.30,.04)+
            f12@mat4(.14,.29,-.45,-.06,-.65,.33,-.37,-.95,.71,-.07,1.00,-.60,-1.68,-.20,-.00,-.70)+
            f13@mat4(-.31,.69,.56,.13,.95,.36,.56,.59,-.63,.52,-.30,.17,1.23,.72,.95,.75)+
            vec4(-.90,-3.26,-.44,-3.11))/1.4+f12
        f03=sin(f10@mat4(.51,-.98,-.28,.16,-.22,-.17,-1.03,.22,.70,-.15,.12,.43,.78,.67,-.85,-.25)+
            f11@mat4(.81,.60,-.89,.61,-1.03,-.33,.60,-.11,-.06,.01,-.02,-.44,.73,.69,1.02,.62)+
            f12@mat4(-.10,.52,.80,-.65,.40,-.75,.47,1.56,.03,.05,.08,.31,-.03,.22,-1.63,.07)+
            f13@mat4(-.18,-.07,-1.22,.48,-.01,.56,.07,.15,.24,.25,-.09,-.54,.23,-.08,.20,.36)+
            vec4(-1.11,-4.28,1.02,-.23))/1.4+f13
        sd = dot(f00,vec4(.09,.12,-.07,-.03))+dot(f01,vec4(-.04,.07,-.08,.05))+dot(f02,vec4(-.01,.06,-.02,.07))+dot(f03,vec4(-.05,.07,.03,.04))-0.16

    return sd


SHAPE_FUNC = {
    SHAPE.NONE: sd_none,
    SHAPE.SPHERE: sd_sphere,
    SHAPE.BOX: sd_box,
    SHAPE.CYLINDER: sd_cylinder,
    SHAPE.CONE: sd_cone,
    SHAPE.PLANE: sd_plane,
    SHAPE.BUNNY: sd_bunny
}


@ti.func
def transform(t: Transform, p: vec3) -> vec3:
    p -= t.position  # Cannot squeeze the Euclidean space of distance field
    p = t.matrix @ p  # Otherwise the correct ray marching is not possible
    return p


@ti.func
def calc_pos_scale(obj: SDFObject, p: vec3) -> tuple[vec3, vec3]:
    pos = transform(obj.transform, p)
    return pos, obj.transform.scale


@ti.func
def normal(shape: ti.template(), obj: SDFObject, p: vec3) -> vec3:
    pos, scale = calc_pos_scale(obj, p)
    n, h = vec3(0), 0.5773 * 0.005

    # from https://iquilezles.org/articles/normalsSDF/
    for i in ti.static(range(4)):
        e = 2.0 * vec3((((i + 3) >> 1) & 1), ((i >> 1) & 1), (i & 1)) - 1.0
        n += e * SHAPE_FUNC[shape](pos + e * h, scale)

    return normalize(n)
