"""
Script para processar imagens/vídeos e extrair landmarks para treinamento
Usa as regras atuais para gerar labels automáticos
"""
import cv2
import numpy as np
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import sys
from datetime import datetime

# Adiciona path do projeto
sys.path.insert(0, str(Path(__file__).parent.parent))

from bodyvision.pose_evaluator import PoseDetector, MLEvaluator
from bodyvision.data_collector import DataCollector


class ImageProcessor:
    """Processa imagens/vídeos e gera dados de treinamento"""
    
    def __init__(self, output_dir="data_collected/processed"):
        """
        Inicializa o processador
        
        Args:
            output_dir: Diretório onde salvar dados processados
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.detector = PoseDetector(static_image_mode=True)
        self.data_collector = DataCollector()
    
    def process_image(self, image_path: Path, pose_mode: str, 
                     expected_label: Optional[str] = None) -> Optional[Dict]:
        """
        Processa uma imagem e extrai landmarks
        
        Args:
            image_path: Caminho da imagem
            pose_mode: Modo da pose ('double_biceps', 'side_chest', etc.)
            expected_label: Label esperado ('correct' ou 'incorrect'), None = auto-detecta
            
        Returns:
            Dict com dados processados ou None se falhar
        """
        try:
            # Carrega imagem
            frame = cv2.imread(str(image_path))
            if frame is None:
                print(f"⚠️ Não foi possível carregar: {image_path}")
                return None
            
            h, w = frame.shape[:2]
            
            # Processa com MediaPipe
            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.detector.pose.process(image_rgb)
            
            if not results.pose_landmarks:
                print(f"⚠️ Nenhuma pose detectada em: {image_path}")
                return None
            
            landmarks = results.pose_landmarks.landmark
            
            # Extrai keypoints
            keypoints = self._extract_keypoints(landmarks, w, h)
            if not keypoints:
                print(f"⚠️ Não foi possível extrair keypoints de: {image_path}")
                return None
            
            # Calcula ângulos
            angles = self._calculate_angles(keypoints)
            
            # Avalia pose usando regras atuais
            evaluation = self._evaluate_pose(pose_mode, keypoints, angles, w)
            
            # Determina label
            if expected_label:
                label = expected_label
            else:
                # Auto-detecta baseado na avaliação
                # Se não há erros ou apenas avisos, considera correto
                errors = [e for e in evaluation.get('errors', []) if not e.startswith('⚠️')]
                label = 'correct' if len(errors) == 0 else 'incorrect'
            
            # Prepara dados para treinamento
            sample_data = {
                'image_path': str(image_path),
                'pose_mode': pose_mode,
                'label': label,
                'landmarks': self._landmarks_to_dict(landmarks),
                'keypoints': keypoints,
                'angles': angles,
                'evaluation': evaluation,
                'frame_size': {'width': int(w), 'height': int(h)},
                'timestamp': datetime.now().isoformat(),
                'source': 'web_scraping'
            }
            
            return sample_data
            
        except Exception as e:
            print(f"❌ Erro ao processar {image_path}: {e}")
            return None
    
    def process_video(self, video_path: Path, pose_mode: str, 
                     sample_rate: int = 30, max_frames: int = 100) -> List[Dict]:
        """
        Processa um vídeo e extrai frames
        
        Args:
            video_path: Caminho do vídeo
            pose_mode: Modo da pose
            sample_rate: A cada quantos frames processar (1 = todos)
            max_frames: Máximo de frames para processar
            
        Returns:
            Lista de dados processados
        """
        try:
            cap = cv2.VideoCapture(str(video_path))
            if not cap.isOpened():
                print(f"⚠️ Não foi possível abrir vídeo: {video_path}")
                return []
            
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            print(f"📹 Processando vídeo: {total_frames} frames @ {fps} fps")
            
            samples = []
            frame_count = 0
            processed_count = 0
            
            while processed_count < max_frames:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Processa apenas a cada sample_rate frames
                if frame_count % sample_rate == 0:
                    # Salva frame temporário
                    temp_frame_path = self.output_dir / f"temp_frame_{processed_count}.jpg"
                    cv2.imwrite(str(temp_frame_path), frame)
                    
                    # Processa frame
                    sample = self.process_image(temp_frame_path, pose_mode)
                    if sample:
                        sample['video_path'] = str(video_path)
                        sample['frame_number'] = frame_count
                        sample['timestamp_video'] = frame_count / fps
                        samples.append(sample)
                    
                    # Remove frame temporário
                    temp_frame_path.unlink()
                    processed_count += 1
                
                frame_count += 1
            
            cap.release()
            print(f"✅ Processados {len(samples)} frames do vídeo")
            return samples
            
        except Exception as e:
            print(f"❌ Erro ao processar vídeo {video_path}: {e}")
            return []
    
    def _extract_keypoints(self, landmarks, width: int, height: int) -> Optional[Dict]:
        """Extrai keypoints dos landmarks"""
        try:
            points = {}
            
            # Pontos principais
            key_indices = {
                'nose': 0,
                'left_shoulder': 11, 'right_shoulder': 12,
                'left_elbow': 13, 'right_elbow': 14,
                'left_wrist': 15, 'right_wrist': 16,
                'left_hip': 23, 'right_hip': 24,
                'left_knee': 25, 'right_knee': 26,
                'left_ankle': 27, 'right_ankle': 28
            }
            
            for name, idx in key_indices.items():
                lm = landmarks[idx]
                points[name] = {
                    'x': lm.x * width,
                    'y': lm.y * height,
                    'z': lm.z,
                    'visibility': getattr(lm, 'visibility', 1.0)
                }
            
            return points
        except:
            return None
    
    def _calculate_angles(self, keypoints: Dict) -> Dict:
        """Calcula ângulos importantes"""
        angles = {}
        
        try:
            # Ângulo do braço esquerdo
            if all(k in keypoints for k in ['left_shoulder', 'left_elbow', 'left_wrist']):
                angles['left_arm'] = self.detector.calculate_angle(
                    [keypoints['left_shoulder']['x'], keypoints['left_shoulder']['y']],
                    [keypoints['left_elbow']['x'], keypoints['left_elbow']['y']],
                    [keypoints['left_wrist']['x'], keypoints['left_wrist']['y']]
                )
            
            # Ângulo do braço direito
            if all(k in keypoints for k in ['right_shoulder', 'right_elbow', 'right_wrist']):
                angles['right_arm'] = self.detector.calculate_angle(
                    [keypoints['right_shoulder']['x'], keypoints['right_shoulder']['y']],
                    [keypoints['right_elbow']['x'], keypoints['right_elbow']['y']],
                    [keypoints['right_wrist']['x'], keypoints['right_wrist']['y']]
                )
            
            # Adicione mais ângulos conforme necessário
            
        except Exception as e:
            print(f"⚠️ Erro ao calcular ângulos: {e}")
        
        return angles
    
    def _evaluate_pose(self, pose_mode: str, keypoints: Dict, angles: Dict, width: int) -> Dict:
        """Avalia pose usando regras atuais"""
        # Esta função deve usar a mesma lógica de avaliação do sistema principal
        # Por enquanto, retorna estrutura básica
        # TODO: Integrar com pose_evaluator.py
        
        evaluation = {
            'errors': [],
            'warnings': [],
            'score': 0.0
        }
        
        # Placeholder - deve usar as regras reais
        # Por exemplo, para double_biceps:
        if pose_mode == 'double_biceps':
            if 'left_arm' in angles and 'right_arm' in angles:
                left_angle = angles['left_arm']
                right_angle = angles['right_arm']
                
                # Verifica se está no intervalo correto (80-100°)
                if not (80 <= left_angle <= 100):
                    evaluation['errors'].append(f"Braço esquerdo fora do ângulo ideal (atual: {left_angle:.0f}°)")
                if not (80 <= right_angle <= 100):
                    evaluation['errors'].append(f"Braço direito fora do ângulo ideal (atual: {right_angle:.0f}°)")
        
        # Calcula score (0-1)
        max_errors = 5
        error_count = len(evaluation['errors'])
        evaluation['score'] = max(0.0, 1.0 - (error_count / max_errors))
        
        return evaluation
    
    def _landmarks_to_dict(self, landmarks) -> Dict:
        """Converte landmarks do MediaPipe para dict"""
        landmarks_dict = {}
        for idx, landmark in enumerate(landmarks):
            landmarks_dict[idx] = {
                'x': float(landmark.x),
                'y': float(landmark.y),
                'z': float(landmark.z),
                'visibility': float(getattr(landmark, 'visibility', 1.0))
            }
        return landmarks_dict
    
    def process_directory(self, dir_path: Path, pose_mode: str, 
                         is_video: bool = False) -> List[Dict]:
        """
        Processa um diretório de imagens ou vídeos
        
        Args:
            dir_path: Diretório com imagens/vídeos
            pose_mode: Modo da pose
            is_video: Se True, processa como vídeos
            
        Returns:
            Lista de dados processados
        """
        all_samples = []
        
        if is_video:
            video_extensions = ['.mp4', '.avi', '.mov', '.mkv']
            files = [f for f in dir_path.iterdir() 
                    if f.suffix.lower() in video_extensions]
        else:
            image_extensions = ['.jpg', '.jpeg', '.png', '.webp']
            files = [f for f in dir_path.iterdir() 
                    if f.suffix.lower() in image_extensions]
        
        print(f"📁 Encontrados {len(files)} arquivos para processar")
        
        for i, file_path in enumerate(files, 1):
            print(f"\n[{i}/{len(files)}] Processando: {file_path.name}")
            
            if is_video:
                samples = self.process_video(file_path, pose_mode)
            else:
                sample = self.process_image(file_path, pose_mode)
                samples = [sample] if sample else []
            
            all_samples.extend(samples)
        
        return all_samples
    
    def save_training_data(self, samples: List[Dict], output_file: str = "web_training_data.json"):
        """
        Salva dados processados em formato de treinamento
        
        Args:
            samples: Lista de amostras processadas
            output_file: Nome do arquivo de saída
        """
        output_path = self.output_dir / output_file
        
        # Converte para formato compatível com train_model.py
        training_data = []
        for sample in samples:
            training_data.append({
                'sample_id': f"web_{Path(sample['image_path']).stem}",
                'pose_mode': sample['pose_mode'],
                'label': sample['label'],
                'frame_path': sample['image_path'],
                'landmarks': sample['landmarks'],
                'quality_metrics': {
                    'evaluation_score': sample['evaluation']['score'],
                    'error_count': len(sample['evaluation']['errors'])
                },
                'timestamp': sample['timestamp'],
                'source': sample.get('source', 'web_scraping')
            })
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(training_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Salvos {len(training_data)} amostras em: {output_path}")
        return output_path


def main():
    """Função principal"""
    print("="*60)
    print("🖼️ Processador de Imagens/Vídeos para Treinamento")
    print("="*60)
    
    processor = ImageProcessor()
    
    print("\n📋 Escolha a fonte:")
    print("1. Diretório de imagens")
    print("2. Diretório de vídeos")
    print("3. Arquivo de imagem único")
    print("4. Arquivo de vídeo único")
    
    choice = input("\nEscolha (1/2/3/4): ").strip()
    
    # Pede modo da pose
    print("\n📌 Modo da pose:")
    print("  - double_biceps")
    print("  - side_chest")
    print("  - side_triceps")
    print("  - most_muscular")
    print("  - enquadramento")
    pose_mode = input("Digite o modo: ").strip()
    
    if choice == '1':
        dir_path = Path(input("Caminho do diretório de imagens: ").strip())
        samples = processor.process_directory(dir_path, pose_mode, is_video=False)
        
    elif choice == '2':
        dir_path = Path(input("Caminho do diretório de vídeos: ").strip())
        samples = processor.process_directory(dir_path, pose_mode, is_video=True)
        
    elif choice == '3':
        file_path = Path(input("Caminho da imagem: ").strip())
        sample = processor.process_image(file_path, pose_mode)
        samples = [sample] if sample else []
        
    elif choice == '4':
        file_path = Path(input("Caminho do vídeo: ").strip())
        samples = processor.process_video(file_path, pose_mode)
        
    else:
        print("❌ Opção inválida")
        return
    
    if samples:
        # Pergunta label esperado
        print("\n🏷️ Label esperado (deixe vazio para auto-detectar):")
        print("  - correct")
        print("  - incorrect")
        expected_label = input("Digite o label (ou Enter): ").strip() or None
        
        if expected_label:
            for sample in samples:
                sample['label'] = expected_label
        
        # Salva dados
        output_file = processor.save_training_data(samples)
        print(f"\n✅ Processamento concluído!")
        print(f"💡 Próximo passo: Execute 'python export_training_data.py' para consolidar")
        print(f"💡 Depois: Execute 'python train_model.py' para treinar")
    else:
        print("\n⚠️ Nenhuma amostra processada")


if __name__ == "__main__":
    main()
