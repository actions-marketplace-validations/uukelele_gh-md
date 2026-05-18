import os
import httpx
import urllib.parse

from lark import Lark, Transformer
from jinja2 import Template

from .fonts import fonts

FONTS = {f["fontName"]: f for f in fonts}

parser = Lark(r"""
start: nodes

?node: text | unparsed_tag | block_tag | inline_tag | font_tag | projects_tag

text: /[^<]+/
unparsed_tag: /<(?!\/?(center|badge|projects|template|stats|devicon)\b|font[="])[^>]*>/

nodes: node*
attrs: attr*

block_tag: "<" TAG_NAME attrs _WS? ">" nodes "</" TAG_NAME _WS? ">"
inline_tag: "<" TAG_NAME attrs _WS? "/>"

font_tag: "<font=" STRING ">" text "</font>"
projects_tag: "<projects" attrs _WS? ">" _WS? TEMPLATE_TAG _WS? "</projects>"

TEMPLATE_TAG: /<template>[\s\S]*?<\/template>/

attr: _WS? ATTR_NAME _WS? "=" _WS? STRING
    | _WS? ATTR_NAME

TAG_NAME: "center" | "badge" | "stats" | "devicon"
ATTR_NAME: /[a-zA-Z_][a-zA-Z0-9_-]*/
STRING: /"[^"]*"/ | /'[^']*'/

_WS: /[ \t\n\r]+/
""")

def apply_font(text: str, font_name: str) -> str:
    if font_name not in FONTS:
        # Just like a browser, we are trying to minimize errors here.
        # So just ignore things that don't work.
        return text
    
    font = FONTS[font_name]
    
    buf = ''
    for char in text:
        if 'a' <= char <= 'z':
            idx = ord(char) - ord('a')
            buf += font['fontLower'][idx] if idx < len(font['fontLower']) else char
        elif 'A' <= char <= 'Z':
            idx = ord(char) - ord('A')
            buf += font['fontUpper'][idx] if idx < len(font['fontUpper']) else char
        elif '0' <= char <= '9':
            idx = ord(char) - ord('0')
            buf += font['fontDigits'][idx] if idx < len(font['fontDigits']) else char
        else: buf += char

    # We want to make screen readers be able to read the text, and not read aloud the font-changed text.
    return f'<span aria-label="{text}"><span aria-hidden="true">{buf}</span></span>'

def fetch_projects(username: str, limit: int = 3, sort: str = 'stars') -> list[dict]:
    token = os.getenv('GITHUB_TOKEN')
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "uukelele/gh-md",
    }
    if token: headers["Authorization"] = f"Bearer {token}"

    try:
        r = httpx.get(
            "https://api.github.com/search/repositories",
            params = {
                'q': f'user:{username} fork:false',
                'sort': sort,
                'per_page': limit,
            },
            headers = headers,
        )
        r.raise_for_status()
        data = r.json()

        return data['items']
    except Exception as e:
        print(f"Error while fetching GitHub projects for {username}: {e}")
        return []
    


class Compiler(Transformer):
    def start(self, items): return items[0]
    
    def nodes(self, items): return ''.join(items)
    
    def attrs(self, items): return dict(items)

    def attr(self, items):
        if len(items) == 1:
            return (str(items[0]), True)
        key = str(items[0])
        value = str(items[-1])[1:-1]
        return (key, value)

    def ATTR_NAME(self, items):
        if isinstance(items, list):
            return str(items[0])
        return str(items)

    def STRING(self, items):
        if isinstance(items, list):
            return str(items[0])
        return str(items)

    def text(self, items): return str(items[0])

    def unparsed_tag(self, items): return str(items[0])

    def RAW_TEXT(self, items): return str(items[0])

    def block_tag(self, items):
        match str(items[0]):
            case 'center': return f'<div align="center">\n{items[2]}\n</div>'

            case _: return f'<{items[0]}>{items[2]}</{items[0]}>'
            
    def inline_tag(self, items):
        match str(items[0]):
            case 'badge':   return self.render_badge(items[1])
            case 'stats':   return self.render_stats(items[1])
            case 'devicon': return self.render_devicon(items[1])

            case _: return f'<{items[0]}/>'

    def font_tag(self, items): return apply_font(str(items[1]), str(items[0])[1:-1])

    def template_tag(self, items): return str(items[0])

    def projects_tag(self, items):
        attrs = items[0]
        template = str(items[1]).removeprefix('<template>').removesuffix('</template>')

        limit = int(attrs.get('limit', 3) if str(attrs.get('limit', 3)).isdigit() else 3)
        sort  = attrs.get('sort', 'stars')
        user  = attrs.get('user', os.getenv('GITHUB_USER'))

        projects = fetch_projects(user, limit, sort)

        t = Template(template)

        return '\n'.join([t.render(project=project) for project in projects])
    
    def render_badge(self, attrs):
        ltext = urllib.parse.quote(attrs.get("ltext", "").replace(" ", "_"))
        rtext = urllib.parse.quote(attrs.get("rtext", "").replace(" ", "_"))
        style = attrs.get("style", "for-the-badge")
        logo = attrs.get("logo", "")
        logoColor = attrs.get("logoColor", "white")
        labelColor = attrs.get("labelColor", "black")
        color = attrs.get("color", "rebeccapurple")
        link = attrs.get("link", attrs.get("href", ""))

        url = f"https://img.shields.io/badge/{ltext}-{rtext}-_?style={style}&logo={logo}&logoColor={logoColor}&labelColor={labelColor}&color={color}"
        tag = f'<img alt="Static Badge" src="{url}" />'

        return f'<a href="{link}">{tag}</a>' if link and link is not True else tag
    
    def render_stats(self, attrs):
        user = attrs.get('user', os.getenv('GITHUB_USER'))
        base_url = attrs.get('base-url', "https://github-readme-stats.vercel.app").removesuffix('/')
        route = attrs.get('route', '/api')

        params = {"username": user}
        if "show-icons" in attrs: params["show_icons"] = "true"
        if "count-private" in attrs: params["count_private"] = "true"
        if "hide-border" in attrs: params["hide_border"] = "true"
        if "layout" in attrs: params["layout"] = attrs["layout"]

        import copy
        dark_p = copy.deepcopy(params)
        dark_p['theme'] = attrs.get('theme', 'transparent')

        light_p = copy.deepcopy(params)
        light_p ['theme'] = 'default'

        dark_qs  = urllib.parse.urlencode(dark_p)
        light_qs = urllib.parse.urlencode(light_p)

        dark_url  = f"{base_url}{route}?{dark_qs}"
        light_url = f"{base_url}{route}?{light_qs}"

        return f'''
<picture>
    <source media="(prefers-color-scheme: dark)"  srcset="{dark_url}"  />
    <source media="(prefers-color-scheme: light)" srcset="{light_url}" />
    <img alt="GitHub Stats" src="{light_url}" />
</picture>
'''
    
    def render_devicon(self, attrs):
        name = attrs.get('name', 'github')
        type = attrs.get('type', 'original')
        height = attrs.get('height', 40)
        return f'<img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/{name}/{name}-{type}.svg" height="{height}" alt="Icon for {name}" />'


compiler = Compiler()

def compile(text: str) -> str:
    tree = parser.parse(text)

    return compiler.transform(tree)