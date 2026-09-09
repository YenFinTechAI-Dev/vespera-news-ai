"""Curated public feeds. Add sources here; never accept arbitrary URLs from visitors."""
SOURCES = [
    dict(id='sec', name='SEC · US', category='financial_crime', language='en', url='https://www.sec.gov/news/pressreleases.rss', hosts=['www.sec.gov','sec.gov']),
    dict(id='ftc', name='FTC · US', category='financial_crime', language='en', url='https://www.ftc.gov/feeds/press-release.xml', hosts=['www.ftc.gov','ftc.gov']),

    dict(id='vn-economy', name='VnExpress', category='economy', language='vi', url='https://vnexpress.net/rss/kinh-doanh.rss', hosts=['vnexpress.net']),
    dict(id='vn-tech', name='VnExpress', category='technology', language='vi', url='https://vnexpress.net/rss/so-hoa.rss', hosts=['vnexpress.net']),
    dict(id='kdnuggets', name='KDnuggets', category='ai', language='en', url='https://www.kdnuggets.com/feed', hosts=['www.kdnuggets.com', 'kdnuggets.com']),
    dict(id='medium-ai', name='Medium · AI', category='ai', language='en', url='https://medium.com/feed/tag/artificial-intelligence', hosts=['medium.com'], subdomains=True),
    dict(id='arxiv-ai', name='arXiv · cs.AI', category='research', language='en', url='https://rss.arxiv.org/rss/cs.AI', hosts=['arxiv.org']),
    dict(id='arxiv-ml', name='arXiv · cs.LG', category='research', language='en', url='https://rss.arxiv.org/rss/cs.LG', hosts=['arxiv.org']),
    dict(id='arxiv-cl', name='arXiv · cs.CL', category='research', language='en', url='https://rss.arxiv.org/rss/cs.CL', hosts=['arxiv.org']),
    dict(id='huggingface', name='Hugging Face', category='ai', language='en', url='https://huggingface.co/blog/feed.xml', hosts=['huggingface.co']),
    dict(id='openai', name='OpenAI', category='ai', language='en', url='https://openai.com/news/rss.xml', hosts=['openai.com']),
    dict(id='google-ai', name='Google AI', category='ai', language='en', url='https://blog.google/technology/ai/rss/', hosts=['blog.google']),
    dict(id='deepmind', name='Google DeepMind', category='ai', language='en', url='https://deepmind.google/blog/rss.xml', hosts=['deepmind.google']),
    dict(id='techcrunch-ai', name='TechCrunch · AI', category='technology', language='en', url='https://techcrunch.com/category/artificial-intelligence/feed/', hosts=['techcrunch.com']),
    dict(id='transformers', name='Transformers · Releases', category='tools', language='en', url='https://github.com/huggingface/transformers/releases.atom', hosts=['github.com']),
    dict(id='vllm', name='vLLM · Releases', category='tools', language='en', url='https://github.com/vllm-project/vllm/releases.atom', hosts=['github.com']),
    dict(id='ollama', name='Ollama · Releases', category='tools', language='en', url='https://github.com/ollama/ollama/releases.atom', hosts=['github.com']),
]

def public_sources():
    return [dict(id=s['id'], name=s['name'], category=s['category'], url=s['url'], configured=True) for s in SOURCES]
