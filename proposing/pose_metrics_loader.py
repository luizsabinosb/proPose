"""
Carregador de métricas dinâmicas extraídas da poseInfo
Permite que o sistema use métricas personalizadas ao invés de valores hardcoded
"""
import json
from pathlib import Path
from typing import Dict, Optional, List, Tuple
import re


class PoseMetricsLoader:
    """Carrega e processa métricas extraídas da poseInfo"""
    
    def __init__(self, metrics_file: Optional[str] = None):
        """
        Inicializa o carregador de métricas
        
        Args:
            metrics_file: Caminho para o arquivo JSON com métricas (opcional)
        """
        if metrics_file is None:
            project_root = Path(__file__).resolve().parent.parent
            preferred_path = project_root / "ml" / "data" / "processed" / "pose_info_training_data.json"
            legacy_path = project_root / "data_collected" / "processed" / "pose_info_training_data.json"
            metrics_file = preferred_path if preferred_path.exists() else legacy_path
        
        self.metrics_file = Path(metrics_file)
        self.metrics_cache: Dict[str, Dict] = {}
        self._load_metrics()
    
    def _load_metrics(self):
        """Carrega métricas do arquivo JSON"""
        if not self.metrics_file.exists():
            print(f"⚠️ Arquivo de métricas não encontrado: {self.metrics_file}")
            print("   Usando métricas padrão (hardcoded)")
            return
        
        try:
            with open(self.metrics_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Agrupa métricas por pose_mode
            for sample in data:
                pose_mode = sample.get('pose_mode')
                extracted_metrics = sample.get('extracted_metrics', {})
                
                if pose_mode and extracted_metrics:
                    # Se já existe, mescla (prioriza a mais recente)
                    if pose_mode not in self.metrics_cache:
                        self.metrics_cache[pose_mode] = extracted_metrics
                    else:
                        # Mescla métricas, priorizando novas
                        self._merge_metrics(self.metrics_cache[pose_mode], extracted_metrics)
            
            print(f"✅ Carregadas métricas para {len(self.metrics_cache)} pose(s)")
            
        except Exception as e:
            print(f"⚠️ Erro ao carregar métricas: {e}")
            print("   Usando métricas padrão (hardcoded)")
    
    def _merge_metrics(self, base: Dict, new: Dict):
        """Mescla métricas, priorizando as novas"""
        # Mescla ângulos
        if 'angles' in new:
            if 'angles' not in base:
                base['angles'] = {}
            base['angles'].update(new['angles'])
        
        # Mescla requisitos (adiciona únicos)
        if 'requirements' in new:
            if 'requirements' not in base:
                base['requirements'] = []
            for req in new['requirements']:
                if req not in base['requirements']:
                    base['requirements'].append(req)
        
        # Mescla notas (adiciona únicas)
        if 'notes' in new:
            if 'notes' not in base:
                base['notes'] = []
            for note in new['notes']:
                if note not in base['notes']:
                    base['notes'].append(note)
    
    def get_angle_ranges(self, pose_mode: str) -> List[Tuple[float, float]]:
        """
        Extrai intervalos de ângulos para uma pose
        
        Args:
            pose_mode: Modo da pose (ex: 'side_chest')
            
        Returns:
            Lista de tuplas (min, max) com intervalos de ângulos
        """
        if pose_mode not in self.metrics_cache:
            return []
        
        metrics = self.metrics_cache[pose_mode]
        angles = metrics.get('angles', {})
        ranges = []
        
        for key, value in angles.items():
            if isinstance(value, dict):
                if 'min' in value and 'max' in value:
                    ranges.append((float(value['min']), float(value['max'])))
                elif 'value' in value:
                    # Ângulo único - cria intervalo pequeno ao redor
                    val = float(value['value'])
                    ranges.append((val - 5, val + 5))
        
        return ranges
    
    def get_primary_angle_range(self, pose_mode: str) -> Optional[Tuple[float, float]]:
        """
        Retorna o intervalo de ângulo principal para uma pose
        
        Args:
            pose_mode: Modo da pose
            
        Returns:
            Tupla (min, max) ou None se não encontrado
        """
        ranges = self.get_angle_ranges(pose_mode)
        if ranges:
            # Retorna o primeiro intervalo (assumindo que é o principal)
            return ranges[0]
        return None
    
    def get_requirements(self, pose_mode: str) -> List[str]:
        """
        Retorna requisitos extraídos do texto
        
        Args:
            pose_mode: Modo da pose
            
        Returns:
            Lista de requisitos (ex: ['extended', 'rotated'])
        """
        if pose_mode not in self.metrics_cache:
            return []
        
        return self.metrics_cache[pose_mode].get('requirements', [])
    
    def get_notes(self, pose_mode: str) -> List[str]:
        """
        Retorna notas importantes extraídas do texto
        
        Args:
            pose_mode: Modo da pose
            
        Returns:
            Lista de notas
        """
        if pose_mode not in self.metrics_cache:
            return []
        
        return self.metrics_cache[pose_mode].get('notes', [])
    
    def has_metrics(self, pose_mode: str) -> bool:
        """Verifica se existem métricas para uma pose"""
        return pose_mode in self.metrics_cache and bool(self.metrics_cache[pose_mode])
    
    def get_all_metrics(self, pose_mode: str) -> Dict:
        """Retorna todas as métricas para uma pose"""
        return self.metrics_cache.get(pose_mode, {})
    
    def parse_angle_from_text(self, text: str, pose_mode: str) -> Optional[Tuple[float, float]]:
        """
        Tenta extrair intervalo de ângulo diretamente do texto
        
        Args:
            text: Texto a ser analisado
            pose_mode: Modo da pose (para contexto)
            
        Returns:
            Tupla (min, max) ou None
        """
        # Padrões para encontrar intervalos de ângulos
        patterns = [
            r'(\d+)[°º]\s*[-–]\s*(\d+)[°º]',  # 80° - 100°
            r'(\d+)\s*[-–]\s*(\d+)\s*graus?',  # 80 - 100 graus
            r'~?(\d+)[°º]',  # ~90°
            r'(\d+)\s*graus?',  # 90 graus
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match.groups()) == 2:
                    min_angle = float(match.group(1))
                    max_angle = float(match.group(2))
                    return (min_angle, max_angle)
                elif len(match.groups()) == 1:
                    angle = float(match.group(1))
                    return (angle - 10, angle + 10)  # Intervalo de ±10°
        
        return None


# Instância global (singleton)
_metrics_loader: Optional[PoseMetricsLoader] = None


def get_metrics_loader() -> PoseMetricsLoader:
    """Retorna instância global do carregador de métricas"""
    global _metrics_loader
    if _metrics_loader is None:
        _metrics_loader = PoseMetricsLoader()
    return _metrics_loader


def reload_metrics():
    """Recarrega métricas do arquivo"""
    global _metrics_loader
    _metrics_loader = None
    return get_metrics_loader()
