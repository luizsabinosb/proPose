"""
Módulo para usar modelos de ML treinados na avaliação de poses
Integra com o sistema de regras para melhorar feedbacks
"""
import numpy as np
from pathlib import Path
import joblib
import warnings
warnings.filterwarnings('ignore')


class MLEvaluator:
    """Avaliador usando modelos de Machine Learning"""
    
    def __init__(self, models_dir=None):
        """
        Inicializa o avaliador ML
        
        Args:
            models_dir: Diretório onde os modelos estão salvos (None = usa ml/models na raiz)
        """
        if models_dir is None:
            project_root = Path(__file__).resolve().parent.parent
            self.models_dir = project_root / "ml" / "models"
        else:
            self.models_dir = Path(models_dir)
        self.models = {}
        self.models_loaded = False
        self._load_models()
    
    def _load_models(self):
        """Carrega modelos treinados"""
        if not self.models_dir.exists():
            print("⚠️ Diretório de modelos não encontrado. Usando apenas regras.")
            return
        
        # Tenta carregar modelo geral
        general_model_path = self.models_dir / "pose_classifier_general.pkl"
        if general_model_path.exists():
            try:
                self.models['general'] = joblib.load(general_model_path)
                print("✅ Modelo ML geral carregado")
            except Exception as e:
                print(f"⚠️ Erro ao carregar modelo geral: {e}")
        
        # Carrega modelos específicos por pose
        pose_modes = ['double_biceps', 'side_chest', 'side_triceps', 
                     'most_muscular', 'enquadramento']
        
        for pose_mode in pose_modes:
            model_path = self.models_dir / f"pose_classifier_{pose_mode}.pkl"
            if model_path.exists():
                try:
                    self.models[pose_mode] = joblib.load(model_path)
                    print(f"✅ Modelo ML para '{pose_mode}' carregado")
                except Exception as e:
                    print(f"⚠️ Erro ao carregar modelo {pose_mode}: {e}")
        
        self.models_loaded = len(self.models) > 0
        
        if not self.models_loaded:
            print("⚠️ Nenhum modelo ML encontrado. Usando apenas regras.")
    
    def extract_features(self, landmarks):
        """
        Extrai features dos landmarks (mesma função usada no treinamento)
        
        Args:
            landmarks: Lista de landmarks do MediaPipe (33 pontos)
        """
        features = []
        
        # Índices dos landmarks principais
        key_landmarks = [
            0,   # nose
            11, 12,  # shoulders
            13, 14,  # elbows
            15, 16,  # wrists
            23, 24,  # hips
            25, 26,  # knees
            27, 28,  # ankles
        ]
        
        # Converte landmarks para dicionário para facilitar acesso
        landmarks_dict = {}
        for idx, landmark in enumerate(landmarks):
            landmarks_dict[idx] = {
                'x': landmark.x,
                'y': landmark.y,
                'z': landmark.z,
                'visibility': getattr(landmark, 'visibility', 1.0)
            }
        
        # Extrai features dos pontos principais
        for idx in key_landmarks:
            if idx in landmarks_dict:
                lm = landmarks_dict[idx]
                features.extend([lm['x'], lm['y'], lm['z'], lm['visibility']])
            else:
                features.extend([0.0, 0.0, 0.0, 0.0])
        
        # Distância entre ombros
        if all(i in landmarks_dict for i in [11, 12]):
            left_shoulder = landmarks_dict[11]
            right_shoulder = landmarks_dict[12]
            shoulder_width = np.sqrt(
                (left_shoulder['x'] - right_shoulder['x'])**2 +
                (left_shoulder['y'] - right_shoulder['y'])**2
            )
            features.append(shoulder_width)
        else:
            features.append(0.0)
        
        # Distância entre punhos
        if all(i in landmarks_dict for i in [15, 16]):
            left_wrist = landmarks_dict[15]
            right_wrist = landmarks_dict[16]
            wrist_distance = np.sqrt(
                (left_wrist['x'] - right_wrist['x'])**2 +
                (left_wrist['y'] - right_wrist['y'])**2
            )
            features.append(wrist_distance)
        else:
            features.append(0.0)
        
        # Altura relativa cotovelo-ombro esquerdo
        if all(i in landmarks_dict for i in [11, 13]):
            features.append(landmarks_dict[13]['y'] - landmarks_dict[11]['y'])
        else:
            features.append(0.0)
        
        # Altura relativa cotovelo-ombro direito
        if all(i in landmarks_dict for i in [12, 14]):
            features.append(landmarks_dict[14]['y'] - landmarks_dict[12]['y'])
        else:
            features.append(0.0)
        
        return np.array(features).reshape(1, -1)
    
    def evaluate_with_ml(self, landmarks, pose_mode):
        """
        Avalia pose usando modelo ML
        
        Args:
            landmarks: Lista de landmarks do MediaPipe
            pose_mode: Modo da pose atual
            
        Returns:
            dict com:
                - prediction: 0 (incorrect) ou 1 (correct)
                - confidence: probabilidade de estar correto (0-1)
                - model_used: qual modelo foi usado
        """
        if not self.models_loaded or not landmarks:
            return None
        
        try:
            # Extrai features
            features = self.extract_features(landmarks)
            
            # Tenta usar modelo específico da pose primeiro
            model = None
            model_name = None
            
            if pose_mode in self.models:
                model = self.models[pose_mode]
                model_name = pose_mode
            elif 'general' in self.models:
                model = self.models['general']
                model_name = 'general'
            else:
                return None
            
            # Faz predição
            prediction = model.predict(features)[0]
            
            # Obtém probabilidades (se disponível)
            if hasattr(model, 'predict_proba'):
                probabilities = model.predict_proba(features)[0]
                confidence = probabilities[1] if len(probabilities) > 1 else 0.5
            else:
                confidence = 0.8 if prediction == 1 else 0.2
            
            return {
                'prediction': int(prediction),
                'confidence': float(confidence),
                'model_used': model_name
            }
        
        except Exception as e:
            print(f"⚠️ Erro na avaliação ML: {e}")
            return None
    
    def combine_with_rules(self, ml_result, rule_feedback, confidence_threshold=0.7):
        """
        Combina resultado ML com feedback das regras
        
        Args:
            ml_result: Resultado do ML (dict ou None)
            rule_feedback: Feedback das regras (string)
            confidence_threshold: Confiança mínima para confiar no ML
            
        Returns:
            dict com feedback combinado
        """
        if ml_result is None:
            # Se não há ML, usa apenas regras
            is_correct = "correta" in rule_feedback.lower() or "centralizado" in rule_feedback.lower()
            return {
                'final_feedback': rule_feedback,
                'is_correct': is_correct,
                'source': 'rules_only',
                'ml_confidence': None
            }
        
        # Extrai se é correto das regras
        rule_is_correct = "correta" in rule_feedback.lower() or "centralizado" in rule_feedback.lower()
        ml_is_correct = ml_result['prediction'] == 1
        ml_confidence = ml_result['confidence']
        
        # Se ML tem alta confiança, prioriza ML
        if ml_confidence >= confidence_threshold:
            if ml_is_correct:
                final_feedback = f"✅ [ML] {rule_feedback}" if rule_is_correct else "✅ [ML] Posição correta"
            else:
                final_feedback = f"❌ [ML] {rule_feedback}" if not rule_is_correct else "❌ [ML] Ajuste necessário"
            
            return {
                'final_feedback': final_feedback,
                'is_correct': ml_is_correct,
                'source': 'ml_high_confidence',
                'ml_confidence': ml_confidence,
                'rule_feedback': rule_feedback
            }
        
        # Se ML tem baixa confiança, usa regras mas adiciona informação do ML
        if rule_is_correct and ml_is_correct:
            # Ambos concordam - reforça
            final_feedback = f"✅ [✓ML] {rule_feedback}"
        elif not rule_is_correct and not ml_is_correct:
            # Ambos concordam - reforça
            final_feedback = f"❌ [✗ML] {rule_feedback}"
        else:
            # Discordam - prioriza regras mas menciona ML
            ml_indicator = "✓" if ml_is_correct else "✗"
            final_feedback = f"{rule_feedback} [ML:{ml_indicator} conf:{ml_confidence:.0%}]"
        
        return {
            'final_feedback': final_feedback,
            'is_correct': rule_is_correct,
            'source': 'rules_prioritized',
            'ml_confidence': ml_confidence,
            'ml_prediction': ml_is_correct,
            'rule_feedback': rule_feedback
        }

