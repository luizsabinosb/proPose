"""
Script para treinar modelo de Machine Learning com dados coletados
Treina um modelo que melhora a avaliação de poses baseado em dados reais
"""
import json
import numpy as np
import sys
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import warnings
warnings.filterwarnings('ignore')

# Adiciona diretório pai ao path
sys.path.insert(0, str(Path(__file__).parent.parent))


def load_training_data(data_file="data_for_training.json"):
    """Carrega dados de treinamento do arquivo JSON"""
    # Tenta encontrar arquivo na raiz ou em treinamento/
    data_path = Path(data_file)
    if not data_path.exists():
        # Tenta na raiz do projeto
        data_path = Path(__file__).parent.parent / data_file
        if not data_path.exists():
            print(f"❌ Arquivo {data_file} não encontrado!")
            print("💡 Execute primeiro:")
            print("   - python export_training_data.py (dados manuais)")
            print("   - python consolidate_training_data.py (consolidar todas as fontes)")
            return None, None, None
    data_file = str(data_path)
    
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if len(data) == 0:
        print("❌ Nenhum dado de treinamento encontrado!")
        print("💡 Colete dados primeiro usando o BodyVision (teclas V, X)")
        return None, None, None
    
    print(f"📊 Carregados {len(data)} amostras de treinamento")
    return data


def extract_features(landmarks_data):
    """
    Extrai features dos landmarks para treinamento
    
    Features extraídas:
    - Coordenadas normalizadas de pontos-chave (x, y, z, visibility)
    - Distâncias entre pontos importantes
    - Ângulos calculados
    """
    if not landmarks_data:
        return None
    
    # Converte landmarks para array numpy
    features = []
    
    # Features: coordenadas dos pontos principais (33 landmarks do MediaPipe)
    key_landmarks = [
        0,   # nose
        11, 12,  # shoulders
        13, 14,  # elbows
        15, 16,  # wrists
        23, 24,  # hips
        25, 26,  # knees
        27, 28,  # ankles
    ]
    
    for idx in key_landmarks:
        if str(idx) in landmarks_data:
            lm = landmarks_data[str(idx)]
            features.extend([lm['x'], lm['y'], lm['z'], lm.get('visibility', 1.0)])
        else:
            features.extend([0.0, 0.0, 0.0, 0.0])  # Padding se não existir
    
    # Features adicionais: distâncias importantes
    if all(str(i) in landmarks_data for i in [11, 12]):  # Shoulders
        left_shoulder = landmarks_data['11']
        right_shoulder = landmarks_data['12']
        shoulder_width = np.sqrt(
            (left_shoulder['x'] - right_shoulder['x'])**2 +
            (left_shoulder['y'] - right_shoulder['y'])**2
        )
        features.append(shoulder_width)
    else:
        features.append(0.0)
    
    # Distância entre punhos (para poses com braços)
    if all(str(i) in landmarks_data for i in [15, 16]):  # Wrists
        left_wrist = landmarks_data['15']
        right_wrist = landmarks_data['16']
        wrist_distance = np.sqrt(
            (left_wrist['x'] - right_wrist['x'])**2 +
            (left_wrist['y'] - right_wrist['y'])**2
        )
        features.append(wrist_distance)
    else:
        features.append(0.0)
    
    # Features: altura relativa de cotovelos e ombros
    if all(str(i) in landmarks_data for i in [11, 13]):  # Left shoulder, elbow
        features.append(landmarks_data['13']['y'] - landmarks_data['11']['y'])
    else:
        features.append(0.0)
    
    if all(str(i) in landmarks_data for i in [12, 14]):  # Right shoulder, elbow
        features.append(landmarks_data['14']['y'] - landmarks_data['12']['y'])
    else:
        features.append(0.0)
    
    return np.array(features)


def prepare_training_data(data, pose_mode_filter=None):
    """
    Prepara dados para treinamento
    
    Args:
        data: Lista de amostras carregadas
        pose_mode_filter: Se especificado, treina apenas para essa pose (None = treina modelo geral)
    """
    X = []  # Features
    y = []  # Labels (0 = incorrect, 1 = correct)
    pose_modes = []  # Para treinamento por pose
    
    print("🔄 Processando dados...")
    
    for sample in data:
        # Filtra por pose se especificado
        if pose_mode_filter and sample['pose_mode'] != pose_mode_filter:
            continue
        
        # Extrai features
        features = extract_features(sample.get('landmarks'))
        if features is None or len(features) == 0:
            continue
        
        X.append(features)
        
        # Converte label para binário
        label = 1 if sample['label'] == 'correct' else 0
        y.append(label)
        pose_modes.append(sample['pose_mode'])
    
    if len(X) == 0:
        print("❌ Nenhuma feature válida extraída!")
        return None, None, None
    
    X = np.array(X)
    y = np.array(y)
    
    print(f"✅ {len(X)} amostras processadas")
    print(f"   - Correct: {np.sum(y == 1)}")
    print(f"   - Incorrect: {np.sum(y == 0)}")
    
    return X, y, pose_modes


def train_model(X, y, model_type='random_forest', save_path='pose_classifier.pkl'):
    """
    Treina modelo de classificação
    
    Args:
        X: Features
        y: Labels
        model_type: Tipo de modelo ('random_forest', 'svm', 'neural_network')
        save_path: Onde salvar o modelo treinado
    """
    print("\n🎓 Iniciando treinamento...")
    
    # Divide em treino e teste
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"📚 Dados de treino: {len(X_train)} amostras")
    print(f"📝 Dados de teste: {len(X_test)} amostras")
    
    # Treina modelo
    if model_type == 'random_forest':
        print("🌲 Treinando Random Forest...")
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=20,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
    else:
        raise ValueError(f"Modelo {model_type} não implementado ainda")
    
    # Treina
    model.fit(X_train, y_train)
    
    # Avalia
    y_train_pred = model.predict(X_train)
    y_test_pred = model.predict(X_test)
    
    train_acc = accuracy_score(y_train, y_train_pred)
    test_acc = accuracy_score(y_test, y_test_pred)
    
    print(f"\n📊 Resultados do Treinamento:")
    print(f"   Acurácia no Treino: {train_acc:.2%}")
    print(f"   Acurácia no Teste: {test_acc:.2%}")
    
    # Relatório detalhado
    print(f"\n📋 Relatório de Classificação (Teste):")
    print(classification_report(y_test, y_test_pred, 
                                target_names=['Incorrect', 'Correct']))
    
    # Matriz de confusão
    print(f"\n🔢 Matriz de Confusão:")
    cm = confusion_matrix(y_test, y_test_pred)
    print(f"                    Predito")
    print(f"                  Incorrect  Correct")
    print(f"Real Incorrect    {cm[0][0]:8d}  {cm[0][1]:7d}")
    print(f"     Correct      {cm[1][0]:8d}  {cm[1][1]:7d}")
    
    # Salva modelo (cria diretório models/ na raiz do projeto)
    models_dir = Path(__file__).parent.parent / "models"
    models_dir.mkdir(exist_ok=True)
    save_path_full = models_dir / Path(save_path).name
    joblib.dump(model, save_path_full)
    print(f"\n💾 Modelo salvo em: {save_path_full}")
    
    return model, test_acc


def train_per_pose(data):
    """Treina um modelo separado para cada tipo de pose"""
    pose_modes = set(sample['pose_mode'] for sample in data)
    print(f"\n🎯 Treinando modelos individuais para cada pose: {pose_modes}")
    
    models = {}
    accuracies = {}
    
    for pose_mode in pose_modes:
        print(f"\n{'='*60}")
        print(f"📌 Treinando modelo para: {pose_mode}")
        print(f"{'='*60}")
        
        X, y, _ = prepare_training_data(data, pose_mode_filter=pose_mode)
        
        if X is None or len(X) < 10:
            print(f"⚠️ Poucos dados para {pose_mode}, pulando...")
            continue
        
        save_path = f"pose_classifier_{pose_mode}.pkl"
        model, acc = train_model(X, y, save_path=save_path)
        models[pose_mode] = model
        accuracies[pose_mode] = acc
    
    return models, accuracies


def main():
    """Função principal"""
    print("="*60)
    print("🎓 Treinamento de Modelo de ML para Avaliação de Poses")
    print("="*60)
    
    # Carrega dados
    data = load_training_data()
    if data is None:
        return
    
    # Pergunta tipo de treinamento
    print("\n📋 Escolha o tipo de treinamento:")
    print("1. Modelo Geral (todas as poses juntas)")
    print("2. Modelos Individuais (um modelo por pose)")
    print("3. Ambos")
    
    choice = input("\nEscolha (1/2/3): ").strip()
    
    if choice in ['1', '3']:
        # Treina modelo geral
        print(f"\n{'='*60}")
        print("🌍 Treinando Modelo Geral")
        print(f"{'='*60}")
        
        X, y, _ = prepare_training_data(data)
        if X is not None:
            train_model(X, y, save_path='pose_classifier_general.pkl')
    
    if choice in ['2', '3']:
        # Treina modelos por pose
        train_per_pose(data)
    
    print("\n✅ Treinamento concluído!")
    print("\n💡 Próximos passos:")
    print("   1. Os modelos estão salvos em models/")
    print("   2. O BodyVision usará automaticamente os modelos treinados")
    print("   3. Rode: python BodyVision.py para usar com ML")


if __name__ == "__main__":
    main()

