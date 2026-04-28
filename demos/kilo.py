#!/usr/bin/env python3
"""Compact Kilo Gateway inference client — streaming chat via OpenRouter-compatible API."""

import argparse, asyncio, json, os, time
import httpx
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text

BASE = os.environ.get("KILO_API_URL", "https://api.kilo.ai")
URL = f"{BASE}/api/openrouter/v1/chat/completions"
KEY = os.environ.get("KILO_API_KEY", "anonymous")
MODEL = "kilo-auto/free" if KEY == "anonymous" else "kilo-auto/balanced"
console = Console()


def headers(key):
    return {"Content-Type": "application/json", "Authorization": f"Bearer {key}",
            "User-Agent": "opencode-kilo-provider", "X-KILOCODE-EDITORNAME": "Kilo CLI"}


async def stream(messages, model, key, temp=0.7, max_tok=None):
    """Yield text chunks from a streaming chat completion."""
    body = {"model": model, "messages": messages, "temperature": temp, "stream": True}
    if max_tok is not None:
        body["max_tokens"] = max_tok
    async with httpx.AsyncClient(headers=headers(key), timeout=120) as c:
        async with c.stream("POST", URL, json=body) as r:
            if r.status_code != 200:
                raise Exception(f"[{r.status_code}] {(await r.aread()).decode()}")
            async for line in r.aiter_lines():
                if not line.startswith("data:"):
                    continue
                data = line[5:].strip()
                if data == "[DONE]":
                    return
                try:
                    yield json.loads(data)["choices"][0]["delta"].get("content", "")
                except (json.JSONDecodeError, KeyError, IndexError):
                    pass


async def infer(prompt, system=None, model=MODEL, key=KEY, temp=0.7):
    """One-shot streaming inference — prints and returns full text."""
    msgs = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": prompt}]
    parts, t0 = [], time.perf_counter()
    with Live(Text("▍", style="green"), console=console, refresh_per_second=12, transient=True) as live:
        async for chunk in stream(msgs, model, key, temp):
            if chunk:
                parts.append(chunk)
                live.update(Markdown("".join(parts) + "▍"))
    text = "".join(parts)
    console.print(Panel(Markdown(text), title="[bold green]Assistant[/]",
                        subtitle=f"[dim]{time.perf_counter()-t0:.1f}s · {model}[/]", border_style="green"))
    return text


async def chat(system=None, model=MODEL, key=KEY):
    """Interactive multi-turn chat loop."""
    console.print(Panel.fit("[bold magenta]⚡ Kilo Gateway[/]\n[dim]Type /exit to quit, /clear to reset[/]",
                            border_style="magenta"))
    console.print(f"  [dim]Model:[/] [bold magenta]{model}[/]  [dim]Auth:[/] {'🔑' if key != 'anonymous' else '🆓'}\n")
    hist = ([{"role": "system", "content": system}] if system else [])
    while True:
        try:
            user = console.input("[bold cyan]You ▸ [/]").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not user:
            continue
        if user.startswith("/"):
            cmd = user.split()[0].lower()
            if cmd in ("/exit", "/quit", "/q"):
                break
            if cmd == "/clear":
                hist = ([{"role": "system", "content": system}] if system else [])
                console.print("[cyan]Cleared.[/]\n"); continue
            if cmd == "/model":
                p = user.split(maxsplit=1)
                if len(p) > 1:
                    model = p[1].strip()
                console.print(f"  [magenta]{model}[/]\n"); continue
            console.print(f"[yellow]Unknown: {cmd}[/]\n"); continue
        hist.append({"role": "user", "content": user})
        parts, t0 = [], time.perf_counter()
        console.print()
        try:
            with Live(Text("▍", style="green"), console=console, refresh_per_second=12, transient=True) as live:
                async for chunk in stream(hist, model, key):
                    if chunk:
                        parts.append(chunk)
                        live.update(Markdown("".join(parts) + "▍"))
            text = "".join(parts)
            console.print(Panel(Markdown(text), title="[bold green]Assistant[/]",
                                subtitle=f"[dim]{time.perf_counter()-t0:.1f}s[/]", border_style="green"))
            console.print()
            hist.append({"role": "assistant", "content": text})
        except Exception as e:
            console.print(f"[red]{e}[/]\n"); hist.pop()
    console.print("[dim]Bye![/]")


def main():
    p = argparse.ArgumentParser(prog="kilo-infer", description="Kilo Gateway inference")
    p.add_argument("-p", "--prompt", help="One-shot prompt")
    p.add_argument("-m", "--model", default=MODEL)
    p.add_argument("-s", "--system", default=None)
    p.add_argument("-k", "--api-key", default=KEY)
    p.add_argument("-t", "--temperature", type=float, default=0.7)
    a = p.parse_args()
    if a.prompt:
        asyncio.run(infer(a.prompt, a.system, a.model, a.api_key, a.temperature))
    else:
        asyncio.run(chat(a.system, a.model, a.api_key))


if __name__ == "__main__":
    main()
