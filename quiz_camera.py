from db import get_questions
import cv2
import mediapipe as mp
import time
 
mp_hands   = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
 
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.75,
    min_tracking_confidence=0.75
)
 
QUESTION_TIME = 15
HOLD_TIME     = 2
NEXT_DELAY    = 2
 
 
def count_fingers(lm):
    f = []
    f.append(1 if lm.landmark[4].x < lm.landmark[3].x else 0)
    for tip, pip in zip([8, 12, 16, 20], [6, 10, 14, 18]):
        f.append(1 if lm.landmark[tip].y < lm.landmark[pip].y else 0)
    return sum(f)
 
 
class QuizCamera:
 
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH,  640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
 
        # Load questions from MySQL
        data           = get_questions()
        self.QUESTIONS = [q['question'] for q in data]
        self.OPTIONS   = [[q['option_a'], q['option_b'],
                           q['option_c'], q['option_d']] for q in data]
        self.CORRECT   = [q['answer'] for q in data]
        self.answers   = [-1] * len(self.QUESTIONS)
 
        # Stability
        self.prev      = -1
        self.stable    = 0
        self.final     = 0
        self.STABILITY = 10
 
        # Hold timer
        self.hold_start = 0
 
        # Quiz state
        self.q_index     = 0
        self.score       = 0
        self.answered    = False
        self.answer_time = 0
        self.q_start     = time.time()
        self.feedback    = ''
        self.fb_color    = 'green'
        self.done        = False
 
    def _record(self, count, timeout=False):
        i = self.q_index
        if i >= len(self.answers):
            return
        if timeout or count == 5:
            self.answers[i] = -1
            self.feedback   = 'SKIPPED!'
            self.fb_color   = 'cyan'
        else:
            self.answers[i] = count
            if count == self.CORRECT[i]:
                self.feedback  = 'CORRECT!'
                self.fb_color  = 'green'
                self.score    += 1
            else:
                correct_text   = self.OPTIONS[i][self.CORRECT[i] - 1]
                self.feedback  = f'WRONG! Ans: {correct_text}'
                self.fb_color  = 'red'
 
    def get_frame(self):
        success, frame = self.cap.read()
        if not success:
            return None
 
        frame  = cv2.flip(frame, 1)
        rgb    = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb)
 
        remaining = int(QUESTION_TIME - (time.time() - self.q_start))
 
        # Auto skip on timeout
        if remaining <= 0 and not self.answered and not self.done:
            self._record(0, timeout=True)
            self.answered    = True
            self.answer_time = time.time()
 
        # Hand detection
        if result.multi_hand_landmarks and not self.answered and not self.done:
            for lm in result.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, lm, mp_hands.HAND_CONNECTIONS)
                cnt = count_fingers(lm)
 
                if cnt == self.prev:
                    self.stable += 1
                else:
                    self.stable = 0
                self.prev = cnt
                if self.stable > self.STABILITY:
                    self.final = cnt
 
                if self.final in [1, 2, 3, 4, 5]:
                    if self.hold_start == 0:
                        self.hold_start = time.time()
                    else:
                        held  = time.time() - self.hold_start
                        bar_w = int((held / HOLD_TIME) * 280)
                        cv2.rectangle(frame, (30, 390), (310, 410),
                                      (50, 50, 50), -1)
                        cv2.rectangle(frame, (30, 390),
                                      (30 + bar_w, 410), (0, 200, 255), -1)
                        cv2.putText(frame, 'Hold to confirm...', (30, 386),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                    (0, 200, 255), 1)
                        if held > HOLD_TIME:
                            self._record(self.final)
                            self.answered    = True
                            self.answer_time = time.time()
                            self.hold_start  = 0
                else:
                    self.hold_start = 0
        elif not result.multi_hand_landmarks:
            self.hold_start = 0
 
        # Move to next question
        if self.answered and time.time() - self.answer_time > NEXT_DELAY:
            self.q_index  += 1
            self.answered  = False
            self.feedback  = ''
            self.q_start   = time.time()
            self.final     = 0
            if self.q_index >= len(self.QUESTIONS):
                self.done = True
 
        # Draw question and options
        if not self.done and self.q_index < len(self.QUESTIONS):
            cv2.putText(frame, self.QUESTIONS[self.q_index], (20, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)
            for i, opt in enumerate(self.OPTIONS[self.q_index]):
                col = (0, 255, 0) if self.final == i + 1 else (200, 200, 200)
                cv2.putText(frame, opt, (20, 85 + i * 28),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.58, col, 2)
 
        # Overlays
        cv2.putText(frame, f'Fingers: {self.final}', (20, 265),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f'Time: {max(remaining, 0)}s', (430, 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        if not self.done:
            cv2.putText(frame,
                        f'Q: {self.q_index + 1}/{len(self.QUESTIONS)}',
                        (430, 60), cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, (200, 200, 200), 1)
 
        # Feedback
        if self.answered and self.feedback:
            fb_col = (0, 220, 0) if self.fb_color == 'green' else \
                     (0, 60, 220) if self.fb_color == 'red' else (220, 220, 0)
            cv2.putText(frame, self.feedback, (20, 320),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, fb_col, 3)
 
        if self.done:
            cv2.putText(frame, 'Quiz Done! See browser panel',
                        (60, 240), cv2.FONT_HERSHEY_SIMPLEX,
                        0.8, (0, 255, 255), 2)
 
        _, buf = cv2.imencode('.jpg', frame)
        return buf.tobytes()
 
    def get_status(self):
        if self.done:
            review = []
            for i, ans in enumerate(self.answers):
                correct_opt = self.OPTIONS[i][self.CORRECT[i] - 1]
                if ans == -1:
                    your_text = 'Skipped / Timed Out'
                    status    = 'skipped'
                elif ans == self.CORRECT[i]:
                    your_text = self.OPTIONS[i][ans - 1]
                    status    = 'correct'
                else:
                    your_text = self.OPTIONS[i][ans - 1]
                    status    = 'wrong'
                review.append({
                    'q'          : self.QUESTIONS[i],
                    'your_ans'   : your_text,
                    'correct_ans': correct_opt,
                    'status'     : status
                })
            total    = len(self.QUESTIONS)
            accuracy = round(self.score / total * 100) if total > 0 else 0
            return {
                'done'    : True,
                'score'   : self.score,
                'total'   : total,
                'accuracy': accuracy,
                'review'  : review
            }
 
        if self.q_index < len(self.QUESTIONS):
            opts      = self.OPTIONS[self.q_index]
            remaining = int(QUESTION_TIME - (time.time() - self.q_start))
            return {
                'done'     : False,
                'question' : self.QUESTIONS[self.q_index],
                'option_a' : opts[0],
                'option_b' : opts[1],
                'option_c' : opts[2],
                'option_d' : opts[3],
                'q_num'    : self.q_index + 1,
                'total'    : len(self.QUESTIONS),
                'score'    : self.score,
                'feedback' : self.feedback,
                'fb_color' : self.fb_color,
                'remaining': max(remaining, 0)
            }
 
        return {
            'done': False, 'question': '', 'q_num': 0,
            'total': len(self.QUESTIONS), 'score': self.score,
            'feedback': '', 'fb_color': 'green', 'remaining': 0
        }
 
    def release(self):
        self.cap.release()
 