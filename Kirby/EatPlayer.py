from pico2d import *
import  Star
import Struct
import win32api
import PlayerState
import main_state
import Player
import Effect

m_PlayerState = None


class CEatPlayer:
    def __init__(self,x,y,dira):
        self.x, self.y = x, y
        self.frame = 1
        self.MaxFrame = 3
        self.imageRight = load_image('Texture/EatKirbyR.png')
        self.imageLeft = load_image('Texture/EatKirbyL.png')
        self.LineLst = [Struct.CLinePos(-60, 120, 520, 120, 0), Struct.CLinePos(520, 230, 800, 230, 0)]
        self.dir = dira
        self.Eating = False
        self.fSpeed = 10
        self.fGravity = 20
        self.fJumpAcc = 1.5
        self.m_bisJump = False
        self.PreAni = 'DOWN'
        self.AniStop = False
        self.CurAni = 'IDLE'
        self.m_bisDead = 0
        self.m_bisDamaged = False
        self.m_bisShoot  =False
        self.AniLst = {'IDLE': Struct.CAniDate(0, 3, 0), 'DOWN': Struct.CAniDate(0, 5, 1),
                       'WALK': Struct.CAniDate(0, 15, 3), 'JUMP': Struct.CAniDate(0, 4, 4),'SHOOT':Struct.CAniDate(0, 4, 6),'FJUMP':Struct.CAniDate(0, 2, 5),'DAMAGED':Struct.CAniDate(0, 2, 5)}
        self.m_Rect = Struct.CRect(128, 128, self.x, self.y)
        # 걷기 이팩트 관련
        self.WalkEffectCount = 0

        self.WalkSound = load_wav('Sound/Dash.wav')
        self.WalkSound.set_volume(30)

        self.JumpSound = load_wav('Sound/Jump.wav')
        self.JumpSound.set_volume(40)

        self.ShootStarSound = load_wav('Sound/ShootStar.wav')
        self.ShootStarSound.set_volume(40)

    def enter(self):
        global m_PlayerState
        m_PlayerState = PlayerState.CPlayerState()
        pass

    def update(self):

        self.Key_Input()
        self.AniMationCheck()
        self.Shooting()
        self.Frame_Check()
        self.Move_Check()
        self.LineCollision()
        self.Jumping()
        self.m_Rect.update(self.x, self.y)
        self.CollisionMonster()
        self.IsScrolling()
        self.m_bisDamaged = False
        self.MakeEffect()
        if(self.CurAni=='DAMAGED'):
            m_Player = Player.CPlayer(self.x, self.y, self.dir)
            m_Player.enter()
            main_state.m_ObjectMgr.Add_Object('PLAYER', m_Player)
            self.m_bisDead=True

        return self.m_bisDead

    def draw(self):
        ScrollX = main_state.m_ScrollMgr.x
        ScrollY = main_state.m_ScrollMgr.y

        if self.dir == 0:
            self.imageRight.clip_draw((int)(self.frame) * 128, 1280 - (self.AniLst[self.CurAni].AniNumber + 1) * 128,
                                      128, 128, self.x-ScrollX, self.y+15)
        else:
            self.imageLeft.clip_draw((2176 - 128) - ((int)(self.frame) * 128),
                                     1280 - (self.AniLst[self.CurAni].AniNumber + 1) * 128, 128, 128, self.x-ScrollX, self.y+15)
        m_PlayerState.draw()

    def AniMationCheck(self):
        if self.CurAni != self.PreAni:
            self.frame = 0
            self.MaxFrame = self.AniLst[self.CurAni].MaxFrame

        self.PreAni = self.CurAni

    def Key_Input(self):
        if self.CurAni != 'JUMP'and self.CurAni != 'SHOOT':
         self.CurAni = 'IDLE'
        else :
          return

        if win32api.GetAsyncKeyState(0x28) & 0x8000:  # 아래
            self.CurAni = 'DOWN'
        if win32api.GetAsyncKeyState(0x25) & 0x8000:  # 왼쪽
            self.dir = 1
            self.CurAni = 'WALK'
        if win32api.GetAsyncKeyState(0x27) & 0x8000:  # 오른쪽
            self.CurAni = 'WALK'
            self.dir = 0
        if win32api.GetAsyncKeyState(0x26) & 0x8000:  # 위
            if self.CurAni != 'JUMP':
                self.JumpSound.play()
                self.CurAni = 'JUMP'
                self.m_bisJump = True
        if win32api.GetAsyncKeyState(0x41) & 0x8000:
            if self.CurAni !='JUMP' and self.CurAni != 'SHOOT':
                self.CurAni = 'SHOOT'


    def Frame_Check(self):
        if self.AniStop == False:
            self.frame = (self.frame + 0.3)
        if (self.frame > self.MaxFrame):
                if(self.CurAni =='SHOOT'):
                    self.m_bisDead =True
                    m_Player = Player.CPlayer(self.x, self.y,self.dir)
                    m_Player.enter()
                    main_state.m_ObjectMgr.Add_Object('PLAYER', m_Player)
                self.frame = 0

    def LineCollision(self):
        Finish =False
        LineLst = main_state.m_LineMgr.LineLst;
        for lineIndex in LineLst:
            if Finish == True:
                return
            if (int(lineIndex.p1y) <= int(self.x)) and lineIndex.p2x >= int(self.x):
                Finish = True
                if (self.m_bisJump == False and self.y + 30 < lineIndex.p1y):
                    if (self.x < (lineIndex.p2x - lineIndex.p1x) / 2 + lineIndex.p1x):  # 중점보다크면
                        self.x = lineIndex.p1x
                    else:
                        self.x = lineIndex.p2x
                elif (self.m_bisJump == False):
                    if (self.y > lineIndex.p1y):
                        self.y = self.y - 15
                        if (lineIndex.p1y > self.y):
                            self.y = lineIndex.p1y


                else:
                    if (int(lineIndex.p1y) <= int(self.x)) and lineIndex.p2x >= int(self.x) and self.y < lineIndex.p1y:
                        self.y = lineIndex.p1y
                        self.m_bisJump = False
                        self.fJumpAcc = 1.5
                        self.AniStop = False
                        self.CurAni = 'FJUMP'
                        self.frame = 0

    def Move_Check(self):
        if self.CurAni == 'WALK' and self.dir == 0:
            self.x = self.x + 10
        elif self.CurAni == 'WALK' and self.dir == 1:
            self.x = self.x - 10
        if self.CurAni == 'JUMP' and self.m_bisJump == True:
            if self.dir == 0:
                self.x = self.x + 5
            else:
                self.x = self.x - 5

    def Jumping(self):
        if self.m_bisJump == True:
                self.fJumpAcc = self.fJumpAcc + 1.0
                self.y = self.y + (self.fGravity - self.fJumpAcc)


    def CollisionMonster(self):
        TempLst = main_state.m_ObjectMgr.Get_ObjectList('MONSTER')
        for n in TempLst:
            if (Struct.CollisionRect(self.m_Rect, n.m_Rect) and n.m_bisdie == False):
                self.CurAni = 'DAMAGED'
                self.frame = 0
                n.Collision = True
                TempLst2 = main_state.m_ObjectMgr.Get_ObjectList('UI')
                for n2 in TempLst2:
                   n2.change()
        TempLst2 = main_state.m_ObjectMgr.Get_ObjectList('BOSS')
        for n in TempLst2:
            if (Struct.CollisionRect(self.m_Rect, n.m_Rect)):
                self.CurAni = 'DAMAGED'
                self.frame = 0
                TempLst2 = main_state.m_ObjectMgr.Get_ObjectList('UI')
                for n2 in TempLst2:
                    n2.change()

        TempLst3 = main_state.m_ObjectMgr.Get_ObjectList('BOSSBULLET')
        for n in TempLst3:
            if (Struct.CollisionRect(self.m_Rect, n.m_Rect) and n.Dead == False):
                self.CurAni = 'DAMAGED'
                self.frame = 0
                n.Dead = True
                TempLst2 = main_state.m_ObjectMgr.Get_ObjectList('UI')
                for n2 in TempLst2:
                    n2.change()
    def Shooting(self):
        if(self.CurAni =='SHOOT'):
            if(self.frame >=2 and self.m_bisShoot ==False):
                self.m_bisShoot = True
                self.ShootStarSound.play()
                m_Star = Star.CStar(self.x, self.y, self.dir)
                m_Star.enter()
                main_state.m_ObjectMgr.Add_Object('BULLET', m_Star)

    def IsScrolling(self):
        fOffsetX = 400
        fOffsetY = 300

        fScrollX = main_state.m_ScrollMgr.x
        fScrollY = main_state.m_ScrollMgr.y
        MoveX = 3
        MoveY = 3

        print(main_state.m_ScrollMgr.x)
        if (fOffsetX + 50 < self.x - fScrollX):
            main_state.m_ScrollMgr.x = main_state.m_ScrollMgr.x + 10
        if (fOffsetX - 50 > self.x - fScrollX):
            main_state.m_ScrollMgr.x = main_state.m_ScrollMgr.x - 10
        if (main_state.m_ScrollMgr.x < 0):
            main_state.m_ScrollMgr.x = 0
        if (main_state.m_ScrollMgr.x > 3140 and main_state.m_LineMgr.stage == 0):
            main_state.m_ScrollMgr.x = 3140
        if (main_state.m_ScrollMgr.x > 1220 and main_state.m_LineMgr.stage == 1):
            main_state.m_ScrollMgr.x = 1220

    def MakeEffect(self):
        if (self.CurAni == 'WALK'):
            self.WalkEffectCount = self.WalkEffectCount + 1
        else:
            self.WalkEffectCount = 0

        if (self.WalkEffectCount > 10):
            self.WalkSound.play()
            if (self.dir == 0):
                RunEffect = Effect.CEffect(self.x - 40, self.y - 30, 0, 1)
            else:
                RunEffect = Effect.CEffect(self.x + 40, self.y - 30, 0, 0)

            main_state.m_ObjectMgr.Add_Object('EFFECT', RunEffect)
            self.WalkEffectCount = 0





