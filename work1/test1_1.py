def init_board():
    return [['.' for _ in range(3)] for _ in range(3)]


def print_board(board):
    print("\n当前棋盘:")
    print("     0   1   2")
    print("   +---+---+---+")
    for i in range(3):
        print(f" {i} | {board[i][0]} | {board[i][1]} | {board[i][2]} |")
        print("   +---+---+---+")
    print()


def check_winner(board, player):
    # 检查行
    for row in range(3):
        if all(board[row][col] == player for col in range(3)):
            return True
    
    # 检查列
    for col in range(3):
        if all(board[row][col] == player for row in range(3)):
            return True
    
    # 检查主对角线(左上到右下)
    if all(board[i][i] == player for i in range(3)):
        return True
    
    # 检查副对角线(右上到左下)
    if all(board[i][2-i] == player for i in range(3)):
        return True
    
    return False


def is_board_full(board):
    return all(board[row][col] != '.' for row in range(3) for col in range(3))


def get_player_input(player):
    try:
        input_str = input(f"玩家 {player} 输入棋盘坐标(坐标取值0,1,2)： X,Y? ")
        coords = input_str.strip().split(',')
        
        if len(coords) != 2:
            print("❌ 输入格式错误！请使用格式: X,Y")
            return None
        
        x = int(coords[0].strip())
        y = int(coords[1].strip())
        
        if x not in [0, 1, 2] or y not in [0, 1, 2]:
            print("❌ 坐标超出范围！请输入0到2之间的数字。")
            return None
        
        return (x, y)
    
    except ValueError:
        print("❌ 输入错误！请输入数字。")
        return None
    except KeyboardInterrupt:
        print("\n\n游戏被中断。")
        return None


def make_move(board, x, y, player):
    if board[x][y] == '.':
        board[x][y] = player
        return True
    else:
        print("❌ 该位置已被占用！请选择其他位置。")
        return False


def play_game():
    print("=" * 50)
    print("欢迎来到命令行井字棋游戏！")
    print("=" * 50)
    print("\n游戏规则：")
    print("1. 两位玩家分别使用 X 和 O 标记")
    print("2. X 玩家先手")
    print("3. 轮流在3x3棋盘上落子")
    print("4. 率先在一行、一列或对角线上连成三个相同标记的玩家获胜")
    print("5. 输入格式: X,Y (例如: 0,1)")
    print()
    
    board = init_board()
    current_player = 'X'
    move_count = 0
    
    while True:
        print_board(board)
        
        # 获取玩家输入
        coords = get_player_input(current_player)
        if coords is None:
            if coords is None and not isinstance(coords, tuple):
                # 游戏被中断
                break
            continue
        
        x, y = coords
        
        # 尝试落子
        if not make_move(board, x, y, current_player):
            continue
        
        move_count += 1
        
        # 检查是否获胜
        if check_winner(board, current_player):
            print_board(board)
            print("=" * 50)
            print(f"🎉 恭喜！玩家 {current_player} 获胜！")
            print("=" * 50)
            break
        
        # 检查是否平局
        if is_board_full(board):
            print_board(board)
            print("=" * 50)
            print("⚖️  游戏平局！棋盘已满，没有玩家获胜。")
            print("=" * 50)
            break
        
        # 切换玩家
        current_player = 'O' if current_player == 'X' else 'X'
    
    # 询问是否再来一局
    print()
    play_again = input("是否再来一局？(y/n): ").strip().lower()
    if play_again == 'y' or play_again == 'yes':
        print("\n" * 2)
        play_game()
    else:
        print("\n感谢游戏！再见！👋")


if __name__ == "__main__":
    try:
        play_game()
    except KeyboardInterrupt:
        print("\n\n游戏已退出。感谢游戏！")
