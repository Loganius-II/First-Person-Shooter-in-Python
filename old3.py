from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from playsound import playsound
import subprocess
from random import choice
from ursina.shaders.lit_with_shadows_shader import lit_with_shadows_shader
from threading import Thread
from pygame import mixer
mixer.init()

shader = lit_with_shadows_shader

def play(audio_file_path):
    subprocess.call(["ffplay", "-nodisp", "-autoexit", audio_file_path])

app = Ursina()
player = FirstPersonController(
    mouse_sensitivity=Vec2(100, 100),
    position=(0, 0, 0),
    height=1,
)

jump_sound_lst = ["Assets/Sounds/jump.mp3","Assets/Sounds/jump2.mp3","Assets/Sounds/jump3.mp3"]
global reloading
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

def play_animation():
    global aiming
    pos = 0 if aiming == True else 1
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

def play_walking_sound():
    mixer.music.load("Assets/Sounds/walking.mp3")
    mixer.music.play(-1)  # Play in a loop

def play_running_sound():
    mixer.music.load("Assets/Sounds/running.mp3")
    mixer.music.play(-1)  # Play in a loop

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

def enable_delay():
    global reloading
    reloading = False
    gun.animate_rotation((0,180,0), delay=0.11, duration=0.1, curve=curve.linear)  
    gun.animate_position((1,1.5,2), delay=0.11, duration=0.1, curve=curve.linear)        

Sky(texture="Assets/Textures/sky.png")
global aiming
aiming = False

def input(key):
    global aiming, ammo, reloading
    if key == "left mouse down":
        if ammo != 0 and reloading == False:
            playsound("Assets/Sounds/glock_sound.mp3", block=False)
            play_animation()
            ammo -= 1
        else:
            playsound("Assets/Sounds/glock_empty.mp3", block=False)       
    elif key == "right mouse down":
        aim()
        aiming = True
    if key == "right mouse up":
        aiming = False    
        gun.animate_position((1, 1.5, 2), delay=0.1, duration=0.1, curve=curve.linear)
    if key == "r":
        playsound("Assets/Sounds/glock_reload.wav", block=False)
        reloading = True
        reload()
        invoke(enable_delay, delay=3.2)
        ammo = 10
    if key == "space":
        playsound(choice(jump_sound_lst), block=False)

app.run()
