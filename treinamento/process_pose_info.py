"""
Script para processar informações de poses da pasta ml/pose_info
Extrai texto de arquivos .pages e processa imagens para treinamento
"""
import cv2
import numpy as np
import json
import subprocess
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import sys
from datetime import datetime
import zipfile
import xml.etree.ElementTree as ET

# Adiciona path do projeto
sys.path.insert(0, str(Path(__file__).parent.parent))

from proposing.pose_evaluator import PoseDetector


class PoseInfoProcessor:
    """Processa informações de poses da pasta ml/pose_info"""
    
    # Mapeamento de nomes de pastas para modos de pose
    POSE_MAPPING = {
        'Double Biceps': 'double_biceps',
        'Side Chest': 'side_chest',
        'Side Triceps': 'side_triceps',
        'Most Muscular': 'most_muscular'
    }
    
    def __init__(self, pose_info_dir: Optional[str] = None, output_dir: Optional[str] = None):
        """
        Inicializa o processador
        
        Args:
            pose_info_dir: Diretório com informações de poses
            output_dir: Diretório onde salvar dados processados
        """
        project_root = Path(__file__).resolve().parent.parent
        self.pose_info_dir = Path(pose_info_dir) if pose_info_dir else project_root / "ml" / "pose_info"
        self.output_dir = Path(output_dir) if output_dir else project_root / "ml" / "data" / "processed"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.detector = PoseDetector(static_image_mode=True)
    
    def extract_text_from_pages(self, pages_path: Path) -> Optional[str]:
        """
        Extrai texto de um arquivo .pages
        
        Args:
            pages_path: Caminho do arquivo .pages
            
        Returns:
            Texto extraído ou None se falhar
        """
        try:
            # Método 1: Usa textutil (macOS)
            try:
                result = subprocess.run(
                    ['textutil', '-convert', 'txt', '-stdout', str(pages_path)],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0 and result.stdout.strip():
                    return result.stdout.strip()
            except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
                pass
            
            # Método 2: Extrai do bundle .pages (é um zip)
            try:
                with zipfile.ZipFile(pages_path, 'r') as zip_ref:
                    # Procura por arquivos de preview ou index
                    for file_info in zip_ref.namelist():
                        if 'preview' in file_info.lower() or 'index' in file_info.lower():
                            content = zip_ref.read(file_info)
                            # Tenta extrair texto do XML
                            try:
                                root = ET.fromstring(content)
                                # Procura por elementos de texto
                                texts = []
                                for elem in root.iter():
                                    if elem.text and elem.text.strip():
                                        texts.append(elem.text.strip())
                                if texts:
                                    return '\n'.join(texts)
                            except:
                                pass
            except:
                pass
            
            # Método 3: Tenta ler como texto simples (às vezes funciona)
            try:
                with open(pages_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    # Procura por padrões de texto legível
                    if len(content) > 100 and any(c.isalpha() for c in content[:500]):
                        return content[:5000]  # Limita tamanho
            except:
                pass
            
            print(f"⚠️ Não foi possível extrair texto de: {pages_path}")
            return None
            
        except Exception as e:
            print(f"⚠️ Erro ao extrair texto de {pages_path}: {e}")
            return None
    
    def extract_metrics_from_text(self, text: str, pose_mode: str) -> Dict:
        """
        Extrai métricas e informações relevantes do texto
        
        Args:
            text: Texto extraído
            pose_mode: Modo da pose
            
        Returns:
            Dict com métricas extraídas
        """
        metrics = {
            'angles': {},
            'requirements': [],
            'notes': []
        }
        
        # Padrões para extrair ângulos
        angle_patterns = [
            r'(\d+)[°º]\s*[-–]\s*(\d+)[°º]',  # 80° - 100°
            r'(\d+)\s*[-–]\s*(\d+)\s*graus?',  # 80 - 100 graus
            r'~?(\d+)[°º]',  # ~90°
            r'(\d+)\s*graus?',  # 90 graus
        ]
        
        for pattern in angle_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match.groups()) == 2:
                    # Intervalo de ângulos
                    min_angle = int(match.group(1))
                    max_angle = int(match.group(2))
                    metrics['angles'][f'range_{len(metrics["angles"])}'] = {
                        'min': min_angle,
                        'max': max_angle
                    }
                elif len(match.groups()) == 1:
                    # Ângulo único
                    angle = int(match.group(1))
                    metrics['angles'][f'single_{len(metrics["angles"])}'] = {
                        'value': angle
                    }
        
        # Extrai palavras-chave importantes
        keywords = {
            'extended': ['estendido', 'extended', 'estender', 'extend'],
            'flexed': ['flexionado', 'flexed', 'flexão', 'flex'],
            'rotated': ['rotacionado', 'rotated', 'rotação', 'rotation'],
            'contracted': ['contraído', 'contracted', 'contração', 'contraction'],
            'aligned': ['alinhado', 'aligned', 'alinhamento', 'alignment']
        }
        
        text_lower = text.lower()
        for key, terms in keywords.items():
            for term in terms:
                if term in text_lower:
                    metrics['requirements'].append(key)
                    break
        
        # Extrai notas importantes (linhas com palavras-chave)
        lines = text.split('\n')
        important_keywords = ['braço', 'arm', 'joelho', 'knee', 'ombro', 'shoulder', 
                             'cotovelo', 'elbow', 'tronco', 'torso', 'pé', 'foot']
        for line in lines:
            if any(kw in line.lower() for kw in important_keywords):
                if len(line.strip()) > 10:  # Ignora linhas muito curtas
                    metrics['notes'].append(line.strip())
        
        return metrics
    
    def process_pose_folder(self, pose_folder: Path) -> List[Dict]:
        """
        Processa uma pasta de pose (ex: "Side Chest/")
        
        Args:
            pose_folder: Pasta com informações da pose
            
        Returns:
            Lista de dados processados
        """
        pose_name = pose_folder.name
        pose_mode = self.POSE_MAPPING.get(pose_name)
        
        if not pose_mode:
            print(f"⚠️ Pose desconhecida: {pose_name}")
            return []
        
        print(f"\n{'='*60}")
        print(f"📌 Processando: {pose_name} ({pose_mode})")
        print(f"{'='*60}")
        
        samples = []
        
        # 1. Encontra arquivos na pasta da pose
        image_files = []
        pages_files = []
        other_files = []
        
        print(f"\n🔍 Analisando arquivos em: {pose_folder.name}/")
        for file_path in pose_folder.iterdir():
            if file_path.is_file():
                suffix = file_path.suffix.lower()
                if suffix in ['.jpg', '.jpeg', '.png', '.webp']:
                    image_files.append(file_path)
                elif suffix == '.pages':
                    pages_files.append(file_path)
                elif not file_path.name.startswith('.'):  # Ignora arquivos ocultos
                    other_files.append(file_path)
        
        print(f"   📷 Imagens encontradas: {len(image_files)}")
        print(f"   📄 Arquivos .pages: {len(pages_files)}")
        if other_files:
            print(f"   📁 Outros arquivos: {len(other_files)} (serão ignorados)")
        
        if not image_files:
            print(f"\n⚠️ Nenhuma imagem encontrada em {pose_folder.name}/")
            print(f"   💡 Adicione imagens de referência (.jpg, .png, etc.)")
            return []
        
        # 2. Extrai texto dos arquivos .pages
        extracted_text = ""
        if pages_files:
            print(f"\n📄 Extraindo texto de {len(pages_files)} arquivo(s) .pages...")
            print(f"   Arquivos encontrados: {[f.name for f in pages_files]}")
            for pages_file in pages_files:
                print(f"   📖 Processando: {pages_file.name}...")
                text = self.extract_text_from_pages(pages_file)
                if text:
                    extracted_text += f"\n\n--- {pages_file.name} ---\n{text}"
                    print(f"   ✅ Texto extraído: {len(text)} caracteres")
                else:
                    print(f"   ⚠️ Não foi possível extrair texto de {pages_file.name}")
        else:
            print(f"\n⚠️ Nenhum arquivo .pages encontrado em {pose_folder.name}")
            print(f"   💡 Adicione arquivos .pages com informações sobre a pose")
        
        # 3. Extrai métricas do texto
        metrics = {}
        if extracted_text:
            print(f"\n📊 Extraindo métricas do texto...")
            metrics = self.extract_metrics_from_text(extracted_text, pose_mode)
            print(f"   ✅ {len(metrics.get('angles', {}))} ângulo(s) encontrado(s)")
            print(f"   ✅ {len(metrics.get('requirements', []))} requisito(s) encontrado(s)")
            print(f"   ✅ {len(metrics.get('notes', []))} nota(s) encontrada(s)")
        
        # 4. Processa imagens
        print(f"\n🖼️ Processando {len(image_files)} imagem(ns)...")
        for i, image_path in enumerate(image_files, 1):
            print(f"\n[{i}/{len(image_files)}] Processando: {image_path.name}")
            
            # Processa imagem diretamente
            sample = self._process_image_direct(
                image_path, 
                pose_mode,
                pose_name,
                extracted_text,
                metrics,
                pages_files[0] if pages_files else None
            )
            
            if sample:
                samples.append(sample)
                print(f"   ✅ Processada com sucesso")
            else:
                print(f"   ⚠️ Falha ao processar imagem")
        
        return samples
    
    def _process_image_direct(self, image_path: Path, pose_mode: str, pose_name: str,
                              extracted_text: str, metrics: Dict, text_file: Optional[str]) -> Optional[Dict]:
        """
        Processa uma imagem diretamente sem usar ImageProcessor
        
        Args:
            image_path: Caminho da imagem
            pose_mode: Modo da pose
            pose_name: Nome da pose
            extracted_text: Texto extraído
            metrics: Métricas extraídas
            text_file: Arquivo de texto original
            
        Returns:
            Dict com dados processados ou None se falhar
        """
        try:
            # Carrega imagem
            frame = cv2.imread(str(image_path))
            if frame is None:
                return None
            
            h, w = frame.shape[:2]
            
            # Processa com MediaPipe
            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.detector.pose.process(image_rgb)
            
            if not results.pose_landmarks:
                return None
            
            landmarks = results.pose_landmarks.landmark
            
            # Extrai landmarks para dict
            landmarks_dict = {}
            for idx, landmark in enumerate(landmarks):
                landmarks_dict[idx] = {
                    'x': float(landmark.x),
                    'y': float(landmark.y),
                    'z': float(landmark.z),
                    'visibility': float(getattr(landmark, 'visibility', 1.0))
                }
            
            # Prepara dados para treinamento
            sample_data = {
                'image_path': str(image_path),
                'pose_mode': pose_mode,
                'label': 'correct',  # Imagens de referência são sempre corretas
                'landmarks': landmarks_dict,
                'frame_size': {'width': int(w), 'height': int(h)},
                'timestamp': datetime.now().isoformat(),
                'source': 'pose_info',
                'pose_name': pose_name,
                'reference_image': True,
                'extracted_text': extracted_text if extracted_text else None,
                'extracted_metrics': metrics,
                'text_file': str(text_file) if text_file else None,
                'evaluation': {
                    'errors': [],
                    'warnings': [],
                    'score': 1.0  # Imagens de referência têm score máximo
                }
            }
            
            return sample_data
            
        except Exception as e:
            print(f"   ⚠️ Erro ao processar {image_path}: {e}")
            return None
    
    def process_all_poses(self) -> List[Dict]:
        """
        Processa todas as poses na pasta ml/pose_info
        
        Returns:
            Lista de todas as amostras processadas
        """
        if not self.pose_info_dir.exists():
            print(f"❌ Diretório não encontrado: {self.pose_info_dir}")
            return []
        
        print("="*60)
        print("🎯 Processador de Informações de Poses")
        print("="*60)
        print(f"📁 Diretório: {self.pose_info_dir}")
        print("\n📋 Estrutura esperada:")
        print("   ml/pose_info/")
        print("   ├── Double Biceps/     (arquivos .pages + imagens)")
        print("   ├── Side Chest/         (arquivos .pages + imagens)")
        print("   ├── Side Triceps/       (arquivos .pages + imagens)")
        print("   └── Most Muscular/      (arquivos .pages + imagens)")
        print("\n💡 Cada pasta contém:")
        print("   - Arquivo(s) .pages com informações textuais da pose")
        print("   - Imagem(ns) de referência (.jpg, .png, etc.)")
        
        all_samples = []
        
        # Processa cada pasta de pose
        pose_folders = [f for f in sorted(self.pose_info_dir.iterdir()) 
                       if f.is_dir() and not f.name.startswith('.')]
        
        if not pose_folders:
            print(f"\n⚠️ Nenhuma pasta de pose encontrada em {self.pose_info_dir}")
            return []
        
        print(f"\n📂 Encontradas {len(pose_folders)} pasta(s) de pose(s):")
        for folder in pose_folders:
            print(f"   - {folder.name}")
        
        for pose_folder in pose_folders:
            samples = self.process_pose_folder(pose_folder)
            all_samples.extend(samples)
        
        return all_samples
    
    def save_training_data(self, samples: List[Dict], output_file: str = "pose_info_training_data.json"):
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
                'sample_id': f"pose_info_{Path(sample['image_path']).stem}",
                'pose_mode': sample['pose_mode'],
                'label': sample['label'],
                'frame_path': sample['image_path'],
                'landmarks': sample['landmarks'],
                'quality_metrics': {
                    'evaluation_score': sample['evaluation']['score'],
                    'error_count': len(sample['evaluation']['errors'])
                },
                'timestamp': sample['timestamp'],
                'source': sample.get('source', 'pose_info'),
                'reference_image': sample.get('reference_image', False),
                'extracted_metrics': sample.get('extracted_metrics', {}),
                'pose_name': sample.get('pose_name', '')
            })
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(training_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Salvos {len(training_data)} amostras em: {output_path}")
        return output_path


def main():
    """Função principal"""
    processor = PoseInfoProcessor()
    
    # Processa todas as poses
    samples = processor.process_all_poses()
    
    if samples:
        # Salva dados
        output_file = processor.save_training_data(samples)
        
        print("\n" + "="*60)
        print("✅ Processamento Concluído!")
        print("="*60)
        print(f"\n📊 Estatísticas:")
        print(f"   Total de amostras: {len(samples)}")
        
        by_pose = {}
        for sample in samples:
            pose = sample.get('pose_mode', 'unknown')
            by_pose[pose] = by_pose.get(pose, 0) + 1
        
        for pose, count in by_pose.items():
            print(f"   {pose}: {count} amostra(s)")
        
        print(f"\n💡 Próximos passos:")
        print(f"   1. Revise os dados em: {output_file}")
        print(f"   2. Execute: python consolidate_training_data.py")
        print(f"   3. Execute: python train_model.py")
    else:
        print("\n⚠️ Nenhuma amostra processada")
        print("💡 Verifique se a pasta ml/pose_info existe e contém imagens válidas")


if __name__ == "__main__":
    main()
