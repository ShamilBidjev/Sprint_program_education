import sys
import os
import time
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

from sprint_app import SprintApp

def generate():
    app = QApplication(sys.argv)
    window = SprintApp()
    window.show()
    
    os.makedirs("screenshots", exist_ok=True)
    
    app.processEvents()
    time.sleep(0.5)
    
    # 1. Lobby Screen (now has Trophy Leaderboard Button!)
    window.stacked_widget.setCurrentIndex(0)
    app.processEvents()
    window.grab().save("screenshots/1_lobby.png")
    
    # 2. Topic Selection Screen (now has the new Class Selection page!)
    window.show_topic_selection()
    app.processEvents()
    window.grab().save("screenshots/2_topic_selection.png")
    
    # 3. Quiz Screen
    window.active_student_name = "Иван Смирнов"
    window.active_student_gender = "boys"
    window.active_age_cat = "old_2"
    window.selected_topic_name = "Дроби 6 класс (LaTeX)"
    window.sprint_questions = window.db.get_questions(1)
    window.current_question_index = 0
    window.correct_answers_count = 0
    window.sprint_responses_log = []
    window.sprint_total_time = 60
    window.sprint_time_remaining = 60
    window.update_quiz_question_ui()
    window.stacked_widget.setCurrentIndex(2)
    app.processEvents()
    window.grab().save("screenshots/3_sprint_quiz.png")
    
    # 4. Result Screen (Simple task index list)
    window.quiz_answer_input.setText("3/4")
    window.on_submit_answer()
    app.processEvents()
    
    window.end_sprint(timeout=False)
    app.processEvents()
    time.sleep(0.5)
    window.grab().save("screenshots/4_sprint_results.png")
    
    # 5. History Screen
    window.show_history()
    app.processEvents()
    time.sleep(0.5)
    window.grab().save("screenshots/5_history.png")
    
    # 6. Settings Screen (now has 'Manage GIFs' option button!)
    window.show_settings()
    app.processEvents()
    time.sleep(0.5)
    window.grab().save("screenshots/6_settings.png")
    
    # 7. Admin Panel Screen (with classes dropdown filter)
    window.show_admin_panel()
    if window.admin_topics_list.count() > 0:
        window.admin_topics_list.setCurrentRow(0)
    app.processEvents()
    time.sleep(0.5)
    window.grab().save("screenshots/7_admin_panel.png")
    
    # 8. Leaderboard Screen (with Trophy SVG header & 1, 2, 3 vector medal SVGs!)
    window.show_leaderboard_screen()
    app.processEvents()
    time.sleep(0.5)
    window.grab().save("screenshots/8_leaderboard.png")
    
    # 9. NEW: GIF Manager View Screen (Index 8)!
    window.show_gif_manager_screen()
    if window.gif_manager_list.count() > 0:
        window.gif_manager_list.setCurrentRow(0)
    app.processEvents()
    time.sleep(0.5)
    window.grab().save("screenshots/9_gif_manager.png")
    
    print("All updated screenshots saved inside 'screenshots/' folder!")

if __name__ == "__main__":
    generate()
