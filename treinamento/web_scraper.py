"""
Script para coletar dados de treinamento de artigos web e imagens/vídeos
Extrai informações sobre poses corretas e incorretas de fontes online
"""
import requests
from bs4 import BeautifulSoup
import json
import re
from pathlib import Path
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
import time


class WebScraper:
    """Coleta informações sobre poses de fisiculturismo de artigos web"""
    
    def __init__(self, output_dir="data_collected/web"):
        """
        Inicializa o scraper
        
        Args:
            output_dir: Diretório onde salvar dados coletados
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def scrape_article(self, url: str) -> Optional[Dict]:
        """
        Faz scraping de um artigo sobre poses
        
        Args:
            url: URL do artigo
            
        Returns:
            Dict com conteúdo extraído ou None se falhar
        """
        try:
            print(f"📄 Coletando: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extrai título
            title = soup.find('title')
            title_text = title.get_text(strip=True) if title else ""
            
            # Extrai conteúdo principal
            # Tenta encontrar artigo principal (varia por site)
            article = soup.find('article') or soup.find('main') or soup.find('div', class_=re.compile('content|article|post'))
            if not article:
                article = soup.find('body')
            
            # Remove scripts e styles
            for script in article.find_all(['script', 'style']):
                script.decompose()
            
            # Extrai texto
            text = article.get_text(separator='\n', strip=True) if article else ""
            
            # Extrai imagens
            images = []
            for img in soup.find_all('img'):
                src = img.get('src') or img.get('data-src')
                if src:
                    full_url = urljoin(url, src)
                    images.append({
                        'url': full_url,
                        'alt': img.get('alt', ''),
                        'title': img.get('title', '')
                    })
            
            # Extrai vídeos
            videos = []
            for video in soup.find_all('video'):
                src = video.get('src')
                if src:
                    full_url = urljoin(url, src)
                    videos.append({'url': full_url})
            
            # Procura por menções de poses específicas
            pose_keywords = {
                'double_biceps': ['double biceps', 'duplo bíceps', 'front double biceps'],
                'side_chest': ['side chest', 'peito lateral', 'lateral chest'],
                'side_triceps': ['side triceps', 'tríceps lateral', 'lateral triceps'],
                'most_muscular': ['most muscular', 'mais muscular', 'crab most muscular'],
                'enquadramento': ['framing', 'enquadramento', 'centering']
            }
            
            detected_poses = []
            text_lower = text.lower()
            for pose, keywords in pose_keywords.items():
                for keyword in keywords:
                    if keyword in text_lower:
                        detected_poses.append(pose)
                        break
            
            result = {
                'url': url,
                'title': title_text,
                'text': text[:5000],  # Limita tamanho
                'images': images[:20],  # Limita quantidade
                'videos': videos[:10],
                'detected_poses': list(set(detected_poses)),
                'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            print(f"✅ Coletado: {len(images)} imagens, {len(videos)} vídeos")
            return result
            
        except Exception as e:
            print(f"❌ Erro ao coletar {url}: {e}")
            return None
    
    def download_image(self, url: str, save_path: Path) -> bool:
        """
        Baixa uma imagem
        
        Args:
            url: URL da imagem
            save_path: Onde salvar
            
        Returns:
            True se sucesso
        """
        try:
            response = self.session.get(url, timeout=10, stream=True)
            response.raise_for_status()
            
            # Verifica se é imagem
            content_type = response.headers.get('content-type', '')
            if not content_type.startswith('image/'):
                return False
            
            save_path.parent.mkdir(parents=True, exist_ok=True)
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return True
        except Exception as e:
            print(f"⚠️ Erro ao baixar {url}: {e}")
            return False
    
    def scrape_multiple(self, urls: List[str], download_images: bool = True) -> List[Dict]:
        """
        Faz scraping de múltiplos artigos
        
        Args:
            urls: Lista de URLs
            download_images: Se True, baixa imagens também
            
        Returns:
            Lista de resultados
        """
        results = []
        images_dir = self.output_dir / "images"
        
        for i, url in enumerate(urls, 1):
            print(f"\n[{i}/{len(urls)}] Processando...")
            result = self.scrape_article(url)
            
            if result:
                results.append(result)
                
                # Baixa imagens se solicitado
                if download_images and result['images']:
                    for j, img_info in enumerate(result['images'][:5]):  # Limita a 5 por artigo
                        img_url = img_info['url']
                        # Tenta inferir extensão
                        ext = Path(urlparse(img_url).path).suffix or '.jpg'
                        if ext not in ['.jpg', '.jpeg', '.png', '.webp']:
                            ext = '.jpg'
                        
                        img_filename = f"article_{i}_img_{j}{ext}"
                        img_path = images_dir / img_filename
                        
                        if self.download_image(img_url, img_path):
                            result['images'][j]['local_path'] = str(img_path)
                        
                        time.sleep(0.5)  # Evita sobrecarga
                
                time.sleep(1)  # Delay entre requisições
        
        # Salva resultados consolidados
        output_file = self.output_dir / "scraped_articles.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Coletados {len(results)} artigos")
        print(f"💾 Salvo em: {output_file}")
        
        return results


def main():
    """Função principal"""
    print("="*60)
    print("🌐 Coletor de Dados Web para Treinamento")
    print("="*60)
    
    # URLs conhecidas sobre poses de fisiculturismo
    known_urls = [
        "https://barbend.com/news/bodybuilding-poses/",
        # Adicione mais URLs aqui
    ]
    
    print("\n📋 URLs para coletar:")
    for url in known_urls:
        print(f"  - {url}")
    
    # Pergunta URLs adicionais
    print("\n💡 Deseja adicionar mais URLs? (s/n)")
    choice = input().strip().lower()
    
    urls = known_urls.copy()
    if choice == 's':
        print("Digite URLs (uma por linha, Enter vazio para terminar):")
        while True:
            url = input().strip()
            if not url:
                break
            if url.startswith('http'):
                urls.append(url)
            else:
                print("⚠️ URL inválida, ignorando...")
    
    # Pergunta se baixa imagens
    print("\n📥 Deseja baixar imagens dos artigos? (s/n)")
    download_imgs = input().strip().lower() == 's'
    
    # Executa scraping
    scraper = WebScraper()
    results = scraper.scrape_multiple(urls, download_images=download_imgs)
    
    print(f"\n✅ Concluído! {len(results)} artigos coletados")
    print(f"📁 Dados salvos em: {scraper.output_dir}")


if __name__ == "__main__":
    main()
