"""
Flaskサーバー - ポーカートレーナー
"""
from flask import Flask, jsonify, request, send_from_directory
from game_engine import PokerGame, FeedbackEngine
from player import Action
import os

app = Flask(__name__)
game = None

@app.route('/')
def index():
    """メインページ"""
    return send_from_directory('.', 'index.html')

@app.route('/api/start_hand', methods=['POST'])
def start_hand():
    """新しいハンドを開始"""
    global game
    
    if game is None:
        game = PokerGame("You")
    
    game.start_new_hand()
    
    return jsonify(get_game_state())

@app.route('/api/player_action', methods=['POST'])
def player_action():
    """プレイヤーのアクション処理"""
    global game
    
    if game is None:
        return jsonify({'error': 'Game not started'}), 400
    
    data = request.json
    action_type = data.get('action')
    amount = data.get('amount', 0)
    
    player = game.human_player
    
    # アクション実行
    if action_type == 'fold':
        player.is_folded = True
        player.record_action(Action.FOLD, 0, game.current_street, "Player folded")
        game._record_action(player.name, Action.FOLD, 0, "Player decision")
    
    elif action_type == 'check':
        player.record_action(Action.CHECK, 0, game.current_street, "Player checked")
        game._record_action(player.name, Action.CHECK, 0, "Player decision")
    
    elif action_type == 'call':
        actual_bet = player.place_bet(amount)
        game.pot += actual_bet
        player.record_action(Action.CALL, actual_bet, game.current_street, "Player called")
        game._record_action(player.name, Action.CALL, actual_bet, "Player decision")
    
    elif action_type == 'raise':
        actual_bet = player.place_bet(amount)
        game.pot += actual_bet
        game.current_bet = player.current_bet
        player.record_action(Action.RAISE, actual_bet, game.current_street, "Player raised")
        game._record_action(player.name, Action.RAISE, actual_bet, "Player decision")
    
    # ベッティングラウンド完了チェック
    active_players = [p for p in game.players if not p.is_folded and not p.is_all_in]
    
    if len(active_players) <= 1:
        # ゲーム終了
        result = game.showdown()
        return jsonify({
            **get_game_state(),
            'game_over': True,
            'result': result
        })
    
    # 全員がベットに同意したかチェック
    all_bets_equal = all(
        p.current_bet == game.current_bet or p.is_folded or p.is_all_in
        for p in game.players
    )
    
    if all_bets_equal:
        # 次のストリートへ
        return jsonify({
            **get_game_state(),
            'hand_complete': True
        })
    
    return jsonify(get_game_state())

@app.route('/api/process_ai', methods=['GET'])
def process_ai():
    """AIのアクションを処理"""
    global game
    
    if game is None:
        return jsonify({'error': 'Game not started'}), 400
    
    actions_taken = []
    
    # 各AIプレイヤーのアクション
    for player in game.players:
        if player.is_human or player.is_folded or player.is_all_in:
            continue
        
        # 既にベットが揃っているかチェック
        if player.current_bet == game.current_bet:
            continue
        
        action, amount, reason = player.decide_action(game._get_game_state())
        
        if action == Action.FOLD:
            player.is_folded = True
            player.record_action(action, 0, game.current_street, reason)
            game._record_action(player.name, action, 0, reason)
        
        elif action == Action.CHECK:
            player.record_action(action, 0, game.current_street, reason)
            game._record_action(player.name, action, 0, reason)
        
        elif action == Action.CALL:
            call_amount = game.current_bet - player.current_bet
            actual_bet = player.place_bet(call_amount)
            game.pot += actual_bet
            player.record_action(action, actual_bet, game.current_street, reason)
            game._record_action(player.name, action, actual_bet, reason)
        
        elif action == Action.RAISE or action == Action.ALL_IN:
            actual_bet = player.place_bet(amount)
            game.pot += actual_bet
            game.current_bet = player.current_bet
            player.record_action(action, actual_bet, game.current_street, reason)
            game._record_action(player.name, action, actual_bet, reason)
        
        actions_taken.append({
            'player': player.name,
            'action': action.value,
            'amount': amount,
            'reason': reason
        })
    
    # アクティブプレイヤーチェック
    active_players = [p for p in game.players if not p.is_folded and not p.is_all_in]
    
    if len(active_players) <= 1:
        result = game.showdown()
        return jsonify({
            **get_game_state(),
            'actions': actions_taken,
            'game_over': True,
            'result': result
        })
    
    # 全員がベットに同意したかチェック
    all_bets_equal = all(
        p.current_bet == game.current_bet or p.is_folded or p.is_all_in
        for p in game.players
    )
    
    if all_bets_equal:
        return jsonify({
            **get_game_state(),
            'actions': actions_taken,
            'hand_complete': True
        })
    
    # プレイヤーのターン
    if not game.human_player.is_folded and not game.human_player.is_all_in:
        if game.human_player.current_bet < game.current_bet:
            return jsonify({
                **get_game_state(),
                'actions': actions_taken,
                'waiting_for_player': True
            })
    
    return jsonify({
        **get_game_state(),
        'actions': actions_taken
    })

@app.route('/api/next_street', methods=['POST'])
def next_street():
    """次のストリートへ進む"""
    global game
    
    if game is None:
        return jsonify({'error': 'Game not started'}), 400
    
    # 全員のcurrent_betリセット
    for player in game.players:
        player.current_bet = 0
    game.current_bet = 0
    
    # ストリート進行
    streets = ['preflop', 'flop', 'turn', 'river']
    current_idx = streets.index(game.current_street)
    
    if current_idx < len(streets) - 1:
        next_street_name = streets[current_idx + 1]
        game.current_street = next_street_name
        
        # カード配布
        if next_street_name == 'flop':
            game.deal_community_cards(3)
        elif next_street_name in ['turn', 'river']:
            game.deal_community_cards(1)
        
        return jsonify({
            **get_game_state(),
            'street': next_street_name
        })
    else:
        # ショーダウン
        result = game.showdown()
        return jsonify({
            **get_game_state(),
            'game_over': True,
            'result': result
        })

@app.route('/api/feedback', methods=['GET'])
def get_feedback():
    """フィードバックを取得"""
    global game
    
    if game is None or not game.hand_history:
        return jsonify({'error': 'No game data'}), 400
    
    report = FeedbackEngine.generate_session_report(game, "You")
    
    return jsonify(report)

def get_game_state():
    """現在のゲーム状態を取得"""
    return {
        'pot': game.pot,
        'current_bet': game.current_bet,
        'community_cards': [str(c) for c in game.community_cards],
        'players': {
            player.name: {
                'chips': player.chips,
                'current_bet': player.current_bet,
                'is_folded': player.is_folded,
                'is_all_in': player.is_all_in,
                'hand': [str(c) for c in player.hand] if player.is_human else None
            }
            for player in game.players
        },
        'street': game.current_street
    }

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False') == 'True'
    
    print("🃏 ポーカートレーナー起動中...")
    if debug:
        print("ブラウザで http://localhost:5000 を開いてください")
    
    app.run(debug=debug, host='0.0.0.0', port=port)
