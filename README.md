# AirExam: Gesture-Based Quiz System

## Overview
AirExam is a contactless quiz system that allows users to answer questions using hand gestures. It uses computer vision to detect finger movements in real time through a webcam.

## Problem Statement
Traditional examination systems rely entirely on keyboards and mice, which creates barriers for students with motor impairments, individuals recovering from injuries, or situations where touchless interaction is required. No student-level project currently addresses this gap with a complete, deployable gesture-based examination tool. Air Exam fills this exact gap.

## Features
-  Finger detection with hand skeleton tracking  
-  Timer-based quiz system (Time Left display)  
-  Gesture-based answer selection  
-  5 fingers gesture to skip questions  
-  Instant "Answer Recorded" feedback  
-  Result screen with per-question review  
-  Final score display  

##  Technologies Used
- Python  
- OpenCV  
- MediaPipe  
- NumPy
- HTML,CSS,JavaScript
- MySQL
- MJPEG via Flask Response
  
## How to Use
-Run python app.py and open the browser
-Show your hand to the webcam
-Read the question on the right panel
-Show 1, 2, 3, or 4 fingers for options A, B, C, D
-Hold the gesture steady for 2 seconds to confirm
-Show 5 fingers to skip a question
-View your score and detailed review at the end 

## Research Gap This Project Addresses
Most existing gesture projects (Air Canvas, Air MNIST, Virtual Mouse) are single-feature demos with no real-world use case. Air Exam is different:

-First gesture-based MCQ system with hold-to-confirm anti-accidental-selection logic
-Designed specifically for accessibility — students who cannot use standard input devices
-Full-stack deployable product, not just a local Python script
-Database-driven with unlimited questions, not hardcoded demos

