"""
ポーカーゲームエンジンとフィードバックシステム
"""
from typing import List, Dict, Optional
from game_logic import Deck, Card, HandEvaluator, HandRank, Rank
from player import Player, HumanPlayer, AIPlayer, PlayStyle, Action

class PokerGame:
    """テキサスホールデムポーカーゲーム"""
    
    STREETS = ['preflop', 'flop', 'turn', 'river']
    
    def __init__(self, player_name: str = "You"):
        self.deck = Deck()
        self.players: List[Player] = []
        self.community_cards: List[Card] = []
        self.pot = 0
        self.current_bet = 0
        self.dealer_position = 0
        self.small_blind = 10
        self.big_blind = 20
        self.current_street = 'preflop'
        self.hand_history: List[Dict] = []
        self.current_hand_data: Dict = {}
        
        # プレイヤー作成
        self.human_player = HumanPlayer(player_name, chips=1000)
        self.players.append(self.human_player)
        
        # AI作成（3人、異なるスタイル）
        self.players.append(AIPlayer("AI_Tight", 1000, PlayStyle.TIGHT))
        self.players.append(AIPlayer("AI_Loose", 1000, PlayStyle.LOOSE))
        self.players.append(AIPlayer("AI_Aggressive", 1000, PlayStyle.AGGRESSIVE))
    
    def start_new_hand(self):
        """新しいハンドを開始"""
        # プレイヤーリセット
        for player in self.players:
            player.reset_for_new_hand()
        
        # ゲーム状態リセット
        self.deck.reset()
        self.community_cards = []
        self.pot = 0
        self.current_bet = 0
        self.current_street = 'preflop'
        
        # ハンド記録初期化
        self.current_hand_data = {
            'hand_number': len(self.hand_history) + 1,
            'players': {p.name: {'chips_start': p.chips} for p in self.players},
            'actions': [],
            'streets': {},
            'pot_size': 0,
            'winner': None
        }
        
        # ディーラーポジション移動
        self.dealer_position = (self.dealer_position + 1) % len(self.players)
        
        # カード配布
        for player in self.players:
            player.receive_cards(self.deck.deal(2))
        
        # ブラインド
        self._post_blinds()
        
        # コミュニティカード記録
        self.current_hand_data['streets']['preflop'] = {
            'community_cards': [],
            'actions': []
        }
    
    def _post_blinds(self):
        """ブラインドを置く"""
        sb_pos = (self.dealer_position + 1) % len(self.players)
        bb_pos = (self.dealer_position + 2) % len(self.players)
        
        # スモールブラインド
        sb_player = self.players[sb_pos]
        sb_amount = sb_player.place_bet(self.small_blind)
        self.pot += sb_amount
        sb_player.record_action(Action.RAISE, sb_amount, 'preflop', 'Small Blind')
        
        # ビッグブラインド
        bb_player = self.players[bb_pos]
        bb_amount = bb_player.place_bet(self.big_blind)
        self.pot += bb_amount
        self.current_bet = self.big_blind
        bb_player.record_action(Action.RAISE, bb_amount, 'preflop', 'Big Blind')
    
    def betting_round(self, street: str) -> bool:
        """
        ベッティングラウンド
        Returns: ゲームが続行するかどうか
        """
        self.current_street = street
        self.current_bet = 0
        
        # 全員のcurrent_betをリセット
        for player in self.players:
            player.current_bet = 0
        
        # アクティブプレイヤーの数を確認
        active_players = [p for p in self.players if not p.is_folded and not p.is_all_in]
        
        if len(active_players) <= 1:
            return False
        
        # ベッティング順序を決定
        first_to_act = (self.dealer_position + 1) % len(self.players)
        if street == 'preflop':
            first_to_act = (self.dealer_position + 3) % len(self.players)  # UTG
        
        betting_complete = False
        last_raiser = None
        action_count = 0
        max_actions = len(self.players) * 3  # 無限ループ防止
        
        current_player_idx = first_to_act
        
        while not betting_complete and action_count < max_actions:
            player = self.players[current_player_idx]
            
            # このプレイヤーがアクション可能か
            if not player.can_bet():
                current_player_idx = (current_player_idx + 1) % len(self.players)
                continue
            
            # 全員がベット額に達しているかチェック
            if last_raiser is not None:
                if current_player_idx == last_raiser:
                    betting_complete = True
                    break
            
            # AIの行動決定またはプレイヤーの入力待ち
            if player.is_human:
                # この部分はWeb UIから呼ばれる想定
                return True  # UIでの入力待ち
            else:
                action, amount, reason = player.decide_action(self._get_game_state())
                
                if action == Action.FOLD:
                    player.is_folded = True
                    player.record_action(action, 0, street, reason)
                    self._record_action(player.name, action, 0, reason)
                
                elif action == Action.CHECK:
                    player.record_action(action, 0, street, reason)
                    self._record_action(player.name, action, 0, reason)
                
                elif action == Action.CALL:
                    call_amount = self.current_bet - player.current_bet
                    actual_bet = player.place_bet(call_amount)
                    self.pot += actual_bet
                    player.record_action(action, actual_bet, street, reason)
                    self._record_action(player.name, action, actual_bet, reason)
                
                elif action == Action.RAISE or action == Action.ALL_IN:
                    actual_bet = player.place_bet(amount)
                    self.pot += actual_bet
                    self.current_bet = player.current_bet
                    last_raiser = current_player_idx
                    player.record_action(action, actual_bet, street, reason)
                    self._record_action(player.name, action, actual_bet, reason)
            
            action_count += 1
            current_player_idx = (current_player_idx + 1) % len(self.players)
            
            # 全員フォールドまたはオールインチェック
            active_players = [p for p in self.players if not p.is_folded and not p.is_all_in]
            if len(active_players) <= 1:
                return False
        
        return True
    
    def deal_community_cards(self, count: int):
        """コミュニティカードを配る"""
        new_cards = self.deck.deal(count)
        self.community_cards.extend(new_cards)
        
        # 記録
        self.current_hand_data['streets'][self.current_street] = {
            'community_cards': [str(c) for c in self.community_cards],
            'actions': []
        }
    
    def showdown(self) -> Dict:
        """ショーダウンして勝者を決定"""
        active_players = [p for p in self.players if not p.is_folded]
        
        if len(active_players) == 1:
            winner = active_players[0]
            winner.win_pot(self.pot)
            result = {
                'winner': winner.name,
                'winning_hand': None,
                'pot': self.pot
            }
        else:
            # 各プレイヤーのハンドを評価
            player_hands = []
            for player in active_players:
                all_cards = player.hand + self.community_cards
                hand_rank, kickers, hand_name = HandEvaluator.evaluate(all_cards)
                player_hands.append({
                    'player': player,
                    'hand_rank': hand_rank,
                    'kickers': kickers,
                    'hand_name': hand_name,
                    'cards': player.hand
                })
            
            # 最強ハンドを見つける
            player_hands.sort(key=lambda x: (x['hand_rank'], x['kickers']), reverse=True)
            winner = player_hands[0]['player']
            winner.win_pot(self.pot)
            
            result = {
                'winner': winner.name,
                'winning_hand': player_hands[0]['hand_name'],
                'pot': self.pot,
                'all_hands': [{
                    'player': ph['player'].name,
                    'hand': [str(c) for c in ph['cards']],
                    'hand_name': ph['hand_name']
                } for ph in player_hands]
            }
        
        # ハンド履歴に記録
        self.current_hand_data['winner'] = result['winner']
        self.current_hand_data['pot_size'] = self.pot
        self.current_hand_data['result'] = result
        
        for player in self.players:
            self.current_hand_data['players'][player.name]['chips_end'] = player.chips
            self.current_hand_data['players'][player.name]['hand'] = [str(c) for c in player.hand]
            self.current_hand_data['players'][player.name]['actions'] = player.actions_history
        
        self.hand_history.append(self.current_hand_data)
        
        return result
    
    def _get_game_state(self) -> Dict:
        """現在のゲーム状態を取得"""
        return {
            'street': self.current_street,
            'pot': self.pot,
            'current_bet': self.current_bet,
            'community_cards': self.community_cards,
            'position': 'button'  # 簡易版
        }
    
    def _record_action(self, player_name: str, action: Action, amount: int, reason: str):
        """アクションを記録"""
        if self.current_street in self.current_hand_data['streets']:
            self.current_hand_data['streets'][self.current_street]['actions'].append({
                'player': player_name,
                'action': action.value,
                'amount': amount,
                'reason': reason
            })
    
    def get_player_stats(self, player_name: str) -> Dict:
        """プレイヤーの統計を取得"""
        player_hands = [h for h in self.hand_history if player_name in h['players']]
        
        if not player_hands:
            return {}
        
        total_hands = len(player_hands)
        hands_played = 0
        hands_won = 0
        total_profit = 0
        preflop_raises = 0
        folds = 0
        
        for hand in player_hands:
            player_data = hand['players'][player_name]
            
            # 参加したハンド
            if player_data['actions']:
                hands_played += 1
                
                # プリフロップレイズ
                preflop_actions = [a for a in player_data['actions'] if a['street'] == 'preflop']
                if any(a['action'] == Action.RAISE for a in preflop_actions):
                    preflop_raises += 1
                
                # フォールド
                if any(a['action'] == Action.FOLD for a in player_data['actions']):
                    folds += 1
            
            # 勝利
            if hand['winner'] == player_name:
                hands_won += 1
            
            # 利益計算
            profit = player_data['chips_end'] - player_data['chips_start']
            total_profit += profit
        
        vpip = (hands_played / total_hands * 100) if total_hands > 0 else 0
        pfr = (preflop_raises / total_hands * 100) if total_hands > 0 else 0
        win_rate = (hands_won / hands_played * 100) if hands_played > 0 else 0
        
        return {
            'total_hands': total_hands,
            'hands_played': hands_played,
            'hands_won': hands_won,
            'vpip': round(vpip, 1),
            'pfr': round(pfr, 1),
            'win_rate': round(win_rate, 1),
            'total_profit': total_profit,
            'fold_rate': round((folds / hands_played * 100) if hands_played > 0 else 0, 1)
        }


class FeedbackEngine:
    """フィードバックエンジン"""
    
    @staticmethod
    def analyze_hand(hand_data: Dict, player_name: str) -> Dict:
        """ハンドを分析してフィードバックを生成"""
        player_data = hand_data['players'][player_name]
        actions = player_data['actions']
        
        feedback = {
            'hand_number': hand_data['hand_number'],
            'result': 'Won' if hand_data['winner'] == player_name else 'Lost',
            'profit': player_data['chips_end'] - player_data['chips_start'],
            'starting_hand': player_data['hand'],
            'good_plays': [],
            'bad_plays': [],
            'suggestions': []
        }
        
        # プリフロップ分析
        preflop_actions = [a for a in actions if a['street'] == 'preflop']
        feedback.update(FeedbackEngine._analyze_preflop(player_data['hand'], preflop_actions))
        
        # ポストフロップ分析
        for street in ['flop', 'turn', 'river']:
            street_actions = [a for a in actions if a['street'] == street]
            if street_actions:
                street_feedback = FeedbackEngine._analyze_street(
                    player_data['hand'],
                    hand_data['streets'].get(street, {}).get('community_cards', []),
                    street_actions,
                    street
                )
                feedback['good_plays'].extend(street_feedback['good'])
                feedback['bad_plays'].extend(street_feedback['bad'])
                feedback['suggestions'].extend(street_feedback['suggestions'])
        
        return feedback
    
    @staticmethod
    def _analyze_preflop(hole_cards: List[str], actions: List[Dict]) -> Dict:
        """プリフロップ分析"""
        feedback = {'good_plays': [], 'bad_plays': [], 'suggestions': []}
        
        # ハンド強度評価（簡易版）
        hand_strength = FeedbackEngine._estimate_hand_strength(hole_cards)
        
        if not actions:
            return feedback
        
        first_action = actions[0]
        
        # 強いハンドでの分析
        if hand_strength > 0.7:
            if first_action['action'] == Action.RAISE.value:
                feedback['good_plays'].append({
                    'street': 'preflop',
                    'comment': f"プレミアムハンド（{', '.join(hole_cards)}）で適切にレイズしました"
                })
            elif first_action['action'] == Action.CALL.value:
                feedback['bad_plays'].append({
                    'street': 'preflop',
                    'comment': f"強いハンド（{', '.join(hole_cards)}）ではレイズを検討すべきでした"
                })
                feedback['suggestions'].append("プレミアムハンドは積極的にレイズしてポットを大きくしましょう")
        
        # 弱いハンドでの分析
        elif hand_strength < 0.3:
            if first_action['action'] == Action.FOLD.value:
                feedback['good_plays'].append({
                    'street': 'preflop',
                    'comment': f"弱いハンド（{', '.join(hole_cards)}）を適切にフォールドしました"
                })
            elif first_action['action'] in [Action.CALL.value, Action.RAISE.value]:
                feedback['bad_plays'].append({
                    'street': 'preflop',
                    'comment': f"弱いハンド（{', '.join(hole_cards)}）での参加はリスクが高いです"
                })
                feedback['suggestions'].append("プリフロップでは強いハンドを選んで参加しましょう")
        
        return feedback
    
    @staticmethod
    def _analyze_street(hole_cards: List[str], community_cards: List[str], actions: List[Dict], street: str) -> Dict:
        """各ストリートの分析"""
        feedback = {'good': [], 'bad': [], 'suggestions': []}
        
        # アグレッションのチェック
        has_bet_or_raise = any(a['action'] in [Action.RAISE.value, Action.ALL_IN.value] for a in actions)
        has_fold = any(a['action'] == Action.FOLD.value for a in actions)
        
        if has_bet_or_raise:
            feedback['good'].append({
                'street': street,
                'comment': f"{street.capitalize()}で積極的にプレイしました"
            })
        
        if has_fold:
            # フォールドが適切かどうかの簡易判定
            if len(actions) > 2:  # 複数のアクション後にフォールド
                feedback['good'].append({
                    'street': street,
                    'comment': f"{street.capitalize()}で状況を見て適切にフォールドしました"
                })
        
        return feedback
    
    @staticmethod
    def _estimate_hand_strength(hole_cards: List[str]) -> float:
        """ハンド強度の簡易推定（0.0 ~ 1.0）"""
        # 文字列からカードを解析
        ranks = []
        suits = []
        
        for card_str in hole_cards:
            if len(card_str) == 3:  # "10♠"のような場合
                rank_str = card_str[:2]
                suit_str = card_str[2]
            else:
                rank_str = card_str[0]
                suit_str = card_str[1]
            
            rank_map = {'A': 14, 'K': 13, 'Q': 12, 'J': 11, '10': 10}
            rank = rank_map.get(rank_str, int(rank_str) if rank_str.isdigit() else 10)
            ranks.append(rank)
            suits.append(suit_str)
        
        # ペア
        if ranks[0] == ranks[1]:
            return 0.5 + (ranks[0] / 28.0)  # 0.5 ~ 1.0
        
        # ハイカード強度
        high_rank = max(ranks)
        base_strength = high_rank / 28.0  # 0.0 ~ 0.5
        
        # スーテッドボーナス
        if suits[0] == suits[1]:
            base_strength += 0.05
        
        # コネクテッドボーナス
        if abs(ranks[0] - ranks[1]) <= 2:
            base_strength += 0.05
        
        return min(base_strength, 1.0)
    
    @staticmethod
    def generate_session_report(game: PokerGame, player_name: str) -> Dict:
        """セッション全体のレポート生成"""
        stats = game.get_player_stats(player_name)
        
        # 各ハンドのフィードバック
        hand_feedbacks = []
        for hand_data in game.hand_history:
            if player_name in hand_data['players']:
                feedback = FeedbackEngine.analyze_hand(hand_data, player_name)
                hand_feedbacks.append(feedback)
        
        # 総合評価
        report = {
            'statistics': stats,
            'hand_feedbacks': hand_feedbacks,
            'overall_assessment': FeedbackEngine._generate_overall_assessment(stats, hand_feedbacks)
        }
        
        return report
    
    @staticmethod
    def _generate_overall_assessment(stats: Dict, feedbacks: List[Dict]) -> Dict:
        """総合評価生成"""
        assessment = {
            'strengths': [],
            'weaknesses': [],
            'recommendations': []
        }
        
        # VPIP分析
        vpip = stats.get('vpip', 0)
        if vpip < 20:
            assessment['strengths'].append("非常にタイトなプレイスタイル（参加率が低い）")
            assessment['recommendations'].append("もう少し多くのハンドに参加してポットを獲得するチャンスを増やしましょう")
        elif vpip > 40:
            assessment['weaknesses'].append("ルースすぎるプレイスタイル（参加率が高すぎ）")
            assessment['recommendations'].append("ハンド選択を厳しくして、強いハンドのみに参加しましょう")
        else:
            assessment['strengths'].append("適切な参加率でプレイしています")
        
        # 勝率分析
        win_rate = stats.get('win_rate', 0)
        if win_rate > 40:
            assessment['strengths'].append("高い勝率を維持しています")
        elif win_rate < 20:
            assessment['weaknesses'].append("勝率が低いです")
            assessment['recommendations'].append("ハンド選択とポジショニングを見直しましょう")
        
        # フォールド率分析
        fold_rate = stats.get('fold_rate', 0)
        if fold_rate > 60:
            assessment['weaknesses'].append("フォールド率が高すぎます")
            assessment['recommendations'].append("もっと積極的にプレイして、ブラインドを守りましょう")
        
        # フィードバック集計
        total_good = sum(len(f['good_plays']) for f in feedbacks)
        total_bad = sum(len(f['bad_plays']) for f in feedbacks)
        
        if total_good > total_bad:
            assessment['strengths'].append("全体的に良い判断が多いです")
        elif total_bad > total_good:
            assessment['recommendations'].append("判断の精度を上げるため、各ストリートでの戦略を見直しましょう")
        
        return assessment
