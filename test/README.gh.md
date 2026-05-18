<center>
  <h1 align="center">GH-MD</h1>
  <center>
    <badge ltext="github action" rtext="compiles markdown" style="for-the-badge" logo="githubactions" logoColor="white" labelColor="black" color="rebeccapurple" href="https://github.com/uukelele/gh-md"/>   
  </center>
</center>

<hr>

## <font="mono">STUFF</font>

<font="double">Many custom fonts are supported!</font>
<font="Funky">They also work well with screen-readers.</font>

# <font="mono">PROJECTS</font>

<projects user="vercel" limit="3" sort="stars">
  <template>
    <h3 title="{{ project.description }}">
      {{ project.name }}
      •
      ⭐ {{ project.stargazers_count }} • 🍴 {{ project.forks_count }}
      •
      <a href="{{ project.html_url }}"><kbd>GitHub</kbd></a>
    </h3>
  </template>
</projects>


# <font="mono">STATS</font>
<center>
  <stats user="uukelele" base-url="https://github-readme-stats-clone-wine.vercel.app" show-icons count-private theme="transparent" hide-border />
  <stats route = "/api/top-langs" user="uukelele" base-url="https://github-readme-stats-clone-wine.vercel.app" layout="compact" theme="transparent" hide-border />
</center>

<center>
  <devicon name="fastapi" height="40" type='original' />
    <img width="12" />
  <devicon name="svelte" height="40"/>
</center>

<hr>