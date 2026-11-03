# Mermaid e procedência

O Mermaid desenha os blocos cercados `mermaid` das páginas do portal, no navegador, offline e sem
CDN (R26 do programa Engenharia de IA). O arquivo é o build de navegador do pacote publicado, sem
alteração. O `.md` gêmeo, o `llms.txt` e o pacote continuam com o bloco como texto.

| Arquivo | Versão | SHA-256 |
|---|---|---|
| `mermaid.min.js` | 12.2.0 | `a8a6a6f805b074a8261a2825c86f99c8054acb3b35f50bb7e24a4f9f2c3c3b9f` |

Origem: pacote `mermaid@12.2.0` do registro npm (`dist/mermaid.min.js`), integridade do tarball
`sha512-w7nr/SFrLO7BaVTs3dQTvYSV6nYSBj0Yy9DjBhsIJtAcHqRzXSq4Pg32ujHZ/AdWsAMNEvvhbm5dt9E2tOiHzw==`.
Repositório: https://github.com/mermaid-js/mermaid. Licença MIT, texto em `LICENSE.txt`.

A 12.2.0 foi publicada em 2026-10-13; a 12.3.0 saiu em 2026-11-03 e ainda não tem tempo de uso,
por isso não foi a escolhida. A inicialização está em `portal/tema/mermaid-init.js`
(`securityLevel: "strict"`).

## Como atualizar

1. `npm pack mermaid@<versão>` numa pasta vazia e extraia o tarball.
2. Copie `package/dist/mermaid.min.js` e `package/LICENSE` (como `LICENSE.txt`) para esta pasta.
3. Atualize versão, SHA-256 (`shasum -a 256 mermaid.min.js`) e integridade acima; o teste
   `tests/unidade/test_mermaid.py` confere o SHA-256.
4. Gere o site e abra uma página com diagrama para conferir.
