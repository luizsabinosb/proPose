"""
Módulo para coleta de dados de treinamento de alta qualidade
Inclui validações automáticas para garantir qualidade do dataset
"""
import cv2
import json
import os
import numpy as np
from datetime import datetime
from pathlib import Path
import hashlib


class DataCollector:
    """Sistema de coleta de dados com validações de qualidade"""
    
    def __init__(self, data_dir=None):
        """
        Inicializa o coletor de dados
        
        Args:
            data_dir: Diretório onde os dados serão salvos (None = usa ml/data na raiz)
        """
        if data_dir is None:
            project_root = Path(__file__).resolve().parent.parent
            self.data_dir = project_root / "ml" / "data"
        else:
            self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Estrutura de diretórios
        self.raw_dir = self.data_dir / "raw"
        self.processed_dir = self.data_dir / "processed"
        self.annotations_dir = self.data_dir / "annotations"
        
        for d in [self.raw_dir, self.processed_dir, self.annotations_dir]:
            d.mkdir(exist_ok=True)
        
        # Contadores por pose
        self.counters = {}
        self.last_frame_hash = None
        self.min_interval_seconds = 2  # Mínimo 2 segundos entre coletas
        
        # Thresholds de qualidade
        self.min_blur_threshold = 100  # Laplacian variance mínimo
        self.min_visible_landmarks = 25  # Mínimo de landmarks visíveis (de 33)
        self.similarity_threshold = 0.95  # Similaridade máxima entre frames (0-1)
        
    def calculate_blur_score(self, frame):
        """
        Calcula score de blur usando Laplacian variance
        Valores maiores indicam imagens mais nítidas
        
        Returns:
            float: Score de blur (maior = menos blur)
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        return laplacian_var
    
    def calculate_frame_hash(self, frame):
        """Calcula hash do frame para detecção de duplicatas"""
        # Redimensiona para hash mais rápido
        small = cv2.resize(frame, (64, 64))
        gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
        frame_bytes = gray.tobytes()
        return hashlib.md5(frame_bytes).hexdigest()
    
    def count_visible_landmarks(self, landmarks):
        """
        Conta quantos landmarks são visíveis
        
        Args:
            landmarks: Lista de landmarks do MediaPipe
            
        Returns:
            int: Número de landmarks visíveis
        """
        if not landmarks:
            return 0
        
        visible_count = 0
        for landmark in landmarks:
            # MediaPipe usa visibility > 0.5 para considerar visível
            if hasattr(landmark, 'visibility') and landmark.visibility > 0.5:
                visible_count += 1
            elif not hasattr(landmark, 'visibility'):
                # Se não tem atributo visibility, assume visível se z não é muito negativo
                if landmark.z > -0.5:
                    visible_count += 1
        return visible_count
    
    def extract_landmarks_data(self, landmarks):
        """
        Extrai dados normalizados dos landmarks
        
        Args:
            landmarks: Lista de landmarks do MediaPipe
            
        Returns:
            dict: Dicionário com landmarks normalizados
        """
        if not landmarks:
            return None
        
        landmarks_data = {}
        for idx, landmark in enumerate(landmarks):
            landmarks_data[idx] = {
                'x': float(landmark.x),
                'y': float(landmark.y),
                'z': float(landmark.z),
                'visibility': float(getattr(landmark, 'visibility', 1.0))
            }
        
        return landmarks_data
    
    def validate_quality(self, frame, landmarks, pose_quality=None):
        """
        Valida qualidade do frame antes de coletar
        
        Args:
            frame: Frame da imagem
            landmarks: Landmarks do MediaPipe
            pose_quality: Feedback de qualidade da pose (opcional)
            
        Returns:
            tuple: (is_valid, reason, quality_metrics)
        """
        quality_metrics = {}
        
        # 1. Verifica blur
        blur_score = self.calculate_blur_score(frame)
        quality_metrics['blur_score'] = blur_score
        if blur_score < self.min_blur_threshold:
            return False, "Imagem muito borrada", quality_metrics
        
        # 2. Verifica visibilidade de landmarks
        visible_count = self.count_visible_landmarks(landmarks)
        quality_metrics['visible_landmarks'] = visible_count
        quality_metrics['total_landmarks'] = len(landmarks) if landmarks else 0
        if visible_count < self.min_visible_landmarks:
            return False, f"Poucos landmarks visíveis ({visible_count}/{quality_metrics['total_landmarks']})", quality_metrics
        
        # 3. Verifica duplicatas (similaridade com último frame)
        frame_hash = self.calculate_frame_hash(frame)
        if frame_hash == self.last_frame_hash:
            return False, "Frame duplicado", quality_metrics
        
        # 4. Verifica tamanho mínimo do frame
        h, w = frame.shape[:2]
        quality_metrics['frame_size'] = {'width': int(w), 'height': int(h)}
        if w < 320 or h < 240:
            return False, "Frame muito pequeno", quality_metrics
        
        # 5. Verifica se pose está detectada
        if not landmarks:
            return False, "Nenhuma pose detectada", quality_metrics
        
        # Calcula score geral de qualidade
        visibility_ratio = visible_count / len(landmarks) if landmarks else 0
        quality_metrics['visibility_ratio'] = visibility_ratio
        quality_metrics['overall_quality'] = (
            blur_score / 500.0 * 0.4 +  # Peso 40% para blur
            visibility_ratio * 0.6  # Peso 60% para visibilidade
        )
        
        return True, "OK", quality_metrics
    
    def save_sample(self, frame, landmarks, pose_mode, label, pose_quality=None, 
                   quality_metrics=None, user_confirmed=True):
        """
        Salva uma amostra validada
        
        Args:
            frame: Frame da imagem
            landmarks: Landmarks do MediaPipe
            pose_mode: Modo da pose atual
            label: Label da amostra ('correct', 'incorrect', 'pending')
            pose_quality: Feedback de qualidade da pose
            quality_metrics: Métricas de qualidade calculadas
            user_confirmed: Se o usuário confirmou a label
        """
        # Incrementa contador
        if pose_mode not in self.counters:
            self.counters[pose_mode] = {}
        if label not in self.counters[pose_mode]:
            self.counters[pose_mode][label] = 0
        self.counters[pose_mode][label] += 1
        
        # Cria identificador único
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        sample_id = f"{pose_mode}_{label}_{timestamp}_{self.counters[pose_mode][label]:04d}"
        
        # Salva frame
        frame_filename = f"{sample_id}.jpg"
        frame_path = self.raw_dir / frame_filename
        cv2.imwrite(str(frame_path), frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
        
        # Extrai landmarks
        landmarks_data = self.extract_landmarks_data(landmarks)
        
        # Prepara metadados
        metadata = {
            'sample_id': sample_id,
            'timestamp': datetime.now().isoformat(),
            'pose_mode': pose_mode,
            'label': label,
            'user_confirmed': user_confirmed,
            'frame_filename': frame_filename,
            'frame_size': {
                'width': int(frame.shape[1]),
                'height': int(frame.shape[0])
            },
            'landmarks': landmarks_data,
            'quality_metrics': quality_metrics or {},
            'pose_quality_feedback': pose_quality
        }
        
        # Salva metadados em JSON
        metadata_filename = f"{sample_id}.json"
        metadata_path = self.annotations_dir / metadata_filename
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        # Atualiza hash do último frame
        self.last_frame_hash = self.calculate_frame_hash(frame)
        
        return sample_id, frame_filename
    
    def collect_sample(self, frame, landmarks, pose_mode, label='pending', 
                      pose_quality=None, force=False):
        """
        Coleta uma amostra com validação automática
        
        Args:
            frame: Frame da imagem
            landmarks: Landmarks do MediaPipe
            pose_mode: Modo da pose atual
            label: Label da amostra ('correct', 'incorrect', 'pending')
            pose_quality: Feedback de qualidade da pose
            force: Se True, ignora validações
            
        Returns:
            tuple: (success, message, sample_id)
        """
        if not force:
            # Valida qualidade
            is_valid, reason, quality_metrics = self.validate_quality(frame, landmarks, pose_quality)
            if not is_valid:
                return False, reason, None
        
        # Salva amostra
        sample_id, filename = self.save_sample(
            frame, landmarks, pose_mode, label, pose_quality, 
            quality_metrics if not force else None
        )
        
        return True, f"Coletado: {filename}", sample_id
    
    def get_statistics(self):
        """Retorna estatísticas da coleta"""
        stats = {
            'total_samples': 0,
            'by_pose': {},
            'by_label': {'correct': 0, 'incorrect': 0, 'pending': 0}
        }
        
        # Conta arquivos JSON (cada JSON = 1 amostra)
        for json_file in self.annotations_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    stats['total_samples'] += 1
                    
                    pose = metadata.get('pose_mode', 'unknown')
                    label = metadata.get('label', 'pending')
                    
                    if pose not in stats['by_pose']:
                        stats['by_pose'][pose] = {'correct': 0, 'incorrect': 0, 'pending': 0}
                    stats['by_pose'][pose][label] = stats['by_pose'][pose].get(label, 0) + 1
                    
                    stats['by_label'][label] = stats['by_label'].get(label, 0) + 1
            except Exception:
                continue
        
        return stats
    
    def export_for_training(self, output_path="data_for_training.json"):
        """
        Exporta dados coletados em formato adequado para treinamento
        
        Args:
            output_path: Caminho do arquivo de saída
        """
        training_data = []
        
        for json_file in self.annotations_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    
                    # Apenas amostras confirmadas pelo usuário
                    if not metadata.get('user_confirmed', False):
                        continue
                    
                    # Apenas labels corretas/incorretas (ignora pending)
                    label = metadata.get('label')
                    if label not in ['correct', 'incorrect']:
                        continue
                    
                    # Prepara dados de treinamento
                    sample = {
                        'sample_id': metadata['sample_id'],
                        'pose_mode': metadata['pose_mode'],
                        'label': label,
                        'frame_path': str(self.raw_dir / metadata['frame_filename']),
                        'landmarks': metadata['landmarks'],
                        'quality_metrics': metadata.get('quality_metrics', {}),
                        'timestamp': metadata['timestamp']
                    }
                    training_data.append(sample)
            except Exception:
                continue
        
        # Salva arquivo consolidado
        output_path = Path(output_path)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(training_data, f, indent=2, ensure_ascii=False)
        
        return len(training_data)

