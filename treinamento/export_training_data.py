"""
Script para exportar dados coletados em formato adequado para treinamento
"""
import sys
from pathlib import Path

# Adiciona diretório pai ao path para importar bodyvision
sys.path.insert(0, str(Path(__file__).parent.parent))

from bodyvision.data_collector import DataCollector


def main():
    """Exporta dados coletados para formato de treinamento"""
    collector = DataCollector()
    
    print("📊 Estatísticas da Coleta:")
    print("-" * 50)
    stats = collector.get_statistics()
    print(f"Total de amostras: {stats['total_samples']}")
    print(f"\nPor Label:")
    for label, count in stats['by_label'].items():
        print(f"  {label}: {count}")
    
    print(f"\nPor Pose:")
    for pose, labels in stats['by_pose'].items():
        print(f"  {pose}:")
        for label, count in labels.items():
            print(f"    {label}: {count}")
    
    print("\n" + "-" * 50)
    print("📤 Exportando dados para treinamento...")
    
    output_file = "data_for_training.json"
    num_exported = collector.export_for_training(output_file)
    
    print(f"✅ Exportadas {num_exported} amostras válidas para '{output_file}'")
    print("\n💡 Próximos passos:")
    print("   - Use este arquivo para treinar modelos de ML")
    print("   - Apenas amostras confirmadas (correct/incorrect) são exportadas")
    print("   - Amostras 'pending' precisam ser confirmadas primeiro")


if __name__ == "__main__":
    main()

