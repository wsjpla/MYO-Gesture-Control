# MYO-Gesture-Control

## Requirement:
* myo-python
* Numpy
* Scikit-learn
* Tensorflow

## Usage:
```dataset.py```: Record EMG signals to make datasets for model training

```train_model.py```: Train the CNN model

```ges_rec_online.py```: Achieve real-time recognition to control a humanoid manipulator (uHand 2.0)

```decode_grip_strength.py```: Decode the relative strength of grip force according to the signal amplitude


## 7 gestures:
< fist >
< finger_spread >
< thumb >
< 1_finger_type >
< 2_finger_type >
< V_gesture >
< relax >
