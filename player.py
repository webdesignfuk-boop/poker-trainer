"""
プレイヤーとAIの実装
"""
from typing import List, Optional, Dict
from enum import Enum
from game_logic import Card, HandEvaluator, Rank
import random

class Action(Enum):
    """アクション種別"""
    FOLD = "fold"
    CHECK = "check"
    CALL = "call"
    RAISE = "raise"
    ALL_IN = "all_in"

class PlayStyle(Enum):
    """プレイスタイル"""
    TIGHT = "tight"        # タイト（保守的）
    LOOSE = "loose"        # ルース（積極的参加）
    AGGRESSIVE = "aggressive"  # アグレッシブ（攻撃的）

class Player:
    """プレイヤー基底クラス"""
    def __init__(self, name: str, chips: int = 1000):
        self.name = name
        self.chips = chips
        self.hand: List[Card] = []
        self.current_bet = 0
        self.total_bet_this_hand = 0
        self.is_folded = False
        self.is_all_in = False
        self.actions_history: List[Dict] = []
    
    def receive_cards(self, cards: List[Card]):
        """カードを受け取る"""
        self.hand = cards
    
    def reset_for_new_hand(self):
        """新しいハンド用にリセット"""
        self.hand = []
        self.current_bet = 0
        self.total_bet_this_hand = 0
        self.is_folded = False
        self.is_all_in = False
        self.actions_history = []
    
    def place_bet(self, amount: int) -> int:
        """ベットを置く"""
        actual_bet = min(amount, self.chips)
        self.chips -= actual_bet
        self.current_bet += actual_bet
        self.total_bet_this_hand += actual_bet
        
        if self.chips == 0:
            self.is_all_in = True
        
        return actual_bet
    
    def win_pot(self, amount: int):
        """ポットを獲得"""
        self.chips += amount
    
    def can_bet(self) -> bool:
        """ベット可能か"""
        return self.chips > 0 and not self.is_folded and not self.is_all_in
    
    def record_action(self, action: Action, amount: int, street: str, reason: str = ""):
        """アクション履歴を記録"""
        self.actions_history.append({
            'action': action,
            'amount': amount,
            'street': street,
            'reason': reason,
            'hand': [str(c) for c in self.hand] if self.hand else []
        })

class HumanPlayer(Player):
    """人間プレイヤー"""
    def __init__(self, name: str = "You", chips: int = 1000):
        super().__init__(name, chips)
        self.is_human = True

class AIPlayer(Player):
    """AIプレイヤー"""
    def __init__(self, name: str, chips: int, play_style: PlayStyle):
        super().__init__(name, chips)
        self.play_style = play_style
        self.is_human = False
        
        # スタイル別パラメータ
        if play_style == PlayStyle.TIGHT:
            self.vpip = 0.20  # 参加率20%
            self.aggression = 0.3  # レイズ頻度30%
            self.bluff_freq = 0.05  # ブラフ頻度5%
        elif play_style == PlayStyle.LOOSE:
            self.vpip = 0.45  # 参加率45%
            self.aggression = 0.25  # レイズ頻度25%
            self.bluff_freq = 0.15  # ブラフ頻度15%
        else:  # AGGRESSIVE
            self.vpip = 0.35  # 参加率35%
            self.aggression = 0.60  # レイズ頻度60%
            self.bluff_freq = 0.25  # ブラフ頻度25%
    
    def decide_action(self, game_state: Dict) -> tuple[Action, int, str]:
        """
        AIの行動を決定
        Returns: (アクション, 金額, 判断理由)
        """
        street = game_state['street']
        pot_size = game_state['pot']
        current_bet = game_state['current_bet']
        call_amount = current_bet - self.current_bet
        community_cards = game_state['community_cards']
        
        # ハンド強度を評価
        if len(community_cards) >= 3:
            all_cards = self.hand + community_cards
            hand_rank, _, hand_name = HandEvaluator.evaluate(all_cards)
            hand_strength = hand_rank / 10.0  # 0.1 ~ 1.0に正規化
        else:
            # プリフロップのハンド強度
            hand_strength = self._evaluate_preflop_hand()
        
        # ポジション考慮（簡易版）
        position_bonus = 0.1 if game_state.get('position') == 'button' else 0
        adjusted_strength = hand_strength + position_bonus
        
        # プレイスタイルに応じた判断
        reason = ""
        
        # フォールド判定
        if call_amount > self.chips:
            # オールインが必要
            if adjusted_strength > 0.6:
                reason = f"強いハンド({hand_strength:.2f})でオールイン"
                return (Action.ALL_IN, self.chips, reason)
            else:
                reason = f"弱いハンド({hand_strength:.2f})でフォールド"
                self.is_folded = True
                return (Action.FOLD, 0, reason)
        
        # ポットオッズ計算
        pot_odds = call_amount / (pot_size + call_amount) if pot_size + call_amount > 0 else 0
        
        # ベット額が大きすぎる場合
        if call_amount > pot_size * 0.8 and adjusted_strength < 0.5:
            reason = f"大きなベット(${call_amount})に対して弱いハンド({hand_strength:.2f})"
            self.is_folded = True
            return (Action.FOLD, 0, reason)
        
        # チェック可能な場合
        if call_amount == 0:
            # ブラフレイズ
            if random.random() < self.bluff_freq:
                raise_amount = int(pot_size * 0.5)
                if raise_amount <= self.chips:
                    reason = f"ブラフレイズ(ポットの50%)"
                    return (Action.RAISE, raise_amount, reason)
            
            # バリューベット
            if adjusted_strength > 0.6 and random.random() < self.aggression:
                raise_amount = int(pot_size * 0.7)
                if raise_amount <= self.chips:
                    reason = f"強いハンド({hand_strength:.2f})でバリューベット"
                    return (Action.RAISE, raise_amount, reason)
            
            reason = "チェックで様子見"
            return (Action.CHECK, 0, reason)
        
        # コール or レイズ or フォールド判断
        if adjusted_strength > 0.7:
            # 強いハンド：レイズ
            if random.random() < self.aggression:
                raise_amount = call_amount + int(pot_size * 0.6)
                if raise_amount <= self.chips:
                    reason = f"強いハンド({hand_strength:.2f})でレイズ"
                    return (Action.RAISE, raise_amount, reason)
            reason = f"強いハンド({hand_strength:.2f})でコール"
            return (Action.CALL, call_amount, reason)
        
        elif adjusted_strength > 0.4:
            # 中程度のハンド：ポットオッズ次第
            if pot_odds < 0.3 or random.random() < 0.6:
                reason = f"中程度のハンド({hand_strength:.2f})でコール"
                return (Action.CALL, call_amount, reason)
            else:
                reason = f"中程度のハンド({hand_strength:.2f})だがポットオッズ悪い"
                self.is_folded = True
                return (Action.FOLD, 0, reason)
        
        else:
            # 弱いハンド
            if call_amount < pot_size * 0.2 and random.random() < 0.3:
                reason = f"弱いハンド({hand_strength:.2f})だが安いのでコール"
                return (Action.CALL, call_amount, reason)
            else:
                reason = f"弱いハンド({hand_strength:.2f})でフォールド"
                self.is_folded = True
                return (Action.FOLD, 0, reason)
    
    def _evaluate_preflop_hand(self) -> float:
        """プリフロップのハンド評価（0.0 ~ 1.0）"""
        if len(self.hand) != 2:
            return 0.5
        
        card1, card2 = self.hand
        rank1, rank2 = card1.rank, card2.rank
        
        # ペア
        if rank1 == rank2:
            pair_strength = {
                Rank.ACE: 1.0, Rank.KING: 0.95, Rank.QUEEN: 0.90,
                Rank.JACK: 0.85, Rank.TEN: 0.80, Rank.NINE: 0.70,
                Rank.EIGHT: 0.65, Rank.SEVEN: 0.60, Rank.SIX: 0.55,
            }
            return pair_strength.get(rank1, 0.50)
        
        # ハイカード
        high_rank = max(rank1, rank2)
        low_rank = min(rank1, rank2)
        
        # AK, AQなどのプレミアムハンド
        if high_rank == Rank.ACE:
            if low_rank >= Rank.KING:
                return 0.85
            elif low_rank >= Rank.JACK:
                return 0.75
            else:
                return 0.60
        
        if high_rank == Rank.KING:
            if low_rank >= Rank.QUEEN:
                return 0.75
            elif low_rank >= Rank.JACK:
                return 0.65
            else:
                return 0.50
        
        # スーテッドボーナス
        suited_bonus = 0.05 if card1.suit == card2.suit else 0
        
        # コネクテッドボーナス
        connected_bonus = 0.05 if abs(rank1 - rank2) <= 2 else 0
        
        base_strength = (high_rank / 14.0) * 0.6
        return min(base_strength + suited_bonus + connected_bonus, 1.0)
