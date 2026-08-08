---
title: "{{ replace .File.ContentBaseName `-` ` ` | title }}"
date: {{ .Date }}
lastmod: {{ .Date }}
draft: true
format: thought
comments: true
comment_id: "{{ .File.ContentBaseName }}"
tags: []
---

Write the complete thought here. Thoughts are shown in full in post lists.
