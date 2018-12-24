;@echo off
if exist .\addon\buildVars.py (
	copy .\addon\buildVars.py .
	)
if exist .\addon\doc\en\readme.md (
	copy .\addon\doc\en\readme.md .
	if exist .\addon\doc\style_md.css (
		copy .\addon\doc\style_md.css .
	)
)
