"""
Serviço de Visão Computacional
Refatorado de proposing/app.py - mantém toda lógica de CV intacta
"""
import cv2
import numpy as np
import time
from typing import Tuple, Optional, Dict, Any
import sys
from pathlib import Path

# Adiciona path do projeto original para importar módulos
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from proposing.pose_evaluator import PoseDetector
from proposing.ml_evaluator import MLEvaluator
from proposing.pose_metrics_loader import get_metrics_loader


class CVService:
    """Serviço principal de visão computacional"""
    
    MODE_NAMES = {
        'double_biceps': 'Duplo Biceps (Frente)',
        'side_chest': 'Side Chest',
        'side_triceps': 'Side Triceps',
        'most_muscular': 'Most Muscular',
        'enquadramento': 'Enquadramento'
    }
    
    def __init__(self, use_ml: bool = True):
        """
        Inicializa o serviço de CV
        
        Args:
            use_ml: Se True, usa modelos ML para avaliação (se disponíveis)
        """
        self.detector = PoseDetector()
        self.use_ml = use_ml
        self.ml_evaluator = MLEvaluator() if use_ml else None
        
        # Verifica se modelos ML estão carregados
        if self.ml_evaluator and not self.ml_evaluator.models_loaded:
            print("⚠️ Modelos ML não encontrados. Usando apenas regras.")
            self.use_ml = False
        
        # Carrega métricas dinâmicas da poseInfo (se disponíveis)
        try:
            metrics_loader = get_metrics_loader()
            if metrics_loader.metrics_cache:
                print(f"✅ Métricas dinâmicas carregadas para {len(metrics_loader.metrics_cache)} pose(s)")
            else:
                print("ℹ️ Usando métricas padrão (hardcoded)")
        except Exception as e:
            print(f"⚠️ Erro ao carregar métricas dinâmicas: {e}")
            print("   Usando métricas padrão (hardcoded)")
    
    def process_frame(
        self, 
        frame: np.ndarray, 
        pose_mode: str, 
        camera_width: int
    ) -> Tuple[np.ndarray, Optional[str], Optional[Any]]:
        """
        Processa um frame e retorna avaliação da pose
        
        Args:
            frame: Frame BGR do OpenCV
            pose_mode: Modo de pose ('double_biceps', 'enquadramento', etc.)
            camera_width: Largura da câmera (para cálculos de pixel)
        
        Returns:
            Tuple contendo:
            - frame_annotated: Frame com esqueleto desenhado
            - pose_quality: Mensagem de avaliação (None se não detectado)
            - landmarks_obj: Objeto de landmarks do MediaPipe (None se não detectado)
        """
        start_time = time.time()
        pose_quality = None
        landmarks_obj = None
        
        # MediaPipe espera RGB
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.detector.pose.process(image_rgb)
        del image_rgb  # Libera memória

        if results.pose_landmarks:
            landmarks_obj = results.pose_landmarks
            
            # Desenha landmarks (esqueleto)
            self.detector.mp_drawing.draw_landmarks(
                frame, 
                results.pose_landmarks, 
                self.detector.mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=self.detector.mp_drawing.DrawingSpec(
                    color=(0, 255, 0), thickness=2, circle_radius=2
                ),
                connection_drawing_spec=self.detector.mp_drawing.DrawingSpec(
                    color=(255, 255, 255), thickness=2
                )
            )
            
            landmarks = results.pose_landmarks.landmark
            h, w, _ = frame.shape

            # Extrai pontos importantes do corpo
            points = self._extract_keypoints(landmarks, camera_width, h)
            
            if not points:
                return frame, "Não foi possível detectar os pontos necessários", None

            # Calcula ângulos
            angles = self._calculate_angles(points)
            
            # Avalia a pose
            pose_quality = self._evaluate_pose(
                pose_mode, points, angles, camera_width
            )
            
            # Se ML está habilitado, combina com ML
            if self.use_ml and self.ml_evaluator and landmarks_obj:
                try:
                    ml_result = self.ml_evaluator.evaluate_with_ml(
                        landmarks_obj.landmark, pose_mode
                    )
                    combined = self.ml_evaluator.combine_with_rules(
                        ml_result, pose_quality
                    )
                    pose_quality = combined['final_feedback']
                except Exception as e:
                    print(f"⚠️ Erro ao usar ML: {e}. Usando apenas regras.")

        processing_time = int((time.time() - start_time) * 1000)
        
        return frame, pose_quality, landmarks_obj
    
    def _extract_keypoints(
        self, 
        landmarks: Any, 
        camera_width: int, 
        height: int
    ) -> Dict[str, Tuple[int, int, float]]:
        """Extrai pontos importantes do corpo com visibilidade"""
        points = {}
        landmark_enum = self.detector.mp_pose.PoseLandmark
        
        try:
            def get_point(landmark_idx):
                lm = landmarks[landmark_idx]
                return (
                    int(lm.x * camera_width), 
                    int(lm.y * height),
                    lm.visibility if hasattr(lm, 'visibility') else 1.0
                )
            
            points["LEFT_SHOULDER"] = get_point(landmark_enum.LEFT_SHOULDER.value)
            points["RIGHT_SHOULDER"] = get_point(landmark_enum.RIGHT_SHOULDER.value)
            points["LEFT_ELBOW"] = get_point(landmark_enum.LEFT_ELBOW.value)
            points["RIGHT_ELBOW"] = get_point(landmark_enum.RIGHT_ELBOW.value)
            points["LEFT_WRIST"] = get_point(landmark_enum.LEFT_WRIST.value)
            points["RIGHT_WRIST"] = get_point(landmark_enum.RIGHT_WRIST.value)
            points["LEFT_HIP"] = get_point(landmark_enum.LEFT_HIP.value)
            points["RIGHT_HIP"] = get_point(landmark_enum.RIGHT_HIP.value)
            points["LEFT_KNEE"] = get_point(landmark_enum.LEFT_KNEE.value)
            points["RIGHT_KNEE"] = get_point(landmark_enum.RIGHT_KNEE.value)
            points["LEFT_ANKLE"] = get_point(landmark_enum.LEFT_ANKLE.value)
            points["RIGHT_ANKLE"] = get_point(landmark_enum.RIGHT_ANKLE.value)
        except (AttributeError, IndexError, KeyError) as e:
            print(f"⚠️ Erro ao extrair keypoints: {e}")
            return {}
        
        return points
    
    def _is_visible(self, point: Tuple[int, int, float], threshold: float = 0.5) -> bool:
        """Verifica se um landmark está visível na câmera"""
        if len(point) < 3:
            return False
        return point[2] >= threshold
    
    def _calculate_angles(self, points: Dict[str, Tuple[int, int, float]]) -> Dict[str, float]:
        """Calcula ângulos do corpo, apenas para landmarks visíveis"""
        angles = {}
        
        # Ângulos dos braços (só se todos os pontos estiverem visíveis)
        if (all(k in points for k in ["LEFT_SHOULDER", "LEFT_ELBOW", "LEFT_WRIST"]) and
            all(self._is_visible(points[k]) for k in ["LEFT_SHOULDER", "LEFT_ELBOW", "LEFT_WRIST"])):
            angles["left_arm"] = self.detector.calculate_angle(
                list(points["LEFT_SHOULDER"][:2]),
                list(points["LEFT_ELBOW"][:2]),
                list(points["LEFT_WRIST"][:2])
            )
        
        if (all(k in points for k in ["RIGHT_SHOULDER", "RIGHT_ELBOW", "RIGHT_WRIST"]) and
            all(self._is_visible(points[k]) for k in ["RIGHT_SHOULDER", "RIGHT_ELBOW", "RIGHT_WRIST"])):
            angles["right_arm"] = self.detector.calculate_angle(
                list(points["RIGHT_SHOULDER"][:2]),
                list(points["RIGHT_ELBOW"][:2]),
                list(points["RIGHT_WRIST"][:2])
            )
        
        # Ângulos das pernas (só se todos os pontos estiverem visíveis)
        if (all(k in points for k in ["LEFT_HIP", "LEFT_KNEE", "LEFT_ANKLE"]) and
            all(self._is_visible(points[k]) for k in ["LEFT_HIP", "LEFT_KNEE", "LEFT_ANKLE"])):
            angles["left_knee"] = self.detector.calculate_angle(
                list(points["LEFT_HIP"][:2]),
                list(points["LEFT_KNEE"][:2]),
                list(points["LEFT_ANKLE"][:2])
            )
        
        if (all(k in points for k in ["RIGHT_HIP", "RIGHT_KNEE", "RIGHT_ANKLE"]) and
            all(self._is_visible(points[k]) for k in ["RIGHT_HIP", "RIGHT_KNEE", "RIGHT_ANKLE"])):
            angles["right_knee"] = self.detector.calculate_angle(
                list(points["RIGHT_HIP"][:2]),
                list(points["RIGHT_KNEE"][:2]),
                list(points["RIGHT_ANKLE"][:2])
            )
        
        return angles
    
    def _evaluate_pose(
        self, 
        pose_mode: str, 
        points: Dict[str, Tuple[int, int, float]], 
        angles: Dict[str, float],
        camera_width: int
    ) -> str:
        """
        Avalia a pose de acordo com o modo selecionado
        Mantém exatamente a mesma lógica de proposing/app.py
        """
        angle_left = angles.get("left_arm", 0)
        angle_right = angles.get("right_arm", 0)
        angle_left_knee = angles.get("left_knee", 0)
        angle_right_knee = angles.get("right_knee", 0)
        
        if pose_mode == 'double_biceps':
            if (all(key in points for key in ["LEFT_ELBOW", "RIGHT_ELBOW", "LEFT_SHOULDER", "RIGHT_SHOULDER"]) and
                all(self._is_visible(points[k]) for k in ["LEFT_ELBOW", "RIGHT_ELBOW", "LEFT_SHOULDER", "RIGHT_SHOULDER"])):
                return self.detector.evaluate_double_biceps(
                    angle_left, angle_right,
                    points["LEFT_ELBOW"][1], points["RIGHT_ELBOW"][1],
                    points["LEFT_SHOULDER"][1], points["RIGHT_SHOULDER"][1]
                )
            return "Nao foi possivel detectar os pontos necessarios"
            
        elif pose_mode == 'side_chest':
            if ("LEFT_SHOULDER" not in points or "RIGHT_SHOULDER" not in points or
                not self._is_visible(points["LEFT_SHOULDER"]) or not self._is_visible(points["RIGHT_SHOULDER"])):
                return "Nao foi possivel detectar os ombros"
            
            # Verifica visibilidade dos braços antes de avaliar
            left_arm_visible = (angle_left > 0 and "LEFT_ELBOW" in points and "LEFT_WRIST" in points and
                               self._is_visible(points["LEFT_ELBOW"]) and self._is_visible(points["LEFT_WRIST"]))
            right_arm_visible = (angle_right > 0 and "RIGHT_ELBOW" in points and "RIGHT_WRIST" in points and
                                self._is_visible(points["RIGHT_ELBOW"]) and self._is_visible(points["RIGHT_WRIST"]))
            
            if not left_arm_visible and not right_arm_visible:
                return "Nao foi possivel detectar os bracos necessarios"
            
            # No Side Chest, o braço FRONTAL (visível) está contraído (80-120°)
            # O braço que está mais contraído e mais próximo da câmera é o frontal
            # Usa uma combinação: ângulo (mais contraído = menor) e posição (mais próximo da câmera)
            camera_center_x = camera_width / 2
            left_shoulder_x = points["LEFT_SHOULDER"][0]
            right_shoulder_x = points["RIGHT_SHOULDER"][0]
            
            # Calcula score para cada braço (menor ângulo = mais contraído, mais próximo da câmera = melhor)
            left_score = 0
            right_score = 0
            
            if left_arm_visible:
                # Score baseado em: ângulo (menor = melhor para side chest) + proximidade da câmera
                angle_score = max(0, 120 - angle_left)  # Menor ângulo = maior score
                distance_score = max(0, camera_width - abs(left_shoulder_x - camera_center_x))
                left_score = angle_score + distance_score * 0.1
            
            if right_arm_visible:
                angle_score = max(0, 120 - angle_right)
                distance_score = max(0, camera_width - abs(right_shoulder_x - camera_center_x))
                right_score = angle_score + distance_score * 0.1
            
            # Verifica se joelhos estão visíveis
            knee_visible = False
            visible_knee_angle = 0
            opposite_arm_angle = 0
            
            # Escolhe o braço com maior score (mais contraído e mais próximo)
            if left_score > right_score and left_arm_visible:
                visible_arm_angle = angle_left
                visible_elbow_height = points["LEFT_ELBOW"][1]
                visible_shoulder_height = points["LEFT_SHOULDER"][1]
                if (angle_left_knee > 0 and "LEFT_KNEE" in points and 
                    self._is_visible(points["LEFT_KNEE"]) and self._is_visible(points.get("LEFT_HIP", (0,0,0))) and 
                    self._is_visible(points.get("LEFT_ANKLE", (0,0,0)))):
                    visible_knee_angle = angle_left_knee
                    knee_visible = True
                opposite_arm_angle = angle_right if right_arm_visible else 0
            elif right_arm_visible:
                visible_arm_angle = angle_right
                visible_elbow_height = points["RIGHT_ELBOW"][1]
                visible_shoulder_height = points["RIGHT_SHOULDER"][1]
                if (angle_right_knee > 0 and "RIGHT_KNEE" in points and 
                    self._is_visible(points["RIGHT_KNEE"]) and self._is_visible(points.get("RIGHT_HIP", (0,0,0))) and 
                    self._is_visible(points.get("RIGHT_ANKLE", (0,0,0)))):
                    visible_knee_angle = angle_right_knee
                    knee_visible = True
                opposite_arm_angle = angle_left if left_arm_visible else 0
            else:
                return "Nao foi possivel detectar os bracos necessarios"
            
            hip_rotation = 0
            if ("LEFT_HIP" in points and "RIGHT_HIP" in points and
                self._is_visible(points["LEFT_HIP"]) and self._is_visible(points["RIGHT_HIP"])):
                hip_rotation = abs(points["LEFT_HIP"][0] - points["RIGHT_HIP"][0])
            
            return self.detector.evaluate_side_chest(
                visible_arm_angle, visible_elbow_height, visible_shoulder_height,
                hip_rotation, visible_knee_angle, opposite_arm_angle, knee_visible
            )
            
        elif pose_mode == 'side_triceps':
            if ("LEFT_SHOULDER" not in points or "RIGHT_SHOULDER" not in points or
                not self._is_visible(points["LEFT_SHOULDER"]) or not self._is_visible(points["RIGHT_SHOULDER"])):
                return "Nao foi possivel detectar os ombros"
            
            # Na Side Triceps, o braço POSTERIOR (que mostra o tríceps) está estendido (~180°)
            # O braço FRONTAL está na frente, mais flexionado
            # IMPORTANTE: Só avaliar braços que estão VISÍVEIS na câmera
            
            # Verifica visibilidade dos braços
            left_arm_visible = (angle_left > 0 and "LEFT_ELBOW" in points and "LEFT_WRIST" in points and
                               self._is_visible(points["LEFT_ELBOW"]) and self._is_visible(points["LEFT_WRIST"]))
            right_arm_visible = (angle_right > 0 and "RIGHT_ELBOW" in points and "RIGHT_WRIST" in points and
                                self._is_visible(points["RIGHT_ELBOW"]) and self._is_visible(points["RIGHT_WRIST"]))
            
            if not left_arm_visible and not right_arm_visible:
                return "Nao foi possivel detectar os bracos necessarios"
            
            # Na Side Triceps, o braço POSTERIOR está estendido para trás (~160-180°)
            # O braço FRONTAL está na frente, mais flexionado
            # Usa uma combinação de ângulo (mais estendido = maior) e posição para detectar o posterior
            
            camera_center_x = camera_width / 2
            left_shoulder_x = points["LEFT_SHOULDER"][0]
            right_shoulder_x = points["RIGHT_SHOULDER"][0]
            
            # Calcula score para cada braço (maior ângulo = mais estendido = posterior)
            left_score = 0
            right_score = 0
            
            if left_arm_visible:
                # Score baseado em: ângulo (maior = mais estendido = melhor para posterior) + posição
                angle_score = angle_left  # Maior ângulo = maior score
                # Braço posterior geralmente está mais longe do centro (mais para o lado)
                distance_score = abs(left_shoulder_x - camera_center_x)
                left_score = angle_score + distance_score * 0.1
            
            if right_arm_visible:
                angle_score = angle_right
                distance_score = abs(right_shoulder_x - camera_center_x)
                right_score = angle_score + distance_score * 0.1
            
            # Verifica se joelhos estão visíveis
            knee_visible = False
            front_knee_angle = 0
            
            # Escolhe o braço com maior score (mais estendido) como posterior
            if left_score > right_score and left_arm_visible:
                # Braço esquerdo é o posterior
                posterior_arm_angle = angle_left
                posterior_elbow_height = points["LEFT_ELBOW"][1]
                posterior_shoulder_height = points["LEFT_SHOULDER"][1]
                posterior_wrist_height = points["LEFT_WRIST"][1]
                front_arm_angle = angle_right if right_arm_visible else 0
                # Verifica visibilidade do joelho direito (frontal)
                if (angle_right_knee > 0 and "RIGHT_KNEE" in points and 
                    self._is_visible(points["RIGHT_KNEE"]) and self._is_visible(points.get("RIGHT_HIP", (0,0,0))) and 
                    self._is_visible(points.get("RIGHT_ANKLE", (0,0,0)))):
                    front_knee_angle = angle_right_knee
                    knee_visible = True
            elif right_arm_visible:
                # Braço direito é o posterior
                posterior_arm_angle = angle_right
                posterior_elbow_height = points["RIGHT_ELBOW"][1]
                posterior_shoulder_height = points["RIGHT_SHOULDER"][1]
                posterior_wrist_height = points["RIGHT_WRIST"][1]
                front_arm_angle = angle_left if left_arm_visible else 0
                # Verifica visibilidade do joelho esquerdo (frontal)
                if (angle_left_knee > 0 and "LEFT_KNEE" in points and 
                    self._is_visible(points["LEFT_KNEE"]) and self._is_visible(points.get("LEFT_HIP", (0,0,0))) and 
                    self._is_visible(points.get("LEFT_ANKLE", (0,0,0)))):
                    front_knee_angle = angle_left_knee
                    knee_visible = True
            else:
                return "Nao foi possivel detectar o braco posterior necessario"
            
            hip_rotation = 0
            if ("LEFT_HIP" in points and "RIGHT_HIP" in points and
                self._is_visible(points["LEFT_HIP"]) and self._is_visible(points["RIGHT_HIP"])):
                hip_rotation = abs(points["LEFT_HIP"][0] - points["RIGHT_HIP"][0])
            
            return self.detector.evaluate_side_triceps(
                posterior_arm_angle, posterior_elbow_height, posterior_shoulder_height,
                posterior_wrist_height, hip_rotation, front_knee_angle, front_arm_angle, knee_visible
            )
            
        elif pose_mode == 'most_muscular':
            if all(key in points for key in ["LEFT_ELBOW", "RIGHT_ELBOW", "LEFT_SHOULDER", 
                                             "RIGHT_SHOULDER", "LEFT_WRIST", "RIGHT_WRIST"]):
                shoulder_width = abs(points["RIGHT_SHOULDER"][0] - points["LEFT_SHOULDER"][0])
                
                torso_alignment = 0
                if all(key in points for key in ["LEFT_SHOULDER", "LEFT_HIP", "RIGHT_SHOULDER", "RIGHT_HIP"]):
                    torso_alignment = abs((points["LEFT_SHOULDER"][1] - points["LEFT_HIP"][1]) - 
                                         (points["RIGHT_SHOULDER"][1] - points["RIGHT_HIP"][1]))
                
                return self.detector.evaluate_most_muscular(
                    angle_left, angle_right,
                    points["LEFT_ELBOW"][1], points["RIGHT_ELBOW"][1],
                    points["LEFT_SHOULDER"][1], points["RIGHT_SHOULDER"][1],
                    shoulder_width,
                    angle_left_knee if angle_left_knee > 0 else 175,
                    angle_right_knee if angle_right_knee > 0 else 175,
                    torso_alignment,
                    points["LEFT_WRIST"][0], points["RIGHT_WRIST"][0],
                    points["LEFT_SHOULDER"][0], points["RIGHT_SHOULDER"][0]
                )
            return "Nao foi possivel detectar os pontos necessarios"
            
        elif pose_mode == 'enquadramento':
            if "LEFT_SHOULDER" in points and "RIGHT_SHOULDER" in points:
                return self.detector.evaluate_centered(
                    points["LEFT_SHOULDER"][0], points["RIGHT_SHOULDER"][0], camera_width
                )
            return "Nao foi possivel detectar os pontos necessarios"
        else:
            return f"Modo '{pose_mode}' ainda nao implementado"

