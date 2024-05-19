from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from playsound import playsound
import subprocess
from random import choice, randint
from ursina.shaders.lit_with_shadows_shader import lit_with_shadows_shader
from threading import Thread, Event
from pygame import mixer

mixer.init()
walking = False
shader = lit_with_shadows_shader

def play(audio_file_path):
    subprocess.call(["ffplay", "-nodisp", "-autoexit", audio_file_path])

app = Ursina()
tip = Text(
    text='Controls:\nW,A,S,D: Walking\nSpace: Jump\nr: Reload\nLeft Click: Shoot\nRight Click: Aim\nShift: Sprint\nk + Left Click: Exit\nk+k: Undo Exit',
    position=(-0.78, 0.4),
    origin=(0, 0),
    scale=0.5,
    color=color.white
)
house = Entity(
    model="Assets/Models/house",
    position=(0, -1, 0),
    scale=(0.66, 0.66, 0.66),
    collider="box",
    texture="Assets/Textures/wood_balls.png"
)
point_lbl = Text(
    text='Destroyed Targets: 0',
    position=(0.2, -0.47),
    origin=(0, 0),
    scale=0.5,
    color=color.white
)
buulet = Text(
    text="Bullets: 10/10",
    position=(0.2, -0.4),
    origin=(0, 0),
    scale=0.7,
    color=color.white
)

clk_lbl = Text(
    text="Trial Time Left: 40",
    position=(0.2, -0.45),
    origin=(0, 0),
    scale=0.7,
    color=color.white
)

clock_event = Event()

def clock():
    clk_time = 40
    while not clock_event.is_set():
        if clk_time == 0:
            kill()
            playsound("Assets/Sounds/glock_sound.mp3", block=False)
            application.quit()
            break
        time.sleep(1)
        clk_time -= 1
        clk_lbl.text = f"Trial Time Left: {clk_time}"

clock_thread = Thread(target=clock)
clock_thread.start()

player = FirstPersonController(
    mouse_sensitivity=Vec2(100, 100),
    position=(0, 5, 10),
    height=1,
)

jump_sound_lst = ["Assets/Sounds/jump.mp3", "Assets/Sounds/jump2.mp3", "Assets/Sounds/jump3.mp3"]
global reloading, killing
killing = False
reloading = False
ammo = 10
gun = Entity(
    parent=player,
    model="Assets/Models/Glock17",
    scale=0.2,
    texture="Assets/Textures/Glock17_BaseColor.png",
    position=(1, 1.5, 1),
    rotation=(0, 180, 0),
    shader=shader
)

class Block(Entity):
    def __init__(self, position):
        super().__init__(position=position, model="cube", texture="Assets/Textures/wood_balls.png", collider="box")
        self.block = "foo"

def play_animation():
    global aiming
    pos = 0 if aiming else 1
    gun.animate_position((pos, 1.5, 1), duration=0.1, curve=curve.linear)
    gun.animate_position((pos, 1.5, 2), delay=0.1, duration=0.1, curve=curve.linear)

def aim():
    gun.animate_position((1, 1.5, 2), duration=0.1, curve=curve.linear)
    gun.animate_position((0, 1.5, 2), delay=0.1, duration=0.1, curve=curve.linear)

ground = Entity(
    model="plane",
    texture_scale=(100, 100),
    texture="grass",
    scale=(110, 110, 110),
    collider="box",
    position=(0, -1, 0),
    shader=shader
)

def move():
    for _ in range(10):
        d = Block((randint(-100, 100), randint(0, 100), randint(-100, 100)))
        d.animate_position((randint(-100, 100), randint(0, 100), randint(-100, 100)), duration=40, curve=curve.linear)
    for _ in range(10):
        d = Block((randint(-100, 100), 0, randint(-100, 100)))
        d.animate_position((randint(-100, 100), 0, randint(-100, 100)), duration=40, curve=curve.linear)

move()

def play_wlk():
    mixer.music.load("Assets/Sounds/walking.mp3")
    mixer.music.play()

def play_run():
    mixer.music.load("Assets/Sounds/running.mp3")
    mixer.music.play()

def kill():
    gun.animate_position((1, 1.5, 2), duration=0.1, curve=curve.linear)
    gun.animate_position((1.3, 2, 2), delay=0.1, duration=0.1, curve=curve.linear)
    gun.animate_rotation((12, 12, 12), delay=0.11, duration=0.1, curve=curve.linear)

def reload():
    gun.animate_position((1, 1.5, 2), duration=0.1, curve=curve.linear)
    gun.animate_position((1.3, 2, 2), delay=0.1, duration=0.1, curve=curve.linear)
    gun.animate_rotation((202, 202, 202), delay=0.11, duration=0.1, curve=curve.linear)

def play_walking_sound():
    mixer.music.load("Assets/Sounds/walking.mp3")
    mixer.music.play(-1)

def play_running_sound():
    mixer.music.load("Assets/Sounds/running.mp3")
    mixer.music.play(-1)

def stop_sound():
    mixer.music.stop()

is_walking = False
is_running = False

def update():
    global is_walking, is_running

    if held_keys["w"] or held_keys["a"] or held_keys["s"] or held_keys["d"]:
        if held_keys["shift"]:
            if not is_running:
                print("running")
                play_running_sound()
                is_running = True
                is_walking = False
        else:
            if not is_walking:
                print("walking")
                play_walking_sound()
                is_walking = True
                is_running = False
    else:
        if is_walking or is_running:
            stop_sound()
            is_walking = False
            is_running = False

    gun.rotation_x = -player.camera_pivot.rotation_x
    if held_keys['shift']:
        player.speed = 10
    else:
        player.speed = 5
    if not held_keys['w']:
        mixer.music.stop()
        walking = False

def enable_delay():
    global reloading
    reloading = False
    gun.animate_rotation((0, 180, 0), delay=0.11, duration=0.1, curve=curve.linear)
    gun.animate_position((1, 1.5, 2), delay=0.11, duration=0.1, curve=curve.linear)

Sky(texture="Assets/Textures/sky.png")
global aiming
aiming = False
killedsd = 0

def input(key):
    global aiming, ammo, reloading, killing, point_lbl, killedsd
    if key == "left mouse down":
        if ammo != 0 and reloading == False:
            playsound("Assets/Sounds/glock_sound.mp3", block=False)
            try:
                if mouse.hovered_entity.block:
                    destroy(mouse.hovered_entity)
                    killedsd += 1
                    print("Just added another kill")
                    point_lbl.text = f"Targets Destroyed: {killedsd}"
                    print(killedsd)
            except Exception as e:
                print(e)
            if killing == True:
                application.quit()
            play_animation()
            ammo -= 1
        else:
            playsound("Assets/Sounds/glock_empty.mp3", block=False)
        buulet.text = f"Bullets: {ammo}/10"
    elif key == "right mouse down":
        aim()
        aiming = True
    if key == "right mouse up":
        aiming = False
        gun.animate_position((1, 1.5, 2), delay=0.1, duration=0.1, curve=curve.linear)
    if key == "r":
        killing = False
        playsound("Assets/Sounds/glock_reload.wav", block=False)
        reloading = True
        reload()
        invoke(enable_delay, delay=3.2)
        ammo = 10
        buulet.text = f"Bullets: {ammo}/10"
    if key == "space":
        playsound(random.choice(jump_sound_lst), block=False)
    if key == "k":
        if killing == False:
            kill()
            killing = True
        else:
            enable_delay()
            killing = False

app.run()
clock_event.set()
clock_thread.join()
