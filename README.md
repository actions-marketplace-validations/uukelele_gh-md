# gh-md
A preprocessor for GitHub README files that allows simple expressions converted into markdown that pops.

## Examples

### Center
```html
<center>
  <h1>My Title</h1>
</center>
```
Renders as centered content.

### Badge
```html
<badge ltext="build" rtext="passing" color="green" />
```
Creates a [shields.io](https://shields.io) badge. Supports `ltext`, `rtext`, `style`, `logo`, `logoColor`, `labelColor`, `color`, `link`, and `href` attributes.

### Font
```html
<font="mono">Monospace Text</font>
<font="double">Wide Text</font>
<font="Funky">Funky Text</font>
```
Applies ASCII art fonts to text. See [`gh_md/fonts.py`](gh_md/fonts.py) for all available fonts (60+ options).

### Projects
```html
<projects user="vercel" limit="3" sort="stars">
  <template>
    {{ project.name }} - ⭐ {{ project.stargazers_count }}
  </template>
</projects>
```
Fetches your GitHub repositories and renders them using a Jinja2 template. Requires `user` attribute. Optional: `limit` (default 3), `sort` (stars, updated, created).

### Stats
```html
<stats user="yourusername" show-icons count-private theme="transparent" hide-border />
```
Displays GitHub Readme Stats. Supports `user`, `show-icons`, `count-private`, `hide-border`, `layout`, `base-url`, `route`, and `theme` attributes.

### Devicon
```html
<devicon name="python" height="32" />
<devicon name="react" type="original" height="32" />
```
Inserts [devicon](https://devicon.dev) icons. Requires `name`. Optional: `type` (original, plain, line), `height`.