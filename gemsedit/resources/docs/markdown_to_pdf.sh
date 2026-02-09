# You might need to install pandoc and weasyprint

pandoc gems_overview.md -o gems_overview.pdf \
  --from=gfm \
  --toc --toc-depth=6 \
  -V toc-title="GEMS Overview - Table of Contents" \
  --pdf-engine=weasyprint \
  --css github.css