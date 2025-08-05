import streamlit as st
import random
import time
from datetime import datetime
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from utils.api_client import APIClient
from utils.state import start_game_session, update_game_score, end_game_session

def show_games_interface():
    """Main brain games interface"""
    st.markdown("### 🧠 Brain Games & Exercises")
    st.markdown("Keep your mind sharp with fun cognitive exercises and memory games.")
    
    # Game selection tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🃏 Memory Match", "🔢 Number Sequence", "🎯 Quick Math", "📊 Progress"])
    
    with tab1:
        show_memory_match_game()
    
    with tab2:
        show_number_sequence_game()
    
    with tab3:
        show_quick_math_game()
    
    with tab4:
        show_game_progress()

def show_memory_match_game():
    """Memory matching card game"""
    st.markdown("#### 🃏 Memory Match")
    st.markdown("Find matching pairs by remembering card positions.")
    
    # Game settings
    col1, col2, col3 = st.columns(3)
    
    with col1:
        difficulty = st.selectbox(
            "Difficulty Level",
            options=["Easy (4x2)", "Medium (4x3)", "Hard (4x4)"],
            key="memory_difficulty"
        )
    
    with col2:
        if st.button("🎮 Start New Game", key="start_memory_game"):
            initialize_memory_game(difficulty)
    
    with col3:
        if st.button("🔄 Reset Game", key="reset_memory_game"):
            reset_memory_game()
    
    # Game state
    if 'memory_game' not in st.session_state:
        st.info("Click 'Start New Game' to begin!")
        return
    
    game_state = st.session_state.memory_game
    
    if not game_state.get('active', False):
        st.info("Click 'Start New Game' to begin!")
        return
    
    # Display game stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Matches Found", game_state.get('matches', 0))
    
    with col2:
        st.metric("Moves", game_state.get('moves', 0))
    
    with col3:
        if game_state.get('start_time'):
            elapsed = time.time() - game_state['start_time']
            st.metric("Time", f"{int(elapsed)}s")
    
    with col4:
        total_pairs = len(game_state.get('cards', [])) // 2
        remaining = total_pairs - game_state.get('matches', 0)
        st.metric("Remaining", remaining)
    
    # Game board
    display_memory_game_board(game_state)
    
    # Check if game is won
    if game_state.get('matches', 0) == len(game_state.get('cards', [])) // 2:
        handle_memory_game_win(game_state)

def initialize_memory_game(difficulty):
    """Initialize memory matching game"""
    # Determine grid size
    grid_sizes = {
        "Easy (4x2)": (4, 2),
        "Medium (4x3)": (4, 3),
        "Hard (4x4)": (4, 4)
    }
    
    cols, rows = grid_sizes.get(difficulty, (4, 2))
    total_cards = cols * rows
    
    # Generate card pairs
    emojis = ["🐶", "🐱", "🐭", "🐹", "🐰", "🦊", "🐻", "🐼", "🐨", "🐯", "🦁", "🐸", "🐵", "🐔", "🐧", "🦄"]
    selected_emojis = emojis[:total_cards//2]
    cards = selected_emojis * 2
    random.shuffle(cards)
    
    # Initialize game state
    st.session_state.memory_game = {
        'active': True,
        'cards': cards,
        'revealed': [False] * total_cards,
        'matched': [False] * total_cards,
        'flipped': [],
        'matches': 0,
        'moves': 0,
        'cols': cols,
        'rows': rows,
        'start_time': time.time(),
        'difficulty': difficulty
    }
    
    # Start game session
    start_game_session("memory_match")

def display_memory_game_board(game_state):
    """Display the memory game board"""
    cards = game_state['cards']
    revealed = game_state['revealed']
    matched = game_state['matched']
    cols = game_state['cols']
    rows = game_state['rows']
    
    # Create grid
    for row in range(rows):
        columns = st.columns(cols)
        
        for col in range(cols):
            card_index = row * cols + col
            
            with columns[col]:
                # Determine what to show on card
                if matched[card_index]:
                    # Matched cards stay revealed
                    card_content = cards[card_index]
                    button_class = "matched"
                elif revealed[card_index]:
                    # Currently flipped cards
                    card_content = cards[card_index]
                    button_class = "flipped"
                else:
                    # Hidden cards
                    card_content = "❓"
                    button_class = "hidden"
                
                # Card button
                if st.button(
                    card_content,
                    key=f"card_{card_index}",
                    help=f"Card {card_index + 1}",
                    use_container_width=True
                ):
                    handle_memory_card_click(card_index)

def handle_memory_card_click(card_index):
    """Handle memory card click"""
    game_state = st.session_state.memory_game
    
    # Don't allow clicking matched or already revealed cards
    if game_state['matched'][card_index] or game_state['revealed'][card_index]:
        return
    
    # Don't allow more than 2 cards flipped at once
    if len(game_state['flipped']) >= 2:
        return
    
    # Reveal the card
    game_state['revealed'][card_index] = True
    game_state['flipped'].append(card_index)
    
    # Check if we have 2 cards flipped
    if len(game_state['flipped']) == 2:
        game_state['moves'] += 1
        
        card1_idx, card2_idx = game_state['flipped']
        card1_value = game_state['cards'][card1_idx]
        card2_value = game_state['cards'][card2_idx]
        
        if card1_value == card2_value:
            # Match found!
            game_state['matched'][card1_idx] = True
            game_state['matched'][card2_idx] = True
            game_state['matches'] += 1
            game_state['flipped'] = []
        else:
            # Not a match - cards will be hidden after a delay
            # For now, we'll hide them immediately on next interaction
            pass
    
    st.rerun()

def reset_memory_game():
    """Reset memory game state"""
    if 'memory_game' in st.session_state:
        del st.session_state.memory_game
    st.rerun()

def handle_memory_game_win(game_state):
    """Handle memory game completion"""
    if not game_state.get('completed', False):
        # Mark as completed
        game_state['completed'] = True
        
        # Calculate final stats
        total_time = int(time.time() - game_state['start_time'])
        moves = game_state['moves']
        difficulty = game_state['difficulty']
        
        # Calculate score (lower moves and time = higher score)
        base_score = 1000
        time_penalty = total_time * 2
        move_penalty = moves * 10
        score = max(100, base_score - time_penalty - move_penalty)
        
        # Display celebration
        st.success("🎉 Congratulations! You completed the memory game!")
        st.balloons()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Final Score", score)
        with col2:
            st.metric("Time", f"{total_time}s")
        with col3:
            st.metric("Moves", moves)
        
        # Save game result
        save_game_result("memory_match", score, total_time, difficulty)
        
        # End game session
        end_game_session()

def show_number_sequence_game():
    """Number sequence memory game"""
    st.markdown("#### 🔢 Number Sequence")
    st.markdown("Remember and repeat the number sequence.")
    
    # Game controls
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🎮 Start Sequence Game", key="start_sequence_game"):
            initialize_sequence_game()
    
    with col2:
        if st.button("🔄 Reset", key="reset_sequence_game"):
            reset_sequence_game()
    
    # Game state
    if 'sequence_game' not in st.session_state:
        st.info("Click 'Start Sequence Game' to begin!")
        return
    
    game_state = st.session_state.sequence_game
    
    if not game_state.get('active', False):
        st.info("Click 'Start Sequence Game' to begin!")
        return
    
    # Display current level and score
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Level", game_state.get('level', 1))
    
    with col2:
        st.metric("Score", game_state.get('score', 0))
    
    with col3:
        st.metric("Sequence Length", len(game_state.get('current_sequence', [])))
    
    # Game display
    display_sequence_game(game_state)

def initialize_sequence_game():
    """Initialize number sequence game"""
    st.session_state.sequence_game = {
        'active': True,
        'level': 1,
        'score': 0,
        'current_sequence': [],
        'user_sequence': [],
        'showing_sequence': False,
        'accepting_input': False,
        'start_time': time.time()
    }
    
    # Generate first sequence
    generate_new_sequence()
    start_game_session("number_sequence")

def generate_new_sequence():
    """Generate new number sequence"""
    game_state = st.session_state.sequence_game
    level = game_state['level']
    
    # Sequence length increases with level
    sequence_length = min(3 + level, 10)
    
    # Generate random sequence
    sequence = [random.randint(1, 9) for _ in range(sequence_length)]
    
    game_state['current_sequence'] = sequence
    game_state['user_sequence'] = []
    game_state['showing_sequence'] = True
    game_state['accepting_input'] = False

def display_sequence_game(game_state):
    """Display sequence game interface"""
    if game_state.get('showing_sequence', False):
        st.info("🔍 Memorize this sequence:")
        
        # Display sequence
        sequence_str = " → ".join(map(str, game_state['current_sequence']))
        st.markdown(f"### {sequence_str}")
        
        if st.button("✅ I've memorized it!", key="memorized_sequence"):
            game_state['showing_sequence'] = False
            game_state['accepting_input'] = True
            st.rerun()
    
    elif game_state.get('accepting_input', False):
        st.info("🎯 Enter the sequence:")
        
        # Number input buttons
        st.markdown("Click the numbers in the correct order:")
        
        cols = st.columns(3)
        for i in range(9):
            col = cols[i % 3]
            with col:
                if st.button(str(i + 1), key=f"num_{i+1}", use_container_width=True):
                    handle_sequence_input(i + 1)
        
        # Show current input
        if game_state['user_sequence']:
            user_str = " → ".join(map(str, game_state['user_sequence']))
            st.markdown(f"**Your sequence:** {user_str}")
        
        # Clear and submit buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Clear", key="clear_sequence"):
                game_state['user_sequence'] = []
                st.rerun()
        
        with col2:
            if st.button("✅ Submit", key="submit_sequence"):
                check_sequence_answer()

def handle_sequence_input(number):
    """Handle number input for sequence game"""
    game_state = st.session_state.sequence_game
    
    if len(game_state['user_sequence']) < len(game_state['current_sequence']):
        game_state['user_sequence'].append(number)
        st.rerun()

def check_sequence_answer():
    """Check if sequence answer is correct"""
    game_state = st.session_state.sequence_game
    
    if game_state['user_sequence'] == game_state['current_sequence']:
        # Correct!
        st.success("🎉 Correct! Well done!")
        
        # Update score and level
        game_state['score'] += game_state['level'] * 100
        game_state['level'] += 1
        
        # Generate next sequence
        time.sleep(1)  # Brief pause
        generate_new_sequence()
        
    else:
        # Incorrect
        st.error("❌ Not quite right. Game over!")
        
        # End game
        total_time = int(time.time() - game_state['start_time'])
        save_game_result("number_sequence", game_state['score'], total_time, f"Level {game_state['level']}")
        
        game_state['active'] = False
        end_game_session()
    
    st.rerun()

def reset_sequence_game():
    """Reset sequence game"""
    if 'sequence_game' in st.session_state:
        del st.session_state.sequence_game
    st.rerun()

def show_quick_math_game():
    """Quick math challenge game"""
    st.markdown("#### 🎯 Quick Math")
    st.markdown("Solve math problems as quickly as possible!")
    
    # Game controls
    col1, col2 = st.columns(2)
    
    with col1:
        difficulty = st.selectbox(
            "Difficulty",
            options=["Easy", "Medium", "Hard"],
            key="math_difficulty"
        )
    
    with col2:
        if st.button("🎮 Start Math Challenge", key="start_math_game"):
            initialize_math_game(difficulty)
    
    # Game state
    if 'math_game' not in st.session_state:
        st.info("Choose difficulty and click 'Start Math Challenge'!")
        return
    
    game_state = st.session_state.math_game
    
    if not game_state.get('active', False):
        st.info("Choose difficulty and click 'Start Math Challenge'!")
        return
    
    # Display game stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Score", game_state.get('score', 0))
    
    with col2:
        st.metric("Correct", game_state.get('correct', 0))
    
    with col3:
        st.metric("Wrong", game_state.get('wrong', 0))
    
    with col4:
        remaining_time = max(0, game_state.get('time_limit', 60) - (time.time() - game_state.get('start_time', time.time())))
        st.metric("Time Left", f"{int(remaining_time)}s")
    
    # Check if time is up
    if remaining_time <= 0:
        handle_math_game_end(game_state)
        return
    
    # Display current problem
    display_math_problem(game_state)

def initialize_math_game(difficulty):
    """Initialize math game"""
    time_limits = {"Easy": 90, "Medium": 60, "Hard": 45}
    
    st.session_state.math_game = {
        'active': True,
        'difficulty': difficulty,
        'score': 0,
        'correct': 0,
        'wrong': 0,
        'start_time': time.time(),
        'time_limit': time_limits[difficulty],
        'current_problem': None
    }
    
    generate_math_problem()
    start_game_session("quick_math")

def generate_math_problem():
    """Generate a new math problem"""
    game_state = st.session_state.math_game
    difficulty = game_state['difficulty']
    
    if difficulty == "Easy":
        # Single digit addition/subtraction
        a = random.randint(1, 9)
        b = random.randint(1, 9)
        operation = random.choice(['+', '-'])
        
        if operation == '+':
            answer = a + b
        else:
            # Ensure positive result
            if a < b:
                a, b = b, a
            answer = a - b
    
    elif difficulty == "Medium":
        # Two digit addition/subtraction, single digit multiplication
        operations = ['+', '-', '*']
        operation = random.choice(operations)
        
        if operation == '*':
            a = random.randint(2, 9)
            b = random.randint(2, 9)
            answer = a * b
        else:
            a = random.randint(10, 50)
            b = random.randint(1, 20)
            
            if operation == '+':
                answer = a + b
            else:
                if a < b:
                    a, b = b, a
                answer = a - b
    
    else:  # Hard
        # More complex operations
        operations = ['+', '-', '*', '/']
        operation = random.choice(operations)
        
        if operation == '*':
            a = random.randint(5, 15)
            b = random.randint(5, 15)
            answer = a * b
        elif operation == '/':
            # Ensure clean division
            answer = random.randint(2, 20)
            b = random.randint(2, 10)
            a = answer * b
        else:
            a = random.randint(20, 100)
            b = random.randint(5, 30)
            
            if operation == '+':
                answer = a + b
            else:
                if a < b:
                    a, b = b, a
                answer = a - b
    
    game_state['current_problem'] = {
        'question': f"{a} {operation} {b}",
        'answer': answer
    }

def display_math_problem(game_state):
    """Display current math problem"""
    problem = game_state['current_problem']
    
    if not problem:
        generate_math_problem()
        st.rerun()
        return
    
    st.markdown(f"### {problem['question']} = ?")
    
    # Answer input
    user_answer = st.number_input(
        "Your answer:",
        value=0,
        key=f"math_answer_{time.time()}",
        help="Enter your answer and press Enter"
    )
    
    if st.button("✅ Submit Answer", key="submit_math_answer"):
        check_math_answer(user_answer, problem['answer'])

def check_math_answer(user_answer, correct_answer):
    """Check math answer"""
    game_state = st.session_state.math_game
    
    if user_answer == correct_answer:
        st.success("🎉 Correct!")
        game_state['correct'] += 1
        game_state['score'] += 10
    else:
        st.error(f"❌ Wrong! The answer was {correct_answer}")
        game_state['wrong'] += 1
    
    # Generate next problem
    generate_math_problem()
    st.rerun()

def handle_math_game_end(game_state):
    """Handle math game end"""
    if not game_state.get('completed', False):
        game_state['completed'] = True
        game_state['active'] = False
        
        st.success("⏰ Time's up! Great job!")
        
        # Display final stats
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Final Score", game_state['score'])
        
        with col2:
            st.metric("Accuracy", f"{game_state['correct']}/{game_state['correct'] + game_state['wrong']}")
        
        with col3:
            if game_state['correct'] + game_state['wrong'] > 0:
                accuracy_pct = (game_state['correct'] / (game_state['correct'] + game_state['wrong'])) * 100
                st.metric("Accuracy %", f"{accuracy_pct:.1f}%")
        
        # Save result
        total_time = game_state['time_limit']
        save_game_result("quick_math", game_state['score'], total_time, game_state['difficulty'])
        
        end_game_session()

def show_game_progress():
    """Show game progress and statistics"""
    st.markdown("#### 📊 Your Gaming Progress")
    
    try:
        api_client = st.session_state.api_client
        
        # Get game statistics
        game_stats = api_client.get_game_stats(days=30)
        
        if game_stats.get('total_games', 0) > 0:
            # Overall stats
            st.markdown("##### 🎮 Overall Statistics (Last 30 Days)")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Games", game_stats['total_games'])
            
            with col2:
                if game_stats.get('games'):
                    avg_score = sum(g.get('total_score', 0) / g.get('count', 1) for g in game_stats['games'].values()) / len(game_stats['games'])
                    st.metric("Average Score", f"{avg_score:.0f}")
            
            with col3:
                if game_stats.get('games'):
                    total_time = sum(g.get('total_time', 0) for g in game_stats['games'].values())
                    st.metric("Total Play Time", f"{total_time//60}m {total_time%60}s")
            
            # Game-specific stats
            st.markdown("##### 🎯 Game Statistics")
            
            for game_type, stats in game_stats.get('games', {}).items():
                with st.expander(f"{get_game_emoji(game_type)} {game_type.replace('_', ' ').title()} ({stats['count']} games)"):
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Best Score", stats.get('best_score', 0))
                    
                    with col2:
                        st.metric("Average Score", f"{stats.get('avg_score', 0):.0f}")
                    
                    with col3:
                        best_time = stats.get('best_time', float('inf'))
                        if best_time != float('inf'):
                            st.metric("Best Time", f"{best_time}s")
                        else:
                            st.metric("Best Time", "N/A")
                    
                    with col4:
                        st.metric("Average Time", f"{stats.get('avg_time', 0):.0f}s")
        
        else:
            st.info("No games played yet. Start playing to see your progress!")
            
        # Achievements section
        show_game_achievements(game_stats)
        
    except Exception as e:
        st.error(f"Error loading game progress: {e}")

def show_game_achievements(game_stats):
    """Show game achievements"""
    st.markdown("##### 🏆 Achievements")
    
    achievements = []
    
    if game_stats.get('total_games', 0) >= 1:
        achievements.append("🎮 First Game - Played your first brain game!")
    
    if game_stats.get('total_games', 0) >= 10:
        achievements.append("🔥 Regular Player - Played 10+ games!")
    
    if game_stats.get('total_games', 0) >= 50:
        achievements.append("🌟 Game Master - Played 50+ games!")
    
    # Check for high scores
    for game_type, stats in game_stats.get('games', {}).items():
        if stats.get('best_score', 0) >= 500:
            achievements.append(f"💯 High Scorer - Scored 500+ in {game_type.replace('_', ' ').title()}!")
    
    if achievements:
        for achievement in achievements:
            st.success(achievement)
    else:
        st.info("Keep playing to unlock achievements! 🎯")

def get_game_emoji(game_type):
    """Get emoji for game type"""
    emojis = {
        "memory_match": "🃏",
        "number_sequence": "🔢",
        "quick_math": "🎯"
    }
    return emojis.get(game_type, "🎮")

def save_game_result(game_type, score, time_taken, difficulty):
    """Save game result to backend"""
    try:
        api_client = st.session_state.api_client
        
        result = api_client.log_game_result(
            game_type=game_type,
            score=score,
            time_taken=time_taken,
            difficulty=difficulty
        )
        
        if result.get("status") == "success":
            st.success("🎯 Game result saved!")
        
    except Exception as e:
        st.error(f"Error saving game result: {e}")