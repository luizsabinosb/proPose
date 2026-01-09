"""
Módulo responsável pela detecção e avaliação de poses de fisiculturismo
"""
import cv2
import mediapipe as mp
import math


class PoseDetector:
    def __init__(self, static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5):
        """Inicializa os módulos do MediaPipe Pose"""
        self.mp_pose = mp.solutions.pose
        # Usa model_complexity=1 (modelo já instalado, evita download)
        # smooth_landmarks=True para suavização (melhor UX)
        self.pose = self.mp_pose.Pose(
            static_image_mode=static_image_mode,
            model_complexity=1,  # 1 = médio (modelo já instalado), evita erro de SSL
            smooth_landmarks=True,
            enable_segmentation=False,  # Desabilita segmentação para melhor performance
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        self.mp_drawing = mp.solutions.drawing_utils

    @staticmethod
    def calculate_angle(a: list[float], b: list[float], c: list[float]) -> float:
        """Calcula o ângulo formado entre três pontos (por exemplo: ombro, cotovelo e pulso)"""
        ba = [a[0] - b[0], a[1] - b[1]]
        bc = [c[0] - b[0], c[1] - b[1]]
        dot_product = ba[0] * bc[0] + ba[1] * bc[1]
        magnitude_ba = math.sqrt(ba[0]**2 + ba[1]**2)
        magnitude_bc = math.sqrt(bc[0]**2 + bc[1]**2)
        if magnitude_ba == 0 or magnitude_bc == 0:
            return 0
        
        # Normaliza o valor para evitar erro de domínio em math.acos
        cos_angle = dot_product / (magnitude_ba * magnitude_bc)
        cos_angle = max(-1.0, min(1.0, cos_angle))  # Limita entre -1 e 1
        
        angle_radians = math.acos(cos_angle)
        return math.degrees(angle_radians)

    @staticmethod
    def evaluate_double_biceps(left_angle, right_angle, left_elbow_height, right_elbow_height, 
                               left_shoulder_height, right_shoulder_height):
        """
        Avalia a postura 'duplo bíceps' (front double biceps)
        
        Baseado nas práticas profissionais de bodybuilding, esta pose:
        - É uma das poses obrigatórias mais clássicas
        - Enfatiza o desenvolvimento dos bíceps, deltoides e tríceps
        - Cotovelos devem estar elevados acima ou na altura dos ombros
        - Braços contraídos em um ângulo de 30-80 graus para mostrar pico do bíceps
        - Competidor deve mostrar simetria entre ambos os lados
        """
        errors = []
        if left_elbow_height > left_shoulder_height:
            errors.append("Cotovelo esquerdo muito baixo - eleve acima ou na altura do ombro")
        if right_elbow_height > right_shoulder_height:
            errors.append("Cotovelo direito muito baixo - eleve acima ou na altura do ombro")
        if not 30 <= left_angle <= 80:
            errors.append(f"Angulo do braco esquerdo fora do intervalo (30-80 graus, atual: {left_angle:.0f}°)")
        if not 30 <= right_angle <= 80:
            errors.append(f"Angulo do braco direito fora do intervalo (30-80 graus, atual: {right_angle:.0f}°)")
        if errors:
            return "Posicao incorreta:\n• " + "\n• ".join(errors)
        return "Posicao correta - Excelente duplo bíceps! Bíceps bem definidos e simétricos."

    @staticmethod
    def evaluate_centered(shoulder_left_x, shoulder_right_x, width):
        """Verifica se o usuário está centralizado horizontalmente na imagem"""
        center_x = width // 2
        body_center_x = (shoulder_left_x + shoulder_right_x) // 2
        offset = abs(center_x - body_center_x)
        threshold = width * 0.1
        if offset < threshold:
            return "Usuario bem centralizado na imagem."
        else:
            return "Centralize-se melhor na camera para avaliacao precisa."

    @staticmethod
    def evaluate_side_triceps(posterior_arm_angle, posterior_elbow_height, posterior_shoulder_height,
                              posterior_wrist_height, hip_rotation, front_knee_angle, front_arm_angle, knee_visible=True):
        """
        Avalia a postura 'side triceps' (tríceps lateral)
        
        Baseado nas métricas profissionais de bodybuilding:
        - Tronco rotacionado ~85-90° em relação ao árbitro
        - Braço posterior (visível): cotovelo totalmente estendido (~160-180° - intervalo tolerante)
        - Braço frontal: pode estar flexionado (segurando o punho do posterior) - apenas se visível
        - Pé frontal: joelho estendido (~180°) - apenas se visível
        - Contração máxima de tríceps, deltoide posterior e grande dorsal
        """
        errors = []
        
        # Métrica principal: braço posterior deve estar estendido (intervalo mais tolerante: 140-180°)
        # Ampliado para ser mais tolerante e evitar falsos negativos
        if not 120 <= posterior_arm_angle <= 180:
            if posterior_arm_angle < 120:
                errors.append(f"Braco posterior deve estar estendido (~120-180°) (atual: {posterior_arm_angle:.0f}°)")
        
        # Cotovelo posterior deve estar ABAIXO do ombro (valores maiores de Y = abaixo na imagem)
        # No Side Triceps, o cotovelo está naturalmente abaixo do ombro quando o braço está estendido para trás
        # Apenas validamos se o cotovelo estiver muito acima (o que seria incorreto)
        if posterior_elbow_height > 0 and posterior_shoulder_height > 0:
            elbow_shoulder_diff = posterior_elbow_height - posterior_shoulder_height
            # Se o cotovelo estiver muito acima do ombro (diferença negativa grande), é incorreto
            if elbow_shoulder_diff < -50:
                errors.append("Cotovelo posterior muito acima do ombro - abaixe para mostrar o triceps corretamente")
        
        # Verifica rotação do tronco (~85-90°)
        # hip_rotation em pixels - idealmente > 10 pixels indica boa rotação
        if hip_rotation > 0 and hip_rotation < 10:
            errors.append("Gire o tronco para o lado (~85-90°) para melhor visualizacao do triceps")
        
        # Pé frontal: joelho estendido (~180°) - APENAS se visível
        if knee_visible and front_knee_angle > 0:
            if not 170 <= front_knee_angle <= 180:
                errors.append(f"Joelho da perna frontal deve estar estendido (~180°) (atual: {front_knee_angle:.0f}°)")
        
        # Braço frontal - apenas valida se estiver visível (front_arm_angle > 0)
        # Não valida se não estiver visível na câmera
        
        if errors:
            return "Posicao incorreta:\n• " + "\n• ".join(errors)
        return "Posicao correta - Excelente side triceps! Triceps bem estendido e destacado."

    @staticmethod
    def evaluate_side_chest(visible_arm_angle, visible_elbow_height, visible_shoulder_height, 
                            hip_rotation, visible_knee_angle, opposite_arm_angle, knee_visible=True):
        """
        Avalia a postura 'side chest' (peito lateral)
        
        Baseado nas métricas profissionais de bodybuilding:
        - Tronco aberto ao árbitro (~80-85°)
        - Braço frontal: cotovelo flexionado (~80-120° - intervalo mais tolerante)
        - Perna frontal: joelho levemente flexionado (~165-170°) - apenas se visível
        - Compressão ativa do peitoral maior
        """
        errors = []
        
        # Métrica principal: braço frontal deve estar contraído (intervalo mais tolerante: 70-130°)
        # Ampliado para ser mais tolerante e evitar falsos negativos
        if not 70 <= visible_arm_angle <= 130:
            errors.append(f"Braco frontal deve estar contraido entre 70-130° (atual: {visible_arm_angle:.0f}°)")
        
        # Verifica rotação do tronco (~80-85°)
        # hip_rotation em pixels - idealmente > 15 pixels indica boa rotação
        if hip_rotation > 0 and hip_rotation < 10:
            errors.append("Gire o tronco para o lado (~80-85°) para melhor visualizacao do peito")
        
        # Cotovelo deve estar abaixo do ombro (valores maiores de Y = abaixo na imagem)
        # No Side Chest, o cotovelo está naturalmente abaixo do ombro, então não validamos isso
        # Apenas verificamos se não está muito acima (o que seria incorreto)
        if visible_elbow_height > 0 and visible_shoulder_height > 0:
            elbow_shoulder_diff = visible_elbow_height - visible_shoulder_height
            # Se o cotovelo estiver muito acima do ombro (diferença negativa grande), é incorreto
            if elbow_shoulder_diff < -30:
                errors.append("Cotovelo muito acima do ombro - abaixe para mostrar o peito")
        
        # Perna frontal: joelho levemente flexionado (~165-170°) - APENAS se visível
        if knee_visible and visible_knee_angle > 0:
            if not 160 <= visible_knee_angle <= 175:
                if visible_knee_angle < 160:
                    errors.append(f"Joelho muito flexionado - estenda ligeiramente para ~165-170° (atual: {visible_knee_angle:.0f}°)")
                elif visible_knee_angle > 175:
                    errors.append(f"Joelho muito estendido - flexione ligeiramente para ~165-170° (atual: {visible_knee_angle:.0f}°)")
        
        # Braço posterior deve estar flexionado (ajudando a comprimir o peitoral) - apenas se visível
        # Se opposite_arm_angle for 0, significa que o braço não está visível, então não valida
        if opposite_arm_angle > 0 and opposite_arm_angle > 160:
            errors.append("Mantenha o braco posterior flexionado para comprimir o peitoral")
        
        if errors:
            return "Posicao incorreta:\n• " + "\n• ".join(errors)
        return "Posicao correta - Excelente side chest! Peito bem projetado e compressao ativa do peitoral."

    @staticmethod
    def evaluate_most_muscular(left_arm_angle, right_arm_angle, left_elbow_height, right_elbow_height,
                               left_shoulder_height, right_shoulder_height, shoulder_width, 
                               left_knee_angle, right_knee_angle, torso_alignment,
                               left_wrist_x, right_wrist_x, left_shoulder_x, right_shoulder_x):
        """
        Avalia a postura 'most muscular' (mais muscular)
        
        Baseado nas práticas profissionais de bodybuilding, esta pose:
        - Não é obrigatória em todas as federações, mas comum em competições
        - Última chance para o competidor mostrar toda a musculatura de uma vez
        - Alguns inclinam para frente com punhos virados para a plateia
        - Outros ficam mais eretos com as mãos entrelaçadas na frente da cintura
        - Cotovelos devem estar abaixo dos ombros
        - Braços contraídos um contra o outro, aproximando as mãos
        """
        errors = []
        
        # Métrica principal: cotovelos devem estar ABAIXO dos ombros
        if left_elbow_height <= left_shoulder_height + 10:
            errors.append("Cotovelo esquerdo deve estar abaixo do ombro")
        if right_elbow_height <= right_shoulder_height + 10:
            errors.append("Cotovelo direito deve estar abaixo do ombro")
        
        # Métrica principal: braços devem estar contraídos um contra o outro
        wrist_distance = abs(left_wrist_x - right_wrist_x)
        shoulder_width_actual = abs(right_shoulder_x - left_shoulder_x)
        
        # Os punhos devem estar próximos (máximo 50% da largura dos ombros)
        if shoulder_width_actual > 0 and wrist_distance > shoulder_width_actual * 0.5:
            errors.append("Aproxime as maos - bracos devem estar contraidos um contra o outro")
        
        # Verifica alinhamento do torso
        if torso_alignment > 30:
            errors.append("Mantenha o torso alinhado para mostrar simetria")
        
        # Joelhos devem estar estendidos ou ligeiramente flexionados
        if left_knee_angle < 160:
            errors.append(f"Estenda mais a perna esquerda (atual: {left_knee_angle:.0f}°)")
        if right_knee_angle < 160:
            errors.append(f"Estenda mais a perna direita (atual: {right_knee_angle:.0f}°)")
        
        if errors:
            return "Posicao incorreta:\n• " + "\n• ".join(errors)
        return "Posicao correta - Excelente most muscular! Toda a musculatura bem destacada."

