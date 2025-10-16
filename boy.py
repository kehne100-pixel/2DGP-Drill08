from pico2d import load_image, get_time
from sdl2 import SDL_KEYDOWN, SDL_KEYUP, SDLK_SPACE, SDLK_RIGHT, SDLK_LEFT, SDLK_a

from state_machine import StateMachine

# 이벤트 체크 함수들
def right_down(e): return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_RIGHT
def right_up(e): return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_RIGHT
def left_down(e): return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_LEFT
def left_up(e): return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_LEFT
def a_down(e): return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_a
def Time_out(e): return e[0] == 'TIME_OUT'


# ------------------- Run 상태 -------------------
class Run:
    def __init__(self, boy):
        self.boy = boy

    def enter(self, e):
        if right_down(e) or left_up(e):
            self.boy.dir = self.boy.face_dir = 1
        elif left_down(e) or right_up(e):
            self.boy.dir = self.boy.face_dir = -1

    def exit(self, e):
        pass

    def do(self):
        self.boy.frame = (self.boy.frame + 1) % 8
        self.boy.x += self.boy.dir * 5
        self.boy.x = max(25, min(775, self.boy.x))

    def draw(self):
        if self.boy.face_dir == 1:
            self.boy.image.clip_draw(self.boy.frame * 100, 100, 100, 100, self.boy.x, self.boy.y, 100, 100)
        else:
            self.boy.image.clip_draw(self.boy.frame * 100, 0, 100, 100, self.boy.x, self.boy.y, 100, 100)


# ------------------- Idle 상태 -------------------
class Idle:
    def __init__(self, boy):
        self.boy = boy

    def enter(self, e):
        self.boy.dir = 0
        self.boy.wait_start_time = get_time()

    def exit(self, e):
        pass

    def do(self):
        self.boy.frame = (self.boy.frame + 1) % 8

    def draw(self):
        if self.boy.face_dir == 1:
            self.boy.image.clip_draw(self.boy.frame * 100, 300, 100, 100, self.boy.x, self.boy.y, 100, 100)
        else:
            self.boy.image.clip_draw(self.boy.frame * 100, 200, 100, 100, self.boy.x, self.boy.y, 100, 100)


# ------------------- AutoRun 상태 -------------------
class AutoRun:
    def __init__(self, boy):
        self.boy = boy

    def enter(self, e):
        self.start_time = get_time()
        self.boy.dir = -1  # Idle에서 'a' 누르면 왼쪽으로 자동 이동
        self.boy.face_dir = -1
        print("AutoRun Start")

    def exit(self, e):
        self.boy.dir = 0
        print("AutoRun End")

    def do(self):
        self.boy.frame = (self.boy.frame + 1) % 8
        self.boy.x += self.boy.dir * 10  # 더 빠른 속도
        self.boy.x = max(25, min(775, self.boy.x))

        # 화면 끝에서 방향 반전
        if self.boy.x <= 25:
            self.boy.dir = 1
            self.boy.face_dir = 1
        elif self.boy.x >= 775:
            self.boy.dir = -1
            self.boy.face_dir = -1

        # 5초 경과 시 Idle 상태 복귀
        if get_time() - self.start_time > 5:
            self.boy.state_machine.handle_state_event(('TIME_OUT', 0))

    def draw(self):
        # AutoRun에서는 캐릭터가 커지고 속도가 빠름
        if self.boy.face_dir == 1:
            self.boy.image.clip_draw(self.boy.frame * 100, 100, 100, 100, self.boy.x, self.boy.y, 150, 150)
        else:
            self.boy.image.clip_draw(self.boy.frame * 100, 0, 100, 100, self.boy.x, self.boy.y, 150, 150)


# ------------------- Boy 클래스 -------------------
class Boy:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.face_dir = 1
        self.dir = 0
        self.image = load_image('animation_sheet.png')

        self.IDLE = Idle(self)
        self.Run = Run(self)
        self.AutoRun = AutoRun(self)

        self.state_machine = StateMachine(
            self.IDLE,
            {
                self.IDLE: {right_down: self.Run, left_down: self.Run, a_down: self.AutoRun},
                self.Run: {left_up: self.IDLE, right_up: self.IDLE, a_down: self.AutoRun},
                self.AutoRun: {Time_out: self.IDLE, left_down: self.Run, right_down: self.Run}
            }
        )

    def update(self):
        self.state_machine.update()

    def draw(self):
        self.state_machine.draw()

    def handle_event(self, event):
        self.state_machine.handle_state_event(('INPUT', event))
