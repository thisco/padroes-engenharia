Trecho redigido do serviço de publicação, no commit fixado no registro de verificação. Lido em 2026-11-03. Cliente do armazenamento, nomes de tabela e mensagens neutralizados; a lógica é a do original.

```python
def guardar_imutabilidade(sessao, armazenamento, chave, checksum):
    """A chave congelada jamais é sobrescrita."""
    if not armazenamento.existe(chave):
        return                                     # ausente: segue
    if sessao.contar_publicacoes(chave=chave):
        raise ObjetoJaPublicado(
            f"A chave {chave} já foi publicada e é imutável; "
            "correções entram como nova versão.")
    checksum_atual = armazenamento.sha256(chave)   # lido em blocos, sem carregar tudo
    if checksum_atual != checksum:
        raise ObjetoJaPublicado(
            f"A chave {chave} já existe com conteúdo divergente e sem registro "
            "de publicação; regenere o catálogo.")
    log.warning(f"Objeto órfão idêntico será regravado: chave={chave} checksum={checksum}")


def publicar(sessao, armazenamento, fornecedor, execucao_id, usuario):
    travar_fornecedor(sessao, fornecedor)          # seção crítica até o commit
    execucao = carregar_execucao(sessao, fornecedor, execucao_id)
    validar_versao(sessao, fornecedor, execucao.versao)   # próxima revisão livre do mês
    checksum, tamanho = medir(armazenamento, chave_de_trabalho(execucao))
    destino = chave_publicada(fornecedor, execucao.versao)
    guardar_imutabilidade(sessao, armazenamento, destino, checksum)
    armazenamento.copiar(chave_de_trabalho(execucao), destino)
    # Mesma transação: desmarca a vigente anterior e insere a nova
    # (o índice único parcial não deixa duas vigentes).
    ...
    # Depois do commit: regrava os manifestos a partir do banco e notifica
    # os integradores; falha de notificação não desfaz a publicação.
```
