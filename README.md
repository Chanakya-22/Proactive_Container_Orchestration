# Deep Unrolled ADMM with Hankel-Structured Attention for MRI Restoration

## 📌 Project Overview
This project implements a **Model-Based Deep Learning** framework for MRI denoising. Unlike standard "Black Box" CNNs, this architecture explicitly "unrolls" the **Alternating Direction Method of Multipliers (ADMM)** optimization algorithm into a deep neural network.

It integrates high-performance **Swin Transformers** with rigorous **Linear Algebra constraints (Hankel Matrices)** to ensure mathematical consistency in medical imaging.

## 🎓 Syllabus & Math Integration
This project directly implements concepts from the advanced mathematics curriculum:
* **Unit 1 (Special Matrices):** Implements **Hankel Matrix priors** to enforce low-rank structure on MRI patches.
* **Unit 2 (Optimization):** The network architecture mimics the iterative steps of **ADMM** (Data Consistency $x$-update, Denoising $z$-update, Multiplier $u$-update).

## 🚀 Key Features
* **White-Box Architecture:** Every layer corresponds to a mathematical optimization step.
* **Heavyweight ML Engine:** Utilizes **Swin Transformers** as a learned proximal operator.
* **Physics-Informed:** Constrains the solution space using Hankel structural properties.

## 📂 Project Structure
* `src/model_admm.py`: The core unrolled network architecture.
* `src/modules.py`: The Swin Transformer denoising block.
* `src/utils_math.py`: Hankel matrix transformation logic.
* `src/train.py`: Training script.

## 🛠️ Usage
1. Install dependencies:
   ```bash
   pip install -r requirements.txt