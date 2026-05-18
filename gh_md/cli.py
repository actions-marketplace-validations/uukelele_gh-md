import typer
from pathlib import Path

from .compiler import compile as cmp

app = typer.Typer()

@app.command()
def compile(input_path: Path, output: Path = 'README.md'):
    input_path = Path(input_path)
    output = Path(output)

    if not input_path.exists():
        raise typer.BadParameter(f"File {input_path} does not exist.")
    
    content = input_path.read_text()

    content = cmp(content)
    
    output.write_text(content)

if __name__ == "__main__":
    app()