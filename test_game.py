"""
ゲームロジックのテストスクリプト
"""
from game_logic import Deck, Card, HandEvaluator, HandRank, Suit, Rank
from player import HumanPlayer, AIPlayer, PlayStyle, Action
from game_engine import PokerGame, FeedbackEngine

def test_deck():
    """デッキのテスト"""
    print("=== デッキテスト ===")
    deck = Deck()
    print(f"デッキ枚数: {len(deck.cards)}")
    
    dealt_cards = deck.deal(5)
    print(f"配られたカード: {dealt_cards}")
    print(f"残りの枚数: {len(deck.cards)}")
    print("✓ デッキテスト完了\n")

def test_hand_evaluation():
    """ハンド評価のテスト"""
    print("=== ハンド評価テスト ===")
    
    # ロイヤルフラッシュ
    royal_flush = [
        Card(Rank.ACE, Suit.SPADES),
        Card(Rank.KING, Suit.SPADES),
        Card(Rank.QUEEN, Suit.SPADES),
        Card(Rank.JACK, Suit.SPADES),
        Card(Rank.TEN, Suit.SPADES),
        Card(Rank.NINE, Suit.HEARTS),
        Card(Rank.EIGHT, Suit.HEARTS)
    ]
    rank, kickers, name = HandEvaluator.evaluate(royal_flush)
    print(f"ロイヤルフラッシュ: {name} (ランク: {rank})")
    
    # フォーカード
    four_kind = [
        Card(Rank.ACE, Suit.SPADES),
        Card(Rank.ACE, Suit.HEARTS),
        Card(Rank.ACE, Suit.DIAMONDS),
        Card(Rank.ACE, Suit.CLUBS),
        Card(Rank.KING, Suit.SPADES),
        Card(Rank.NINE, Suit.HEARTS),
        Card(Rank.EIGHT, Suit.HEARTS)
    ]
    rank, kickers, name = HandEvaluator.evaluate(four_kind)
    print(f"フォーカード: {name} (ランク: {rank})")
    
    # ワンペア
    one_pair = [
        Card(Rank.ACE, Suit.SPADES),
        Card(Rank.ACE, Suit.HEARTS),
        Card(Rank.KING, Suit.DIAMONDS),
        Card(Rank.QUEEN, Suit.CLUBS),
        Card(Rank.JACK, Suit.SPADES),
        Card(Rank.NINE, Suit.HEARTS),
        Card(Rank.EIGHT, Suit.HEARTS)
    ]
    rank, kickers, name = HandEvaluator.evaluate(one_pair)
    print(f"ワンペア: {name} (ランク: {rank})")
    print("✓ ハンド評価テスト完了\n")

def test_ai_decision():
    """AI判断のテスト"""
    print("=== AI判断テスト ===")
    
    # タイトなAI
    tight_ai = AIPlayer("Tight", 1000, PlayStyle.TIGHT)
    tight_ai.hand = [Card(Rank.ACE, Suit.SPADES), Card(Rank.KING, Suit.SPADES)]
    
    game_state = {
        'street': 'preflop',
        'pot': 30,
        'current_bet': 20,
        'community_cards': [],
        'position': 'button'
    }
    
    action, amount, reason = tight_ai.decide_action(game_state)
    print(f"Tight AI (A♠K♠): {action.value} ${amount} - {reason}")
    
    # ルースなAI
    loose_ai = AIPlayer("Loose", 1000, PlayStyle.LOOSE)
    loose_ai.hand = [Card(Rank.SEVEN, Suit.HEARTS), Card(Rank.TWO, Suit.DIAMONDS)]
    
    action, amount, reason = loose_ai.decide_action(game_state)
    print(f"Loose AI (7♥2♦): {action.value} ${amount} - {reason}")
    
    # アグレッシブなAI
    aggressive_ai = AIPlayer("Aggressive", 1000, PlayStyle.AGGRESSIVE)
    aggressive_ai.hand = [Card(Rank.JACK, Suit.CLUBS), Card(Rank.TEN, Suit.CLUBS)]
    
    action, amount, reason = aggressive_ai.decide_action(game_state)
    print(f"Aggressive AI (J♣10♣): {action.value} ${amount} - {reason}")
    print("✓ AI判断テスト完了\n")

def test_game_flow():
    """ゲームフローのテスト"""
    print("=== ゲームフローテスト ===")
    
    game = PokerGame("TestPlayer")
    print(f"プレイヤー数: {len(game.players)}")
    print(f"プレイヤー: {[p.name for p in game.players]}")
    
    # 新しいハンド開始
    game.start_new_hand()
    print(f"\nハンド開始:")
    print(f"  ポット: ${game.pot}")
    print(f"  あなたの手札: {game.human_player.hand}")
    print(f"  ディーラーポジション: {game.dealer_position}")
    
    # 各プレイヤーのチップ
    for player in game.players:
        print(f"  {player.name}: ${player.chips} (ベット: ${player.current_bet})")
    
    print("✓ ゲームフローテスト完了\n")

def test_feedback():
    """フィードバックのテスト"""
    print("=== フィードバックテスト ===")
    
    # サンプルハンドデータ
    hand_data = {
        'hand_number': 1,
        'players': {
            'You': {
                'chips_start': 1000,
                'chips_end': 1050,
                'hand': ['A♠', 'K♠'],
                'actions': [
                    {'action': 'raise', 'amount': 50, 'street': 'preflop', 'reason': 'Strong hand'},
                    {'action': 'call', 'amount': 20, 'street': 'flop', 'reason': 'Good flop'}
                ]
            }
        },
        'winner': 'You',
        'pot_size': 150,
        'streets': {
            'preflop': {'community_cards': [], 'actions': []},
            'flop': {'community_cards': ['Q♠', 'J♠', '10♠'], 'actions': []}
        }
    }
    
    feedback = FeedbackEngine.analyze_hand(hand_data, 'You')
    
    print(f"ハンド #{feedback['hand_number']}")
    print(f"結果: {feedback['result']}")
    print(f"利益: ${feedback['profit']}")
    print(f"スターティングハンド: {feedback['starting_hand']}")
    
    if feedback['good_plays']:
        print("\n良かったプレイ:")
        for play in feedback['good_plays']:
            print(f"  - [{play['street']}] {play['comment']}")
    
    if feedback['suggestions']:
        print("\nアドバイス:")
        for suggestion in feedback['suggestions']:
            print(f"  - {suggestion}")
    
    print("✓ フィードバックテスト完了\n")

def main():
    """すべてのテストを実行"""
    print("=" * 50)
    print("ポーカートレーナー - テストスイート")
    print("=" * 50)
    print()
    
    try:
        test_deck()
        test_hand_evaluation()
        test_ai_decision()
        test_game_flow()
        test_feedback()
        
        print("=" * 50)
        print("✅ すべてのテストが成功しました！")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
