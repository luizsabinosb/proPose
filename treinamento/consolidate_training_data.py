"""
Script para consolidar dados de treinamento de múltiplas fontes
Combina dados coletados manualmente, web scraping e processamento de imagens
"""
import json
from pathlib import Path
from typing import List, Dict
import sys

# Adiciona path do projeto
sys.path.insert(0, str(Path(__file__).parent.parent))

from proposing.data_collector import DataCollector


def load_json_data(file_path: Path) -> List[Dict]:
    """Carrega dados de um arquivo JSON"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception as e:
        print(f"⚠️ Erro ao carregar {file_path}: {e}")
        return []


def consolidate_all_sources(output_file: str = "data_for_training.json") -> int:
    """
    Consolida dados de todas as fontes
    
    Args:
        output_file: Arquivo de saída consolidado
        
    Returns:
        Número total de amostras consolidadas
    """
    print("="*60)
    print("🔄 Consolidando Dados de Treinamento")
    print("="*60)
    
    project_root = Path(__file__).resolve().parent.parent
    ml_data_dir = project_root / "ml" / "data"
    processed_dir = ml_data_dir / "processed"
    temp_manual_path = project_root / "temp_manual.json"
    output_path = Path(output_file)
    if not output_path.is_absolute():
        output_path = project_root / output_path

    all_samples = []
    
    # 1. Dados coletados manualmente (via DataCollector)
    print("\n1️⃣ Carregando dados coletados manualmente...")
    collector = DataCollector()
    collector.export_for_training(temp_manual_path)
    if temp_manual_path.exists():
        manual_samples = load_json_data(temp_manual_path)
        all_samples.extend(manual_samples)
        print(f"   ✅ {len(manual_samples)} amostras manuais")
        temp_manual_path.unlink()  # Remove temporário
    else:
        print("   ⚠️ Nenhum dado manual encontrado")
    
    # 2. Dados de web scraping (processados)
    print("\n2️⃣ Carregando dados de web scraping...")
    web_data_path = processed_dir / "web_training_data.json"
    if web_data_path.exists():
        web_samples = load_json_data(web_data_path)
        all_samples.extend(web_samples)
        print(f"   ✅ {len(web_samples)} amostras de web scraping")
    else:
        print("   ⚠️ Nenhum dado de web scraping encontrado")
    
    # 3. Dados de processamento de imagens/vídeos
    print("\n3️⃣ Carregando dados de imagens/vídeos processados...")
    if processed_dir.exists():
        for json_file in processed_dir.glob("*.json"):
            if json_file.name not in ["web_training_data.json"]:  # Evita duplicar
                samples = load_json_data(json_file)
                all_samples.extend(samples)
                print(f"   ✅ {len(samples)} amostras de {json_file.name}")
    
    # 4. Dados de poseInfo (referências de poses)
    print("\n4️⃣ Carregando dados de poseInfo...")
    pose_info_path = processed_dir / "pose_info_training_data.json"
    if pose_info_path.exists():
        pose_info_samples = load_json_data(pose_info_path)
        all_samples.extend(pose_info_samples)
        print(f"   ✅ {len(pose_info_samples)} amostras de referência de poses")
    else:
        print("   ⚠️ Nenhum dado de poseInfo encontrado")
        print("   💡 Execute: python process_pose_info.py para processar poseInfo")
    
    # 5. Remove duplicatas (baseado em sample_id ou hash de landmarks)
    print("\n5️⃣ Removendo duplicatas...")
    seen_ids = set()
    unique_samples = []
    duplicates = 0
    
    for sample in all_samples:
        sample_id = sample.get('sample_id', '')
        if sample_id and sample_id in seen_ids:
            duplicates += 1
            continue
        seen_ids.add(sample_id)
        unique_samples.append(sample)
    
    if duplicates > 0:
        print(f"   ⚠️ Removidas {duplicates} duplicatas")
    
    # 6. Estatísticas
    print("\n📊 Estatísticas:")
    print(f"   Total de amostras: {len(unique_samples)}")
    
    by_pose = {}
    by_label = {'correct': 0, 'incorrect': 0}
    by_source = {}
    
    for sample in unique_samples:
        pose = sample.get('pose_mode', 'unknown')
        label = sample.get('label', 'unknown')
        source = sample.get('source', 'unknown')
        
        if pose not in by_pose:
            by_pose[pose] = {'correct': 0, 'incorrect': 0}
        by_pose[pose][label] = by_pose[pose].get(label, 0) + 1
        
        if label in by_label:
            by_label[label] += 1
        
        by_source[source] = by_source.get(source, 0) + 1
    
    print(f"\n   Por Pose:")
    for pose, counts in by_pose.items():
        print(f"     {pose}: {counts.get('correct', 0)} corretas, {counts.get('incorrect', 0)} incorretas")
    
    print(f"\n   Por Label:")
    print(f"     Correct: {by_label['correct']}")
    print(f"     Incorrect: {by_label['incorrect']}")
    
    print(f"\n   Por Fonte:")
    for source, count in by_source.items():
        print(f"     {source}: {count}")
    
    # 7. Salva arquivo consolidado
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(unique_samples, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Dados consolidados salvos em: {output_path}")
    print(f"📦 Total: {len(unique_samples)} amostras únicas")
    
    return len(unique_samples)


def main():
    """Função principal"""
    num_samples = consolidate_all_sources()
    
    if num_samples > 0:
        print("\n💡 Próximos passos:")
        print("   1. Revise os dados consolidados se necessário")
        print("   2. Execute: python train_model.py")
        print("   3. Os modelos treinados serão usados automaticamente")
    else:
        print("\n⚠️ Nenhum dado encontrado para consolidar")
        print("💡 Colete dados primeiro usando:")
        print("   - Coleta manual (interface)")
        print("   - Web scraping (python web_scraper.py)")
        print("   - Processamento de imagens (python image_processor.py)")


if __name__ == "__main__":
    main()
