# You might need to install pandoc and pdflatex

pandoc gems_overview.md -o gems_overview.pdf \
  --toc --toc-depth=6 \
  --pdf-engine=pdflatex \
  -V mainfont="Garmond" \
  -V geometry:margin=1in