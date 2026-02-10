"""
テキサスホールデムポーカー - ゲームロジック
"""
import random
from enum import IntEnum
from typing import List, Tuple, Dict
from collections import Counter

class Suit(IntEnum):
    """スート（マーク）"""
    HEARTS = 0    # ♥
    DIAMONDS = 1  # ♦
    CLUBS = 2     # ♣
    SPADES = 3    # ♠

class Rank(IntEnum):
    """ランク（数字）"""
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14

class Card:
    """トランプカード"""
    SUIT_SYMBOLS = {
        Suit.HEARTS: '♥',
        Suit.DIAMONDS: '♦',
        Suit.CLUBS: '♣',
        Suit.SPADES: '♠'
    }
    
    RANK_SYMBOLS = {
        Rank.TWO: '2', Rank.THREE: '3', Rank.FOUR: '4', Rank.FIVE: '5',
        Rank.SIX: '6', Rank.SEVEN: '7', Rank.EIGHT: '8', Rank.NINE: '9',
        Rank.TEN: '10', Rank.JACK: 'J', Rank.QUEEN: 'Q', 
        Rank.KING: 'K', Rank.ACE: 'A'
    }
    
    def __init__(self, rank: Rank, suit: Suit):
        self.rank = rank
        self.suit = suit
    
    def __str__(self):
        return f"{self.RANK_SYMBOLS[self.rank]}{self.SUIT_SYMBOLS[self.suit]}"
    
    def __repr__(self):
        return str(self)
    
    def __eq__(self, other):
        return self.rank == other.rank and self.suit == other.suit
    
    def __hash__(self):
        return hash((self.rank, self.suit))

class Deck:
    """トランプデッキ"""
    def __init__(self):
        self.cards = []
        self.reset()
    
    def reset(self):
        """デッキをリセット"""
        self.cards = [Card(rank, suit) for suit in Suit for rank in Rank]
        self.shuffle()
    
    def shuffle(self):
        """シャッフル"""
        random.shuffle(self.cards)
    
    def deal(self, count: int = 1) -> List[Card]:
        """カードを配る"""
        dealt = self.cards[:count]
        self.cards = self.cards[count:]
        return dealt

class HandRank(IntEnum):
    """ハンドの強さ"""
    HIGH_CARD = 1
    ONE_PAIR = 2
    TWO_PAIR = 3
    THREE_OF_A_KIND = 4
    STRAIGHT = 5
    FLUSH = 6
    FULL_HOUSE = 7
    FOUR_OF_A_KIND = 8
    STRAIGHT_FLUSH = 9
    ROYAL_FLUSH = 10

class HandEvaluator:
    """ハンド評価クラス"""
    
    HAND_NAMES = {
        HandRank.HIGH_CARD: "ハイカード",
        HandRank.ONE_PAIR: "ワンペア",
        HandRank.TWO_PAIR: "ツーペア",
        HandRank.THREE_OF_A_KIND: "スリーカード",
        HandRank.STRAIGHT: "ストレート",
        HandRank.FLUSH: "フラッシュ",
        HandRank.FULL_HOUSE: "フルハウス",
        HandRank.FOUR_OF_A_KIND: "フォーカード",
        HandRank.STRAIGHT_FLUSH: "ストレートフラッシュ",
        HandRank.ROYAL_FLUSH: "ロイヤルフラッシュ"
    }
    
    @staticmethod
    def evaluate(cards: List[Card]) -> Tuple[HandRank, List[int], str]:
        """
        7枚のカードから最強の5枚の役を評価
        Returns: (役のランク, キッカー値のリスト, 役の名前)
        """
        if len(cards) != 7:
            raise ValueError("7枚のカードが必要です")
        
        # 全ての5枚の組み合わせを評価
        from itertools import combinations
        best_hand = (HandRank.HIGH_CARD, [], "")
        
        for five_cards in combinations(cards, 5):
            hand = HandEvaluator._evaluate_five_cards(list(five_cards))
            if hand > best_hand:
                best_hand = hand
        
        return best_hand
    
    @staticmethod
    def _evaluate_five_cards(cards: List[Card]) -> Tuple[HandRank, List[int], str]:
        """5枚のカードを評価"""
        ranks = sorted([card.rank for card in cards], reverse=True)
        suits = [card.suit for card in cards]
        rank_counts = Counter(ranks)
        
        is_flush = len(set(suits)) == 1
        is_straight = HandEvaluator._is_straight(ranks)
        
        # ロイヤルフラッシュ
        if is_flush and is_straight and ranks[0] == Rank.ACE:
            return (HandRank.ROYAL_FLUSH, ranks, HandEvaluator.HAND_NAMES[HandRank.ROYAL_FLUSH])
        
        # ストレートフラッシュ
        if is_flush and is_straight:
            return (HandRank.STRAIGHT_FLUSH, ranks, HandEvaluator.HAND_NAMES[HandRank.STRAIGHT_FLUSH])
        
        # フォーカード
        if 4 in rank_counts.values():
            four_kind = [r for r, c in rank_counts.items() if c == 4][0]
            kicker = [r for r in ranks if r != four_kind]
            return (HandRank.FOUR_OF_A_KIND, [four_kind] + kicker, HandEvaluator.HAND_NAMES[HandRank.FOUR_OF_A_KIND])
        
        # フルハウス
        if 3 in rank_counts.values() and 2 in rank_counts.values():
            three_kind = [r for r, c in rank_counts.items() if c == 3][0]
            pair = [r for r, c in rank_counts.items() if c == 2][0]
            return (HandRank.FULL_HOUSE, [three_kind, pair], HandEvaluator.HAND_NAMES[HandRank.FULL_HOUSE])
        
        # フラッシュ
        if is_flush:
            return (HandRank.FLUSH, ranks, HandEvaluator.HAND_NAMES[HandRank.FLUSH])
        
        # ストレート
        if is_straight:
            return (HandRank.STRAIGHT, ranks, HandEvaluator.HAND_NAMES[HandRank.STRAIGHT])
        
        # スリーカード
        if 3 in rank_counts.values():
            three_kind = [r for r, c in rank_counts.items() if c == 3][0]
            kickers = sorted([r for r in ranks if r != three_kind], reverse=True)
            return (HandRank.THREE_OF_A_KIND, [three_kind] + kickers, HandEvaluator.HAND_NAMES[HandRank.THREE_OF_A_KIND])
        
        # ツーペア
        pairs = [r for r, c in rank_counts.items() if c == 2]
        if len(pairs) == 2:
            pairs = sorted(pairs, reverse=True)
            kicker = [r for r in ranks if r not in pairs]
            return (HandRank.TWO_PAIR, pairs + kicker, HandEvaluator.HAND_NAMES[HandRank.TWO_PAIR])
        
        # ワンペア
        if len(pairs) == 1:
            kickers = sorted([r for r in ranks if r != pairs[0]], reverse=True)
            return (HandRank.ONE_PAIR, [pairs[0]] + kickers, HandEvaluator.HAND_NAMES[HandRank.ONE_PAIR])
        
        # ハイカード
        return (HandRank.HIGH_CARD, ranks, HandEvaluator.HAND_NAMES[HandRank.HIGH_CARD])
    
    @staticmethod
    def _is_straight(ranks: List[int]) -> bool:
        """ストレート判定（Aは1としても14としても使える）"""
        sorted_ranks = sorted(ranks, reverse=True)
        
        # 通常のストレート
        if sorted_ranks[0] - sorted_ranks[4] == 4 and len(set(sorted_ranks)) == 5:
            return True
        
        # A-2-3-4-5のストレート（ホイール）
        if sorted_ranks == [14, 5, 4, 3, 2]:
            return True
        
        return False
