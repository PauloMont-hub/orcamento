# Plafond — PWA

Controlo do orçamento mensal por ciclo de salário. Funciona offline, instala-se no ecrã principal do telemóvel e guarda os dados apenas no próprio dispositivo (sem contas nem servidor).

## Ficheiros

| Ficheiro | Para que serve |
|---|---|
| `index.html` | A app completa (HTML, CSS e JS num só ficheiro) |
| `manifest.webmanifest` | Nome, cores e ícones para instalar no ecrã principal |
| `sw.js` | Service worker: guarda a app em cache para abrir sem rede |
| `icons/` | Ícones 192, 512, maskable, Apple (180) e favicon |
| `.nojekyll` | Diz ao GitHub Pages para servir os ficheiros tal como estão |

Todos os caminhos são relativos, por isso a app funciona tanto em `utilizador.github.io/orcamento/` como num domínio próprio.

## Publicar no GitHub Pages

1. Cria um repositório **público** no GitHub, por exemplo `orcamento`.
2. Em **Add file → Upload files**, arrasta **o conteúdo** desta pasta (não a pasta em si). O `index.html` tem de ficar na raiz do repositório. O `.nojekyll` é um ficheiro oculto: no Mac, mostra-o no Finder com `Cmd + Shift + .` antes de arrastar.
3. Faz **Commit changes**.
4. Vai a **Settings → Pages**. Em *Source* escolhe **Deploy from a branch**, branch `main`, pasta `/ (root)`, e guarda.
5. Ao fim de 1 ou 2 minutos, a app fica em `https://<utilizador>.github.io/orcamento/`.

### Domínio próprio (opcional)
Em **Settings → Pages → Custom domain** escreve, por exemplo, `plafond.montstudio.pt`. No DNS do domínio cria um registo `CNAME` de `plafond` para `<utilizador>.github.io`. Quando o certificado estiver pronto, ativa **Enforce HTTPS**.

## Instalar no iPhone

1. Abre o endereço no **Safari**.
2. Toca em **Partilhar → Adicionar ao ecrã principal**.
3. Abre a app pelo ícone. A partir daí abre em ecrã inteiro e funciona sem rede.

Uma app instalada no ecrã principal tem armazenamento **separado** do Safari. Se a usares primeiro no Safari e depois a instalares, os dados não passam de um para o outro. Usa sempre o ícone.

No Android (Chrome) aparece a opção **Instalar app** no menu.

## Os dados

- Ficam guardados no próprio dispositivo (localStorage). Não há sincronização entre o telemóvel e o PC.
- Faz de vez em quando uma cópia em **Definições → Exportar cópia de segurança**. No iPhone abre a folha de partilha, onde podes guardar em Ficheiros, enviar por email, etc.
- Para passar os dados para outro dispositivo, usa **Importar cópia de segurança** com esse ficheiro.
- Apagar os dados do site no browser, ou remover a app do ecrã principal, apaga também os gastos.

## Publicar uma versão nova

1. Altera os ficheiros e carrega-os para o repositório.
2. Em `sw.js`, sobe o número em `VERSION` (por exemplo `plafond-v1.0.1`). Sem isto, os telemóveis podem continuar a mostrar a versão em cache.
3. A versão nova aparece ao reabrir a app uma ou duas vezes.

## Testar localmente

```bash
cd plafond-pwa
python3 -m http.server 8000
```

Depois abre `http://localhost:8000`. O service worker só funciona em `localhost` ou em HTTPS. Abrir o `index.html` com duplo clique não chega.
