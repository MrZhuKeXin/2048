import curses
from collections import defaultdict
from random import choice,randrange

letter_codes=[ord(i) for i in 'WSADRQBwsadrqb']
action=['UP','DOWN','LEFT','RIGHT','RESET','EXIT','BEGIN']
action_dict=dict(zip(letter_codes,action*2))
help_string1 = '(W)Up (S)Down (A)Left (D)Right'
help_string2 = ' (R)Restart (Q)Exit (B)Begin'

#翻转矩阵
def shift(field):
    return [i[::-1] for i in field]
#矩阵转置
def transpose(field):
    return [list(i) for i in zip(*field)]
#类Gamefield,包含主函数矩阵的类
class Gamefield(object):
    def __init__(self,height=4,width=4,win_value=128):
        self.height = height
        self.width = width
        self.win_value = win_value
        self.score=0
        self.highscore=0
        self.reset()

    def spwan(self):
        x=4 if randrange(100)>86 else 2
        (i,j)=choice([(i,j) for i in range(self.height) for j in range(self.width) if self.field[i][j]==0])
        self.field[i][j]=x

    def reset(self):
        if self.score>self.highscore:
            self.highscore=self.score
        self.score=0
        self.field=[[0 for i in range(self.width)] for j in range(self.height)]
        self.spwan()
        self.spwan()
    #移动小方块
    def move(self,direction):
        def move_row_left(row):
            def gather(row):
                new_row=[0 for i in range(len(row))]
                index=0
                for i in row:
                    if i>0:
                        new_row[index]=i
                        index=index+1
                return new_row
            def merge(row):
                new_row=[0 for i in range(len(row))]
                i=0
                while i<len(row)-1:
                    if row[i]==row[i+1]:
                        row[i]=2*row[i]
                        self.score+=row[i]
                        row[i+1]=0
                        i=i+1
                    i=i+1
                return row
            return gather(merge(gather(row)))
        move_action={
            'LEFT':lambda field:[move_row_left(i) for i in field],
            'RIGHT':lambda field:shift([move_row_left(i) for i in shift(field)]),
            'UP':lambda field:transpose([move_row_left(i) for i in transpose(field)]),
            'DOWN':lambda field:transpose(shift([move_row_left(i) for i in shift(transpose(field))]))
        }
        if direction in move_action:
            if self.move_is_possible(direction):
                self.field = move_action[direction](self.field)
                self.spwan()
            return True
        else:
            return False

    #判断是否可以移动
    def move_is_possible(self,direction):
        def left_move_is_possible(field):
            def left_move_row_is_possible(row):
                def change(i):
                    if row[i] == row[i+1] and row[i] != 0:#有相同的可以合并
                        return True
                    if row[i] == 0 and row[i+1] != 0:#有空位
                        return True
                    return False
                return any(change(i) for i in range(len(row)-1))
            return any(left_move_row_is_possible(row) for row in field)
        move_possible_action = {
            'LEFT': lambda field: left_move_is_possible(field),
            'RIGHT': lambda field: left_move_is_possible(shift(field)),
            'UP': lambda field: left_move_is_possible(transpose(field)),
            'DOWN': lambda field: left_move_is_possible(shift(transpose(field)))
        }
        if direction in move_possible_action:
            return move_possible_action[direction](self.field)
        else:
            raise AttributeError('<Move is possible()>:必须要是指令表中的指令')
    #判断是否游戏结束
    def is_gameover(self):
        if any(any(i==0 for i in row) for row in self.field):
            return False
        else:
            for i in['UP','DOWN','LEFT','RIGHT']:
                if self.move_is_possible(i):
                    return False
        return True
    #判断是否胜利
    def is_win(self):
        return any(any(i>=self.win_value for i in row) for row in self.field)
    #画出矩阵
    def draw(self,stdscr):
        stdscr.addstr('+-----' * self.width+'+\n')
        for row in self.field:
            for i in row:
                if i!=0:
                    stdscr.addstr('|'+'{:^5}'.format(i))
                else:
                    stdscr.addstr('|     ')
            stdscr.addstr('|\n')
            stdscr.addstr('+-----' * self.width + '+\n')
#主函数，使用curses的wrapped调用来显示
def main(stdscr):

    gamefield=Gamefield()

    def begin():
        stdscr.clear()
        stdscr.addstr("Welcome to 2048~\n")
        stdscr.addstr("[author:@ZhuKeXin]\n")
        stdscr.addstr("+-----------------+\n")
        stdscr.addstr('[1]New Game\n')
        stdscr.addstr('[2]Ranking\n')
        stdscr.addstr('[3]Settings\n')
        stdscr.addstr('[4]Exit\n')
        begin_dict = {ord('1'): 'GAME', ord('2'): 'RANKINGS', ord('3'): 'SETTINGS', ord('4'): 'EXIT'}
        c = stdscr.getch()
        while c not in begin_dict:
            c = stdscr.getch()
        if begin_dict[c]=='GAME':
            gamefield.reset()
        return begin_dict[c]

    def game():
        stdscr.clear()
        stdscr.addstr("SCORE:%s\n" % gamefield.score)
        if gamefield.highscore!=0:
            stdscr.addstr("HIGHSCORE:%s\n" % gamefield.highscore)
        gamefield.draw(stdscr)
        stdscr.addstr(help_string1+'\n')
        stdscr.addstr(help_string2)
        if gamefield.is_gameover():
            return 'GAMEOVER'
        elif gamefield.is_win():
            return 'WIN'
        c = stdscr.getch()
        if c in letter_codes:
            if action_dict[c]=='RESET':
                return 'RESET'
            if action_dict[c]=='BEGIN':
                return 'BEGIN'
            if action_dict[c]=='EXIT':
                return 'EXIT'
            if action_dict[c] in ['UP','DOWN','LEFT','RIGHT']:
                    gamefield.move(action_dict[c])
        return 'GAME'

    def gameover():
        stdscr.clear()
        stdscr.addstr("SCORE:%s\n" % gamefield.score)
        if gamefield.highscore!=0:
            stdscr.addstr("HIGHSCORE:%s\n" % gamefield.highscore)
        gamefield.draw(stdscr)
        stdscr.addstr('Game Over!\n')
        stdscr.addstr(help_string2+'\n')
        c=stdscr.getch()
        gameover_dict = {ord('R'):'RESET',ord('r'):'RESET',ord('B'):'BEGIN',ord('b'):'BEGIN',ord('Q'):'EXIT',ord('q'):'EXIT'}
        while c not in gameover_dict:
            c=stdscr.getch()
        return gameover_dict[c]

    def win():
        stdscr.clear()
        stdscr.addstr("SCORE:%s\n" % gamefield.score)
        if gamefield.highscore!=0:
            stdscr.addstr("HIGHSCORE:%s\n" % gamefield.highscore)
        gamefield.draw(stdscr)
        stdscr.addstr('You win! %s!\n'%gamefield.win_value)
        stdscr.addstr(help_string2 + '\n')
        c = stdscr.getch()
        win_dict = {ord('R'): 'RESET', ord('r'): 'RESET', ord('B'): 'BEGIN', ord('b'): 'BEGIN', ord('Q'): 'EXIT',
                         ord('q'): 'EXIT'}
        while c not in win_dict:
            c = stdscr.getch()
        return win_dict[c]

    def settings():
        stdscr.clear()
        stdscr.addstr("[Settings](not yet)\n")
        stdscr.addstr("You can choose a mode as  you wish\n")
        stdscr.addstr("Mode now : win_score[2048]\n")
        stdscr.addstr("+-----------------+\n")
        stdscr.addstr('[1]2048\n')
        stdscr.addstr('[2]4096\n')
        stdscr.addstr('[3]8192\n')
        stdscr.addstr('[4]16384\n')
        settings_dict = {ord('B'): 'BEGIN', ord('b'): 'BEGIN', ord('Q'): 'EXIT',
                         ord('q'): 'EXIT'}
        stdscr.addstr(' (Q)Exit (B)Begin')
        c = stdscr.getch()
        while c not in settings_dict:
            c=stdscr.getch()
        return settings_dict[c]

    def rankings():
        stdscr.clear()
        stdscr.addstr("[Rankings](not yet)\n")
        stdscr.addstr("+-----------------+\n")
        for i in range(1,10):
            stdscr.addstr("[Ranking %s]-------------------\n"%i)
        rankings_dict = {ord('B'): 'BEGIN', ord('b'): 'BEGIN', ord('Q'): 'EXIT',
                         ord('q'): 'EXIT'}
        stdscr.addstr(' (Q)Exit (B)Begin')
        c = stdscr.getch()
        while c not in rankings_dict:
            c = stdscr.getch()
        return rankings_dict[c]

    def reset():
        gamefield.reset()
        return 'GAME'
    def exit():
        pass

    state_actions={
        'BEGIN':begin,
        'GAME':game,
        'GAMEOVER':gameover,
        'WIN':win,
        'RESET':reset,
        'SETTINGS':settings,
        'RANKINGS':rankings,
        'EXIT':exit
    }

    state='BEGIN'

    while state != 'EXIT':
        state = state_actions[state]()

curses.wrapper(main)