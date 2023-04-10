import time
import taichi as ti
from taichi.math import vec2
from taichi.ui import LEFT, RIGHT, UP, DOWN, RELEASE


from .config import image_resolution
from .fileds import image_pixels, diff_pixels, ray_buffer
from .camera import smooth, camera_exposure,  camera_focus, camera_aperture, camera_vfov
from .scene import build_scene
from .renderer import render


window = ti.ui.Window("渲染引擎", image_resolution)
canvas = window.get_canvas()
camera = ti.ui.Camera()
camera.position(0, -0.2, 4.0)
smooth.init(camera)


build_scene()
prev_time = time.time()

while window.running:
    curr_time = time.time()
    dt = curr_time - prev_time                          # dt 表示两次渲染循环之间的时间差
    prev_time = curr_time

                                                        # 相机移动方向
    direction = vec2(float(window.is_pressed(RIGHT)) - float(window.is_pressed(LEFT)),
                     float(window.is_pressed(UP)) - float(window.is_pressed(DOWN)))

    refreshing = False                                  # 根据用户按下的按键来调整相机的各种参数，并在窗口中实时更新相机视角。
    if window.is_pressed('z'):                          # 按下 'z' 键时，会将相机视场角的值增加 direction.y * dt * 10
        camera_vfov[None] += direction.y * dt * 10      # 其中 direction.y 表示用户按下 'up' 或 'down' 键的方向
        direction.y = 0                                 # 将 direction.y 设为 0 ，并将 refreshing 设为 True 。
        refreshing = True                               # 在控制台中输出相机视场角的值
        print('vfov', camera_vfov[None])
    elif window.is_pressed('x'):
        camera_aperture[None] += direction.y * dt       # 将相机光圈的值增加 direction.y * dt
        direction.y = 0
        refreshing = True
        print('aperture', camera_aperture[None])
    elif window.is_pressed('c'):
        camera_focus[None] += direction.y * dt          # 将相机聚焦距离的值增加 direction.y * dt
        direction.y = 0
        refreshing = True
        print('focus', camera_focus[None])              # 最后在控制台中输出相机聚焦距离的值
    elif window.is_pressed('v'):
        camera_exposure[None] += direction.y * dt       # 会将相机曝光值的值增加 direction.y * dt
        direction.y = 0
        print('exposure', camera_exposure[None])        # 在控制台中输出相机曝光值的值

    for event in window.get_events(RELEASE):
        if event.key == 'g':
            ti.tools.imwrite(image_pixels, 'out/main_' +
                             str(curr_time) + '.png')

    speed = dt * 5 * (10 if window.is_pressed('Shift') else 1)
    camera.track_user_inputs(window, movement_speed=speed, hold_key=ti.ui.LMB)
    smooth.update(dt, camera, direction)

    render(refreshing)  # refreshing 变量的作用是判断是否需要重新渲染画面，如果用户更改了相机参数，则需要重新渲染画面并更新窗口中的图像。

    canvas.set_image(image_pixels)
    # canvas.set_image((diff_pixels.to_numpy() > 1e-3).astype('float32'))
    # canvas.set_image(((ray_buffer.depth).to_numpy() / 3.0).astype('float32'))

    window.show()




