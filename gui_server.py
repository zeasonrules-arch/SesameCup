import json
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler


def load_data():
    with open('data.json', 'r', encoding='utf-8') as f: return json.load(f)


def save_data(data):
    with open('data.json', 'w', encoding='utf-8') as f: json.dump(data, f, ensure_ascii=False, indent=2)


def calc_group(scores, matches, teams):
    stats = {k: {'name': teams[k], 'wins': 0, 'points': 0, 'net_points': 0} for k in teams}
    for match in matches:
        score_str = scores['group'].get(match, "")
        if not score_str: continue
        try:
            s1, s2 = map(int, score_str.split('-'))
            t1, t2 = match.split('_')
            stats[t1]['points'] += s1;
            stats[t1]['net_points'] += (s1 - s2)
            stats[t2]['points'] += s2;
            stats[t2]['net_points'] += (s2 - s1)
            if s1 > s2:
                stats[t1]['wins'] += 1
            elif s2 > s1:
                stats[t2]['wins'] += 1
        except:
            pass
    ranked = sorted(stats.items(), key=lambda x: (x[1]['wins'], x[1]['net_points'], x[1]['points']), reverse=True)
    return ranked


def resolve_match(score_str, t1_name, t2_name):
    if not score_str: return None, None
    try:
        s1, s2 = map(int, score_str.split('-'))
        return (t1_name, t2_name) if s1 > s2 else (t2_name, t1_name)
    except:
        return None, None


def calculate_all():
    data = load_data()
    teams = data['teams'];
    scores = data['scores']
    calc = {'ranks': {}, 'knockout_teams': {}, 'placement_teams': {}, 'final_standings': {},
            'placement_standings': {'top': {}, 'bot': {}}}

    a_ranked = calc_group(scores, ['a1_a2', 'a3_a4', 'a1_a3', 'a2_a4', 'a1_a4', 'a2_a3'],
                          {k: teams[k] for k in ['a1', 'a2', 'a3', 'a4']})
    b_ranked = calc_group(scores, ['b1_b2', 'b3_b4', 'b1_b3', 'b2_b4', 'b1_b4', 'b2_b3'],
                          {k: teams[k] for k in ['b1', 'b2', 'b3', 'b4']})

    for i in range(4):
        if i < len(a_ranked): calc['ranks'][f'A{i + 1}'] = a_ranked[i][1]
        if i < len(b_ranked): calc['ranks'][f'B{i + 1}'] = b_ranked[i][1]

    knockouts_map = {'A1_B4': ('A1', 'B4', 'C1', 'D1'), 'A4_B1': ('A4', 'B1', 'C4', 'D4'),
                     'A2_B3': ('A2', 'B3', 'C2', 'D2'), 'A3_B2': ('A3', 'B2', 'C3', 'D3')}
    for match, (t1_id, t2_id, w_id, l_id) in knockouts_map.items():
        t1_name = calc['ranks'].get(t1_id, {}).get('name', '')
        t2_name = calc['ranks'].get(t2_id, {}).get('name', '')
        calc['knockout_teams'][match] = {'t1': t1_name, 't2': t2_name}
        winner, loser = resolve_match(scores['knockout'].get(match, ""), t1_name, t2_name)
        if winner:
            calc['placement_teams'][w_id] = winner
            calc['placement_teams'][l_id] = loser

    def calc_placement(stage_key, matches, p_teams):
        stats = {k: {'name': p_teams.get(k, ''), 'wins': 0, 'points': 0, 'net_points': 0} for k in p_teams}
        for match in matches:
            score_str = scores[stage_key].get(match, "")
            if not score_str: continue
            try:
                s1, s2 = map(int, score_str.split('-'))
                t1, t2 = match.split('_')
                if t1 in stats: stats[t1]['net_points'] += (s1 - s2); stats[t1]['points'] += s1; stats[t1]['wins'] += (
                    1 if s1 > s2 else 0)
                if t2 in stats: stats[t2]['net_points'] += (s2 - s1); stats[t2]['points'] += s2; stats[t2]['wins'] += (
                    1 if s2 > s1 else 0)
            except:
                pass
        return sorted([(k, v) for k, v in stats.items() if v['name']],
                      key=lambda x: (x[1]['wins'], x[1]['net_points'], x[1]['points']), reverse=True)

    top_ranked = calc_placement('placement_top', ['C1_C2', 'C3_C4', 'C1_C3', 'C2_C4', 'C1_C4', 'C2_C3'],
                                {k: calc['placement_teams'].get(k, '') for k in ['C1', 'C2', 'C3', 'C4']})
    bot_ranked = calc_placement('placement_bot', ['D1_D2', 'D3_D4', 'D1_D3', 'D2_D4', 'D1_D4', 'D2_D3'],
                                {k: calc['placement_teams'].get(k, '') for k in ['D1', 'D2', 'D3', 'D4']})

    calc['placement_standings']['top'] = {item[0]: item[1] for item in top_ranked}
    calc['placement_standings']['bot'] = {item[0]: item[1] for item in bot_ranked}

    titles = ['冠军', '亚军', '季军', '殿军'];
    sub_titles = ['小冠军', '小亚军', '小季军', '小殿军']
    for i in range(min(4, len(top_ranked))): calc['final_standings'][titles[i]] = top_ranked[i][1]['name']
    for i in range(min(4, len(bot_ranked))): calc['final_standings'][sub_titles[i]] = bot_ranked[i][1]['name']

    data['calculated'] = calc
    save_data(data)


class AdminHTTPHandler(SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/api/update':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            req = json.loads(post_data.decode('utf-8'))

            data = load_data()
            stage = req.get('stage')
            match = req.get('match')
            score = req.get('score', '')

            if stage in data['scores'] and match in data['scores'][stage]:
                data['scores'][stage][match] = score
                save_data(data)
                calculate_all()

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"status":"success"}')
            else:
                self.send_response(400)
                self.end_headers()


if __name__ == '__main__':
    # Initialize calculations on start
    calculate_all()
    PORT = 8000
    print(f"==================================================")
    print(f"🚀 芝麻杯本地管理服务器已启动！")
    print(f"👉 后台管理请访问: http://localhost:{PORT}/admin.html")
    print(f"👉 观众大屏请访问: http://localhost:{PORT}/index.html")
    print(f"==================================================")
    server = HTTPServer(('', PORT), AdminHTTPHandler)
    server.serve_forever()