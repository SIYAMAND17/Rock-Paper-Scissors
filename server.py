import cv2
import mediapipe as mp
import random
import time

# Mediapipe instellingen
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.8)

# Camera openen
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# Spel instellingen
game_interval = 5  # Elke 5 seconden een nieuw spel
show_result_time = 2  # Laat het resultaat 2 seconden zien
max_score = 5  # Speel tot 5 punten
game_active = False  # Wacht tot de speler op ENTER drukt

# Scores
player_score = 0
computer_score = 0

# Startwaarden
computer_choice = "..."
player_choice = "Onbekend"
result = ""
result_color = (255, 255, 255)
last_game_time = time.time()
showing_result = False

# Functie om aantal opgestoken vingers te tellen
def count_fingers(hand_landmarks):
    fingertip_ids = [
        mp_hands.HandLandmark.THUMB_TIP,
        mp_hands.HandLandmark.INDEX_FINGER_TIP,
        mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
        mp_hands.HandLandmark.RING_FINGER_TIP,
        mp_hands.HandLandmark.PINKY_TIP
    ]
    
    finger_count = sum(1 for tip_id in fingertip_ids if hand_landmarks.landmark[tip_id].y < hand_landmarks.landmark[tip_id - 2].y)
    return finger_count

# Spel loopt continu
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)  # Spiegel beeld voor natuurlijke interactie

    if not game_active:
        # Wacht op ENTER om te starten
        text = "Druk op ENTER om te starten"
        text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1.5, 3)[0]
        text_x = (frame.shape[1] - text_size[0]) // 2
        text_y = (frame.shape[0] + text_size[1]) // 2
        cv2.putText(frame, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
        cv2.imshow("Rock Paper Scissors", frame)

        # Wacht tot ENTER wordt ingedrukt
        if cv2.waitKey(1) & 0xFF == 13:
            game_active = True
            player_score, computer_score = 0, 0  # Reset scores
            last_game_time = time.time()
        continue

    # Controleer of het spel voorbij is
    if player_score >= max_score or computer_score >= max_score:
        winner = "Computer" if computer_score > player_score else "Jij"
        final_score_text = f"{winner} wint met {computer_score} - {player_score}!"
        
        text_size = cv2.getTextSize(final_score_text, cv2.FONT_HERSHEY_SIMPLEX, 1.5, 3)[0]
        text_x = (frame.shape[1] - text_size[0]) // 2
        text_y = (frame.shape[0] + text_size[1]) // 2

        cv2.putText(frame, final_score_text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 255), 3)
        cv2.putText(frame, "           Druk op ENTER om opnieuw te beginnen", (text_x - 100, text_y + 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        cv2.imshow("Rock Paper Scissors", frame)

        # Wacht tot ENTER wordt ingedrukt om opnieuw te starten
        if cv2.waitKey(1) & 0xFF == 13:
            player_score, computer_score = 0, 0  # Reset scores
            game_active = False
        continue

    # Countdown berekenen
    time_since_last_game = time.time() - last_game_time
    seconds_left = int(game_interval - time_since_last_game)

    # Converteer naar RGB en analyseer handpositie
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    player_choice = "Onbekend"
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            finger_count = count_fingers(hand_landmarks)

            if finger_count >= 4:
                player_choice = "Paper"
            elif 2 <= finger_count <= 3:
                player_choice = "Scissors"
            else:
                player_choice = "Rock"

    if time_since_last_game >= game_interval:
        if not showing_result:
            computer_choice = random.choice(["Rock", "Paper", "Scissors"])
            if player_choice == "Onbekend":
                result = "Onbekend, speler afwezig"
                result_color = (0, 255, 255)
            elif player_choice == computer_choice:
                result = "Gelijkspel!"
                result_color = (0, 255, 255)
            elif (player_choice == "Rock" and computer_choice == "Scissors") or \
                 (player_choice == "Paper" and computer_choice == "Rock") or \
                 (player_choice == "Scissors" and computer_choice == "Paper"):
                result = "Jij wint!"
                result_color = (0, 255, 0)
                player_score += 1
            else:
                result = "Computer wint!"
                result_color = (0, 0, 255)
                computer_score += 1

            showing_result = True
            last_game_time = time.time()

    elif showing_result and time_since_last_game >= show_result_time:
        showing_result = False
        last_game_time = time.time()
        computer_choice = "..."
        result = ""

    loading_dots = "." * ((seconds_left % 3) + 1) if not showing_result else ""

    margin = 50
    right_x = frame.shape[1] - 250
    bottom_y = frame.shape[0] - 60

    cv2.putText(frame, f"Speler: {player_choice}", (margin, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(frame, f"Computer: {computer_choice if showing_result else loading_dots}", (margin, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    if showing_result:
        text_size = cv2.getTextSize(result, cv2.FONT_HERSHEY_SIMPLEX, 2, 4)[0]
        text_x = (frame.shape[1] - text_size[0]) // 2
        text_y = (frame.shape[0] + text_size[1]) // 2
        cv2.putText(frame, result, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 2, result_color, 4)

    cv2.putText(frame, "SCOREBORD", (right_x, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)
    cv2.putText(frame, f"Jij: {player_score}", (right_x, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(frame, f"Computer: {computer_score}", (right_x, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    if not showing_result:
        cv2.putText(frame, f"Nieuwe ronde in: {seconds_left}s", (margin, bottom_y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

    cv2.imshow("Rock Paper Scissors", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
