
[app]
title = AI Architectural Analyzer
package.name = aiarchanalyzer
package.domain = com.aiarch.analyzer

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,txt

version = 1.0
requirements = python3,kivy,streamlit,plotly,pandas,numpy

[buildozer]
log_level = 2

[android]
api = 31
minapi = 21
ndk = 25b
accept_sdk_license = True
