import pyxel
import random

class SlotGame:
    def __init__(self):
        # ゲームの初期化
        self.balance = 10000  # スタート時の残高
        self.bet = 200  # ベット額
        # スロットのリール（3x3のグリッド）
        self.wheels = [[self.get_item() for _ in range(3)] for _ in range(3)]
        self.spinning = [False, False, False]  # 各リールのスピン状態
        self.game_over = False  # ゲームオーバーのフラグ
        self.free_spins = 0  # フリースピンのカウンター
        self.spin_speed_factor = 1  # スピン速度の因子
        self.win_checked = False  # 勝利のチェック状態
        self.frame_count = 0  # フレームカウント
        # ボタンのプロパティ
        self.buttons = {
            'spin': {'shape': 'rect', 'coords': (20, 170, 20, 20)},
            'bet_increase': {'shape': 'circ', 'coords': (200, 180, 10)},
            'bet_decrease': {'shape': 'circ', 'coords': (225, 180, 10)},
            'stop_0': {'shape': 'circ', 'coords': (60, 155, 6)},
            'stop_1': {'shape': 'circ', 'coords': (130, 155, 6)},
            'stop_2': {'shape': 'circ', 'coords': (200, 155, 6)},
        }
        # Pyxelの初期化
        pyxel.init(250, 200, title="Slot Machine", fps=60, display_scale=8)
        pyxel.load('my_resource.pyxres')  # リソースの読み込み
        pyxel.mouse(True)  # マウスカーソルの表示
        pyxel.run(self.update, self.draw)  # アップデートと描画メソッドの実行
    
    def get_item(self):
        # スロットの各項目を確率に基づいて選ぶ
        probabilities = {0: 0.30,  
                         1: 0.15, 
                         2: 0.1, 
                         3: 0.15,  
                         4: 0.10, 
                         5: 0.05, 
                         6: 0.15} 
        return random.choices(list(probabilities.keys()), weights=list(probabilities.values()), k=1)[0]

    def update(self):
        # ゲームの状態をアップデート
        if self.game_over:
            pyxel.play(1, 4)  # ゲームオーバー時のサウンド
            pyxel.stop(0)  # ループサウンドの停止
            return

        # ベット額の更新
        if pyxel.btnp(pyxel.KEY_UP) or self.is_mouse_on_button('bet_increase') and pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            self.bet = min(self.bet + 100, self.balance)
        if pyxel.btnp(pyxel.KEY_DOWN) or self.is_mouse_on_button('bet_decrease') and pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            self.bet = max(self.bet - 100, 200)

        # スピンとストップボタンの処理
        if pyxel.btnp(pyxel.KEY_SPACE) and (self.balance > 0 or self.free_spins > 0) or self.is_mouse_on_button('spin') and pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) and (self.balance > 0 or self.free_spins > 0):
            pyxel.play(0, 3)  # スピンサウンド
            if not any(self.spinning):  # 全てのリールが停止している場合のみスピンを許可
                if self.free_spins > 0:
                    self.free_spins -= 1
                else:
                    if self.balance < self.bet:
                        self.bet = self.balance
                    self.balance -= self.bet
                    
                self.spinning = [True, True, True]  # リールのスピン開始
                self.spin_speed_factor = 1
                self.win_checked = False
        
        if any(self.spinning):
            pyxel.play(0, 0, loop=True)  # スピン中のサウンド（ループ）

        # 個々のリールの停止処理
        for i in range(3):
            if pyxel.btnp(pyxel.KEY_1 + i) or self.is_mouse_on_button(f'stop_{i}') and pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                pyxel.play(0, 1)  # 停止サウンド
                self.spinning[i] = False

        # スピン中のリールの更新
        for i in range(3):
            if self.spinning[i] and random.random() < 0.5 * self.spin_speed_factor:
                self.wheels[i] = [self.get_item() for _ in range(3)]
        

        # 全てのリールが停止したかチェックし、勝利条件を確認
        if not any(self.spinning) and not self.win_checked:
            self.win_checked = True
            win_amount = self.check_for_win()
            self.balance += win_amount
            if self.balance <= 0 and self.free_spins <= 0:
                self.game_over = True

    def is_mouse_on_button(self, button):
        # マウスが特定のボタンの上にあるかチェック
        mouse_x, mouse_y = pyxel.mouse_x, pyxel.mouse_y
        button_props = self.buttons.get(button)

        if button_props:
            if button_props['shape'] == 'rect':
                x, y, w, h = button_props['coords']
                return x <= mouse_x <= x + w and y <= mouse_y <= y + h
            elif button_props['shape'] == 'circ':
                x, y, r = button_props['coords']
                return (mouse_x - x)**2 + (mouse_y - y)**2 <= r**2
        return False

    def check_for_win(self):
        # 勝利条件をチェックし、勝利金額を計算
        total_win = 0

        # 水平および垂直ラインのチェック
        for i in range(3):
            if self.wheels[i][0] == self.wheels[i][1] == self.wheels[i][2]:
                total_win += self.calculate_reward(self.wheels[i][0])
            if self.wheels[0][i] == self.wheels[1][i] == self.wheels[2][i]:
                total_win += self.calculate_reward(self.wheels[0][i])

        # 対角線のチェック
        if self.wheels[0][0] == self.wheels[1][1] == self.wheels[2][2]:
            total_win += self.calculate_reward(self.wheels[0][0])
        if self.wheels[0][2] == self.wheels[1][1] == self.wheels[2][0]:
            total_win += self.calculate_reward(self.wheels[0][2])

        return total_win

    def calculate_reward(self, item):
        # 各項目に対する報酬の定義
        rewards = {
            0: 3 * self.bet, # bet額の3倍
            1: 6 * self.bet, # bet額の6倍
            2: 12 * self.bet, # bet額の12倍
            3: 1,  # アイテム3の特別処理
            4: 1,  # アイテム4の特別処理
            5: 1,  # アイテム5の特別処理
            6: 1   # アイテム6の特別処理
        }
        # 特別処理
        if item in [0, 3]:
            pyxel.play(0, 2)  # サウンド再生
        elif item in [1, 5]:
            pyxel.play(0, 5)  # 別のサウンド再生
        elif item in [2, 4]:
            pyxel.play(0, 6)  # 別のサウンドを再生

        # アイテムごとの特別な効果
        if item == 3:
            self.free_spins += 1  # アイテム4が出た場合、フリースピンを1回追加
        elif item == 4:
            self.free_spins += 5  # アイテム5が出た場合、フリースピンを5回追加
        elif item == 5:
            self.game_over = True  # アイテム5が出た場合、ゲームオーバー
        elif item == 6:
            self.spin_speed_factor = 0.1  # アイテム6が出た場合、スピン速度を半分にする
    
        return rewards[item]  # 定義した報酬を返す

    def draw(self):
        pyxel.cls(0)  # 画面をクリアする

        if self.game_over:
            # ゲームオーバーの場合の画面表示
            pyxel.rect(0, 0, 250, 200, 9)  # 背景の矩形を描画
            pyxel.text(70, 90, "Game Over!", 7)  # ゲームオーバーのテキスト
            pyxel.text(70, 105, f"Final Balance: {self.balance}", 7)  # 最終残高の表示
        else:
            # ゲームオーバーでない場合の画面表示
            pyxel.rect(0, 0, 250, 200, 9)  # 背景の矩形を描画
            pyxel.rectb(0, 0, 250, 200, 0)  # 背景の矩形の枠線を描画

            # スロットの各アイテムを描画
            for i in range(3):
                for j in range(3):
                    x = 30 + i * 70
                    y = 30 + j * 40
                    pyxel.rect(x, y, 60, 35, 5)  # アイテムの背景矩形
                    pyxel.rectb(x, y, 60, 35, 0)  # アイテムの枠線

            # スロットの各アイテムの画像を描画
            for i in range(3):
                for j in range(3):
                    item = self.wheels[i][j]
                    pyxel.blt(35 + i * 70, 32 + j * 40, 1, (item % 4) * 16, (item // 4) * 16, 16, 16)

            # 残高、フリースピン、賭け金の表示
            pyxel.text(15, 15, f"Balance: {self.balance}", 7)
            pyxel.text(80, 15, f"Free Spins: {self.free_spins}", 7)
            pyxel.text(180, 15, f"Bet: {self.bet}", 7)

            # 各スロットの停止ボタンを描画
            for i in range(3):
                x, y, r = self.buttons[f'stop_{i}']['coords']
                pyxel.circ(x, y, r, 7)

            # 「スピン」ボタンを描画
            pyxel.rect(20, 170, 40, 20, 8)  # 「スピン」ボタンの背景
            pyxel.text(25, 176, "S P I N", 7)  # 「スピン」というテキスト

            # 賭け金の増減ボタンを描画
            x, y, r = self.buttons['bet_increase']['coords']
            pyxel.circ(x, y, r, 5)
            pyxel.text(x - 2, y - 2, "+", 7)

            x, y, r = self.buttons['bet_decrease']['coords']
            pyxel.circ(x, y, r, 10)
            pyxel.text(x - 2, y - 2, "-", 7)

SlotGame()
