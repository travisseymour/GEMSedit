Great question — Pandoc can absolutely turn your Markdown (with images and formatting) into a **beautiful PDF**, but there are a few moving parts depending on how fancy you want to get.

---

### ✅ **Basic conversion (images included)**

If you just want to go from `file.md` → `file.pdf` (with images from `./media`), run:

```bash
pandoc file.md -o file.pdf
```

As long as your Markdown links images like:
```markdown
![alt text](media/image1.png)
```
—they’ll be embedded in the PDF just fine.

---

### 🌟 **For a beautiful PDF**, here are your best enhancements:

#### 1. **Use a better PDF engine (recommended)**
Install **`xelatex`** or **`lualatex`** for better font and layout control:
```bash
# Debian/Ubuntu
sudo apt install texlive-xetex

# Fedora
sudo dnf install texlive-xetex

# macOS
brew install --cask mactex
```

Then run:
```bash
pandoc file.md -o file.pdf --pdf-engine=xelatex
```

---

#### 2. **Custom fonts**
Want a nice font like Garamond or Inter?
```bash
pandoc file.md -o file.pdf \
  --pdf-engine=xelatex \
  -V mainfont="Garamond"
```

You can replace `"Garamond"` with any installed system font (case-sensitive!).

---

#### 3. **Tweak page size, margins, etc.**
```bash
-V geometry:margin=1in
-V papersize:a4
```

Example:
```bash
pandoc file.md -o file.pdf \
  --pdf-engine=xelatex \
  -V mainfont="Garamond" \
  -V geometry:margin=1in \
  -V papersize=a4
```

---

#### 4. **Include a stylesheet (optional but powerful)**
You can make a custom Pandoc YAML or LaTeX template, but even simpler: just make a `metadata.yaml` file:

```yaml
title: "My Document"
author: "Drow Elf"
date: "`date +%Y-%m-%d`"
mainfont: "Garamond"
geometry: margin=1in
papersize: a4
```

Then run:
```bash
pandoc metadata.yaml file.md -o file.pdf --pdf-engine=xelatex
```

---

### 💡 Pro Tip: Use a table of contents
```bash
--toc --toc-depth=2
```

---

### 🧪 Final example:

```bash
pandoc file.md -o file.pdf \
  --pdf-engine=xelatex \
  --toc --toc-depth=2 \
  -V mainfont="Garamond" \
  -V geometry:margin=1in \
  -V papersize=a4
```

---

### Pandoc handles **syntax highlighting** beautifully for code blocks in Markdown-to-PDF conversion. 
You just need to tell it how to highlight and choose a theme.

---

### ✅ **Basic setup**

Use triple backticks in your Markdown with the language specified:

<pre>
```python
def greet(name):
    return f"Hello, {name}!"
```
</pre>

Then run Pandoc with:

```bash
pandoc file.md -o file.pdf --pdf-engine=xelatex --highlight-style tango
```

---

### 🎨 **Available highlight styles**

Here are some built-in styles you can try:

- `pygments` (default)
- `tango`
- `kate`
- `monochrome`
- `espresso`
- `zenburn`
- `haddock`
- `breezedark`

Example:
```bash
pandoc file.md -o file.pdf \
  --pdf-engine=xelatex \
  --highlight-style zenburn
```

---

### 🎛️ **Combine with a font and layout**

```bash
pandoc file.md -o file.pdf \
  --pdf-engine=xelatex \
  -V mainfont="Fira Code" \
  -V geometry:margin=1in \
  -V papersize:a4 \
  --highlight-style tango
```

> You can use a monospaced font like `Fira Code`, `Source Code Pro`, or `Courier New` for nice-looking code blocks.

---

### 💡 Want custom syntax highlighting?

You can create your own style:
```bash
pandoc --print-highlight-style=zenburn > my-style.theme
```

Edit `my-style.theme`, then use it:
```bash
pandoc file.md -o file.pdf --highlight-style=my-style.theme
```

---

Let me know if you want to include inline code color, fenced block styles, or support for dark backgrounds!
