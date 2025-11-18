# coding=utf-8
import feedparser
import time
from datetime import datetime
from typing import Dict, List, Optional
import requests
import pytz


class RSSFeedCrawler:
    """Rastreador de feeds RSS para fuentes de noticias europeas"""
    
    def __init__(self, proxy_url: Optional[str] = None):
        self.proxy_url = proxy_url
        
    def fetch_rss_feed(self, feed_config: Dict) -> Dict:
        """Obtener datos de un feed RSS"""
        feed_id = feed_config.get('id', '')
        feed_name = feed_config.get('name', feed_id)
        feed_url = feed_config.get('url', '')
        
        if not feed_url:
            print(f"Error: No se especificó URL para el feed {feed_id}")
            return {}
            
        try:
            print(f"Obteniendo feed RSS: {feed_name} ({feed_url})")
            
            # Configurar headers para simular navegador
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/rss+xml, application/xml, text/xml, */*'
            }
            
            proxies = None
            if self.proxy_url:
                proxies = {'http': self.proxy_url, 'https': self.proxy_url}
            
            # Descargar el feed
            response = requests.get(feed_url, headers=headers, proxies=proxies, timeout=15)
            response.raise_for_status()
            
            # Parsear el feed con feedparser
            feed = feedparser.parse(response.content)
            
            if feed.bozo:
                print(f"Advertencia: Feed RSS mal formado para {feed_name}")
            
            # Extraer artículos
            result = {}
            for index, entry in enumerate(feed.entries[:50], 1):  # Limitar a 50 artículos
                title = entry.get('title', '').strip()
                link = entry.get('link', '')
                
                if not title:
                    continue
                    
                # Limpiar título
                title = title.replace('\n', ' ').replace('\r', ' ')
                title = ' '.join(title.split())
                
                # Agregar al resultado con estructura compatible
                if title not in result:
                    result[title] = {
                        'ranks': [index],
                        'url': link,
                        'mobileUrl': link  # RSS no diferencia entre móvil/desktop
                    }
                else:
                    result[title]['ranks'].append(index)
            
            print(f"Feed {feed_name}: {len(result)} artículos obtenidos")
            return result
            
        except requests.RequestException as e:
            print(f"Error al obtener feed {feed_name}: {e}")
            return {}
        except Exception as e:
            print(f"Error al procesar feed {feed_name}: {e}")
            return {}
    
    def crawl_rss_feeds(self, feed_configs: List[Dict], request_interval: int = 500) -> tuple:
        """Rastrear múltiples feeds RSS"""
        results = {}
        id_to_name = {}
        failed_ids = []
        
        for i, feed_config in enumerate(feed_configs):
            feed_id = feed_config.get('id', f'rss_{i}')
            feed_name = feed_config.get('name', feed_id)
            
            id_to_name[feed_id] = feed_name
            
            feed_result = self.fetch_rss_feed(feed_config)
            
            if feed_result:
                results[feed_id] = feed_result
            else:
                failed_ids.append(feed_id)
            
            # Intervalo entre peticiones
            if i < len(feed_configs) - 1:
                time.sleep(request_interval / 1000)
        
        print(f"RSS: Exitosos: {list(results.keys())}, Fallidos: {failed_ids}")
        return results, id_to_name, failed_ids
