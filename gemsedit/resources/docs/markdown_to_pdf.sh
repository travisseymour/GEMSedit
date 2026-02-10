# You might need to install pandoc and weasyprint

pandoc gems_overview.md -o gems_overview.pdf \
  --from=gfm \
  --toc --toc-depth=6 \
  -V toc-title="GEMS Overview - Table of Contents" \
  --pdf-engine=weasyprint \
  --css github.css

pandoc GEMS_Action_Reference.md -o GEMS_Action_Reference.pdf \
  --from=gfm \
  --toc --toc-depth=4 \
  -V toc-title="GEMS Action Reference - Table of Contents" \
  --pdf-engine=weasyprint \
  --css github.css