import random
import time
import os
from enum import Enum
from typing import List, Dict, Optional
from collections import deque
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
except ImportError:
    exit()
# Terminal control utility functions
class TerminalUI:
    @staticmethod
    def clear_screen():
        os.system('cls' if os.name == 'nt' else 'clear')
    
    @staticmethod
    def move_cursor(x, y):
        print(f"\033[{y};{x}H", end="")
    
    @staticmethod
    def clear_line():
        print("\033[2K", end="")
    
    @staticmethod
    def reset_cursor():
        print("\033[H", end="")

class Card:
    def __init__(self, suit: str, value: str):
        self.suit = suit
        self.value = value

    def __repr__(self):
        if self.value == '10':
            return f'{self.suit.ljust(2)}{self.value.rjust(3)}'
        else:
            return f'{self.suit.ljust(2)}{self.value.rjust(2)}'

class Deck:
    def __init__(self, num_decks: int):
        self.cards = []
        self.num_decks = num_decks
        self.suits = ['♥️', '♦️', '♣️', '♠️']
        # self.suits = ['♥', '♦', '♣', '♠']
        #self.suits = ['󱢪', '󱢦', '󱢢', '󱢮']
        self.values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

        for _ in range(self.num_decks):
            for suit in self.suits:
                for value in self.values:
                    self.cards.append(Card(suit, value))
        random.shuffle(self.cards)

    def deal_card(self) -> Card:
        return self.cards.pop()

class Hand:
    def __init__(self):
        self.cards = []
        self.bet = 0

    def add_card(self, card: Card):
        self.cards.append(card)

    def get_value(self) -> int:
        value = 0
        aces = 0
        for card in self.cards:
            if card.value.isnumeric():
                value += int(card.value)
            else:
                if card.value == 'A':
                    aces += 1
                    value += 11
                else:
                    value += 10

        while value > 21 and aces:
            value -= 10
            aces -= 1
        return value

    def __repr__(self):
        return f'Hand value: {self.get_value()} with cards {self.cards}'

class Player:
    def __init__(self, name: str, balance: int):
        self.name = name
        self.balance = balance
        self.hand = Hand()
        self.position = 0  # Display position on screen

    def hit(self, deck: Deck):
        self.hand.add_card(deck.deal_card())

    def double_down(self, deck: Deck):
        if len(self.hand.cards) != 2:
            print('Can only double down on initial two cards')
            return False
        self.hit(deck)
        return True

    def split(self, deck: Deck):
        if len(self.hand.cards) != 2 or self.hand.cards[0].value != self.hand.cards[1].value:
            print('Can only split initial two cards of same value')
            return False
        new_hand = Hand()
        new_hand.add_card(self.hand.cards.pop())
        new_hand.add_card(deck.deal_card())
        self.hand.add_card(deck.deal_card())
        return True

class GameUI:
    def __init__(self, terminal_width=80):
        self.width = terminal_width
        self.dealer_hand = None
        self.players = []
        self.messages = []
        self.active_player_index = 0
    
    def initialize(self, players):
        self.players = players
        for i, player in enumerate(players):
            player.position = 10 + i * 5
    
    def draw_frame(self):
        TerminalUI.clear_screen()
        print("=" * self.width)
        print("BLACKJACK".center(self.width))
        print("=" * self.width)
        print("Dealer:".ljust(self.width))
        print(" " * self.width)
        print("-" * self.width)
        for player in self.players:
            line_pos = player.position
            TerminalUI.move_cursor(0, line_pos)
            print(f"Player: {player.name}")
            TerminalUI.move_cursor(self.width - 15, line_pos)
            print(f"Balance: ${player.balance}")
            TerminalUI.move_cursor(0, line_pos + 1)
            print("Cards: ".ljust(self.width))
            TerminalUI.move_cursor(0, line_pos + 2)
            print("Value: ".ljust(self.width))
            TerminalUI.move_cursor(0, line_pos + 3)
            print("-" * self.width)
        TerminalUI.move_cursor(0, max([p.position for p in self.players]) + 5)
        print("=" * self.width)
        for _ in range(3):
            print(" " * self.width)
    
    def update_dealer_hand(self, hand, hide_first_card=False):
        self.dealer_hand = hand
        # Clear previous dealer cards line
        TerminalUI.move_cursor(0, 4)
        TerminalUI.clear_line()
        TerminalUI.move_cursor(8, 4)
        if hide_first_card and len(hand.cards) > 0:
            cards_display = ["🂠"] + [str(card) for card in hand.cards[1:]]
            print(" ".join(cards_display))
            # Clear previous value line
            TerminalUI.move_cursor(0, 5)
            TerminalUI.clear_line()
            TerminalUI.move_cursor(0, 5)
            print("Value: ?")
        else:
            print(" ".join([str(card) for card in hand.cards]))
            TerminalUI.move_cursor(0, 5)
            TerminalUI.clear_line()
            TerminalUI.move_cursor(0, 5)
            print(f"Value: {hand.get_value()}")
    
    def update_player_hand(self, player_index):
        player = self.players[player_index]
        line_pos = player.position
        # Clear previous cards line
        TerminalUI.move_cursor(0, line_pos + 1)
        TerminalUI.clear_line()
        TerminalUI.move_cursor(8, line_pos + 1)
        print(" ".join([str(card) for card in player.hand.cards]))
        # Clear previous value line
        TerminalUI.move_cursor(0, line_pos + 2)
        TerminalUI.clear_line()
        TerminalUI.move_cursor(8, line_pos + 2)
        print(str(player.hand.get_value()))
        # Update balance with clear then padded print
        TerminalUI.move_cursor(0, line_pos)
        TerminalUI.clear_line()
        TerminalUI.move_cursor(self.width - 15, line_pos)
        balance_str = f"Balance: ${player.balance}"
        print(f"{balance_str:<15}")
    
    def set_active_player(self, player_index):
        self.active_player_index = player_index
        for i, player in enumerate(self.players):
            TerminalUI.move_cursor(0, player.position)
            if i == player_index:
                print(f"Player: {player.name} ◀")
            else:
                print(f"Player: {player.name}  ")
    
    def show_message(self, message):
        self.messages.append(message)
        if len(self.messages) > 3:
            self.messages.pop(0)
        msg_start_line = max([p.position for p in self.players]) + 6
        for i, msg in enumerate(self.messages):
            TerminalUI.move_cursor(0, msg_start_line + i)
            TerminalUI.clear_line()
            print(msg)
    
    def prompt_for_action(self, available_actions):
        msg_start_line = max([p.position for p in self.players]) + 10
        TerminalUI.move_cursor(0, msg_start_line)
        TerminalUI.clear_line()
        
        if len(available_actions) == 1:
            # If only one action string is passed, use it verbatim as the prompt
            prompt = available_actions[0]
        else:
            # Multiple actions - format as before
            action_display = '/'.join(available_actions)
            prompt = f"Choose action ({action_display}): "
        
        print(prompt, end='', flush=True)
        return input().lower()
        
# Rich-based UI for enhanced terminal rendering
if Console:
    class RichGameUI:
        def __init__(self):
            self.console = Console()
            self.players = []
            self.dealer_hand = None
            self.hide_dealer = False
            self.messages = []
            self.active_player_index = 0

        def initialize(self, players):
            self.players = players

        def draw_frame(self):
                # 1) Clear & header
                self.console.clear()
                total_width = self.console.size.width
                self.console.rule("[bold yellow]BLACKJACK[/bold yellow]")

                # 2) Dealer panel spans full width
                cards = []
                value = "?"
                if self.dealer_hand:
                    if self.hide_dealer and len(self.dealer_hand.cards) > 0:
                        cards = ["🂠"] + [str(c) for c in self.dealer_hand.cards[1:]]
                    else:
                        cards = [str(c) for c in self.dealer_hand.cards]
                        value = str(self.dealer_hand.get_value())

                dealer_body = "\n".join([
                    " ".join(cards),
                    f"Value: {value}"
                ])
                dealer_panel = Panel(
                    Text(dealer_body, justify="center"),
                    title="[bold]Dealer[/bold]",
                    border_style="blue",
                    width=total_width
                )

                # 3) Fixed‐width player panels
                players = self.players
                n = len(players)
                gap = 1               # spaces between panels
                min_w = 20            # never go below this
                # carve the remaining width up evenly:
                panel_w = max(min_w, (total_width - gap * (n - 1)) // n)

                player_panels = []
                for idx, p in enumerate(players):
                    card_str = " ".join(str(c) for c in p.hand.cards)
                    val_str  = str(p.hand.get_value())
                    body = "\n".join([f"Cards: {card_str}", f"Value: {val_str}"])
                    border = "green" if idx == self.active_player_index else "magenta"
                    title  = f"> {p.name} <" if idx == self.active_player_index else p.name
                    subtitle = f"Balance: ${p.balance}"

                    player_panels.append(Panel(
                        Text(body),
                        title=title,
                        subtitle=subtitle,
                        border_style=border,
                        width=panel_w
                    ))

                # 4) Render everything
                from rich.columns import Columns
                self.console.print(dealer_panel)
                self.console.print()  # blank line
                self.console.print(Columns(
                    player_panels,
                    padding=(0, gap),
                    expand=False
                ))

                # 5) Messages (same as before)
                if self.messages:
                    self.console.print("\n[bold]Messages:[/bold]")
                    for msg in self.messages:
                        self.console.print(f"- {msg}")

        def update_dealer_hand(self, hand, hide_first_card=False):
            self.dealer_hand = hand
            self.hide_dealer = hide_first_card
            self.draw_frame()

        def update_player_hand(self, player_index):
            self.draw_frame()

        def set_active_player(self, player_index):
            self.active_player_index = player_index
            self.draw_frame()

        def show_message(self, message):
            self.messages.append(message)
            if len(self.messages) > 5:
                self.messages.pop(0)
            self.draw_frame()

        def prompt_for_action(self, available_actions):
            if len(available_actions) == 1:
                prompt = available_actions[0]
            else:
                prompt = f"Choose action ({'/'.join(available_actions)}): "
            return self.console.input(prompt).lower()

class Game:
    def __init__(self, num_decks: int, num_bots: int, interactive: bool = True, human_actions: Optional[List[str]] = None):
        self.interactive = interactive
        self.human_actions = deque(human_actions) if human_actions else deque()
        self.deck = Deck(num_decks)
        self.players = []
        # Choose UI: use Rich if available, else fallback to original
        if Console:
            self.ui = RichGameUI()
        else:
            try:
                terminal_size = os.get_terminal_size()
                self.ui = GameUI(terminal_size.columns)
            except:
                self.ui = GameUI()
        if self.interactive:
            for i in range(num_bots + 1):
                if i == 0:
                    # Human player -- name prompt or from predefined actions
                    if Console:
                        self.ui.console.clear()
                        self.ui.console.print("[bold yellow]Welcome to Blackjack![/bold yellow]")
                        if self.human_actions:
                            name = self.human_actions.popleft()
                        else:
                            name = self.ui.console.input("Enter your name: ")
                    else:
                        TerminalUI.clear_screen()
                        print("Welcome to Blackjack!")
                        if self.human_actions:
                            name = self.human_actions.popleft()
                        else:
                            name = input("Enter your name: ")
                    self.players.append(Player(name, 100))
                else:
                    self.players.append(Player(f'Bot {i}', 100))
        else:
            # Non-interactive mode: only bots
            for i in range(1, num_bots + 1):
                self.players.append(Player(f'Bot {i}', 100))
        self.ui.initialize(self.players)

    def _prompt(self, available_actions):
        if self.human_actions:
            return self.human_actions.popleft().lower()
        if not self.interactive:
            raise RuntimeError("No human actions available")
        return self.ui.prompt_for_action(available_actions)

    def play(self, max_rounds: Optional[int] = None):
        try:
            rounds_played = 0
            while True:
                # stop after max_rounds in non-interactive or when specified
                if max_rounds is not None and rounds_played >= max_rounds:
                    return
                rounds_played += 1
                self.ui.draw_frame()
                dealer_hand = Hand()
                for i, player in enumerate(self.players):
                    player.hand = Hand()
                    self.ui.set_active_player(i)
                    if not player.name.startswith('Bot'):
                        self.ui.show_message(f"{player.name}'s turn to place a bet")
                        bet_msg = f"Enter your bet (Balance ${player.balance}, min $5, max $100): "
                        while True:
                            try:
                                bet = int(self._prompt([bet_msg]))
                                if 5 <= bet <= 100 and bet <= player.balance:
                                    break
                                self.ui.show_message("Invalid bet amount. Try again.")
                            except ValueError:
                                self.ui.show_message("Please enter a valid number.")
                    else:
                        self.ui.show_message(f"{player.name} is placing a bet...")
                        if self.interactive:
                            time.sleep(1)
                        bet = 10
                    player.balance -= bet
                    player.hand.bet = bet
                    self.ui.update_player_hand(i)
                dealer_hand.add_card(self.deck.deal_card())
                dealer_hand.add_card(self.deck.deal_card())
                self.ui.update_dealer_hand(dealer_hand, hide_first_card=True)
                for i, player in enumerate(self.players):
                    player.hit(self.deck)
                    player.hit(self.deck)
                    self.ui.update_player_hand(i)
                for i, player in enumerate(self.players):
                    self.ui.set_active_player(i)
                    if player.hand.get_value() == 21:
                        self.ui.show_message(f"{player.name} has Blackjack!")
                        continue
                    while player.hand.get_value() < 21:
                        self.ui.show_message(f"{player.name}'s turn")
                        if not player.name.startswith('Bot'):
                            available_actions = ["hit", "stand"]
                            if len(player.hand.cards) == 2:
                                if player.balance >= player.hand.bet:
                                    available_actions.append("double down")
                                if player.hand.cards[0].value == player.hand.cards[1].value:
                                    available_actions.append("split")
                            action = self._prompt(available_actions)
                        else:
                            self.ui.show_message(f"{player.name} is thinking...")
                            if self.interactive:
                                time.sleep(random.randint(1, 5))
                            if len(player.hand.cards) == 2 and player.hand.cards[0].value == player.hand.cards[1].value:
                                action = 'split'
                            elif len(player.hand.cards) == 2 and player.hand.get_value() == 11 and player.balance >= player.hand.bet:
                                action = 'double down'
                            elif player.hand.get_value() < 11:
                                action = 'hit'
                            elif player.hand.get_value() == 11:
                                action = 'hit'
                            elif 12 <= player.hand.get_value() <= 16:
                                action = random.choices(['hit', 'stand'], [0.3, 0.7], k=1)[0]
                            else:
                                action = 'stand'
                            self.ui.show_message(f"{player.name} chooses to {action}.")
                        if action == 'hit':
                            player.hit(self.deck)
                            self.ui.update_player_hand(i)
                            if player.hand.get_value() > 21:
                                self.ui.show_message(f"{player.name} busts!")
                                break
                        elif action == 'double down':
                            if player.balance >= player.hand.bet:
                                if player.double_down(self.deck):
                                    player.balance -= player.hand.bet
                                    player.hand.bet *= 2
                                    self.ui.update_player_hand(i)
                                    self.ui.show_message(f"{player.name} doubled down!")
                                    break
                            else:
                                self.ui.show_message("Not enough balance to double down.")
                        elif action == 'split':
                            if player.split(self.deck):
                                self.ui.show_message(f"{player.name} split their hand!")
                                self.ui.update_player_hand(i)
                            else:
                                self.ui.show_message("Cannot split these cards.")
                        elif action == 'stand':
                            self.ui.show_message(f"{player.name} stands.")
                            break
                self.ui.show_message("Dealer's turn...")
                self.ui.update_dealer_hand(dealer_hand, hide_first_card=False)
                if self.interactive:
                    time.sleep(1)
                while dealer_hand.get_value() < 17:
                    dealer_hand.add_card(self.deck.deal_card())
                    self.ui.update_dealer_hand(dealer_hand)
                    if self.interactive:
                        time.sleep(1)
                dealer_value = dealer_hand.get_value()
                dealer_bust = dealer_value > 21
                for i, player in enumerate(self.players):
                    player_value = player.hand.get_value()
                    if player_value > 21:
                        self.ui.show_message(f"{player.name} busts and loses ${player.hand.bet}.")
                    elif dealer_bust:
                        player.balance += player.hand.bet * 2
                        self.ui.show_message(f"{player.name} wins ${player.hand.bet}! Dealer busted.")
                    elif player_value == 21 and len(player.hand.cards) == 2:
                        player.balance += int(player.hand.bet * 2.5)
                        self.ui.show_message(f"{player.name} wins ${int(player.hand.bet * 1.5)} with Blackjack!")
                    elif player_value > dealer_value:
                        player.balance += player.hand.bet * 2
                        self.ui.show_message(f"{player.name} wins ${player.hand.bet}!")
                    elif player_value < dealer_value:
                        self.ui.show_message(f"{player.name} loses ${player.hand.bet}.")
                    else:
                        player.balance += player.hand.bet
                        self.ui.show_message(f"{player.name} pushes. Bet returned.")
                    self.ui.update_player_hand(i)
                    if player.balance <= 0:
                        self.ui.show_message(f"{player.name} has run out of money! Game over.")
                        return
                self.ui.show_message("Press Enter to play another round or Ctrl+C to exit.")
                if self.interactive:
                    # wait for human to continue; in tests, skip
                    self._prompt([""])
        except KeyboardInterrupt:
            TerminalUI.clear_screen()
            print("Thanks for playing Blackjack!")