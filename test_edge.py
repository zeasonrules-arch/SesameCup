import json
# 导入您自己写的引擎文件（确保 gui_server.py 在同级目录）
import gui_server


def inject_test_data():
    # 1. 加载现有数据
    with open('data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 2. 注入极端测试数据 (A组大乱斗：A1, A2, A3 胜场全部是 2胜1负)
    # 故意制造：A1 赢 A2，A2 赢 A3，A3 赢 A1 的连环套
    test_scores = {
        "a1_a2": "25-23",  # A1胜 (净胜分+2)
        "a3_a4": "25-10",  # A3胜
        "a1_a3": "20-25",  # A3胜 (A1净胜分-5, 此时A1总净胜分为-3)
        "a2_a4": "25-15",  # A2胜
        "a1_a4": "25-20",  # A1胜 (A1净胜分+5, 此时A1总净胜分为+2)
        "a2_a3": "25-23",  # A2胜
    }

    # 覆盖 A 组的比分
    for match, score in test_scores.items():
        data['scores']['group'][match] = score

    # 3. 保存并触发您的计算引擎
    gui_server.save_data(data)
    gui_server.calculate_all()
    print("✅ 极端测试数据已注入并计算完毕！")


if __name__ == '__main__':
    inject_test_data()